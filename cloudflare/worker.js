/**
 * Study Forge Worker — studyforge.studio
 * Upload → R2 + D1 → Groq BYOK processing on Cloudflare (not your laptop)
 * Private Ollama remains optional elsewhere; this path is cloud-hosted.
 */

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

const GROQ_URL = "https://api.groq.com/openai/v1/chat/completions";
const DEFAULT_MODEL = "openai/gpt-oss-20b";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json", ...CORS },
  });
}

async function groqChat(env, system, user, maxTokens = 1200) {
  const key = env.GROQ_API_KEY;
  if (!key) throw new Error("GROQ_API_KEY secret not set on Worker");
  const model = env.GROQ_MODEL || DEFAULT_MODEL;
  const res = await fetch(GROQ_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${key}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      temperature: 0.3,
      max_tokens: maxTokens,
      messages: [
        { role: "system", content: system },
        { role: "user", content: user },
      ],
    }),
  });
  if (!res.ok) {
    const t = await res.text();
    throw new Error(`Groq HTTP ${res.status}: ${t.slice(0, 300)}`);
  }
  const data = await res.json();
  const text = data.choices?.[0]?.message?.content?.trim() || "";
  if (!text) throw new Error("Groq returned empty content");
  return text;
}

async function extractText(filename, bytes) {
  const lower = (filename || "").toLowerCase();
  const dec = new TextDecoder("utf-8", { fatal: false });
  if (lower.endsWith(".txt") || lower.endsWith(".md") || lower.endsWith(".markdown") || lower.endsWith(".csv")) {
    return dec.decode(bytes).trim();
  }
  // Best-effort for other types (PDF/DOCX need dedicated parsers later)
  const asText = dec.decode(bytes).trim();
  if (asText.length > 80 && !asText.includes("\u0000")) return asText;
  throw new Error(
    "Cloud processing currently supports .txt / .md. Convert PDF/DOCX to text or use a future parser."
  );
}

async function processJob(env, jobId) {
  const row = await env.DB.prepare("SELECT * FROM jobs WHERE id = ?").bind(jobId).first();
  if (!row) return;

  const now = () => new Date().toISOString();
  try {
    await env.DB.prepare("UPDATE jobs SET status = ?, updated_at = ? WHERE id = ?")
      .bind("forging", now(), jobId)
      .run();

    const obj = await env.FILES.get(row.r2_key);
    if (!obj) throw new Error("File missing in R2");
    const bytes = new Uint8Array(await obj.arrayBuffer());
    const text = await extractText(row.filename, bytes);
    if (!text || text.length < 10) throw new Error("Extracted text too short");

    const clip = text.slice(0, 12000);

    const summary = await groqChat(
      env,
      "You are a study summarizer. Write a concise lecture summary. No preamble.",
      clip
    );
    const keyPoints = await groqChat(
      env,
      "Extract 5–8 key study takeaways as a numbered list. No preamble.",
      clip
    );
    const flashcards = await groqChat(
      env,
      "Create 5–8 Q&A flashcards for active recall. Format: Q: ... A: ...",
      clip
    );
    const definitions = await groqChat(
      env,
      "List important terms and short definitions from the material.",
      clip
    );
    const synthesized = await groqChat(
      env,
      "You are the Judge. Merge the following into coherent study notes. Remove redundancy.",
      `SUMMARY:\n${summary}\n\nKEY POINTS:\n${keyPoints}\n\nDEFINITIONS:\n${definitions}\n\nFLASHCARDS:\n${flashcards}`
    );

    const result = {
      source_file: row.filename,
      summary,
      key_points: keyPoints,
      flashcards,
      definitions,
      synthesized,
      provider_used: "groq",
      processed_at: now(),
      host: "cloudflare",
    };

    const resultKey = `results/${jobId}.json`;
    await env.FILES.put(resultKey, JSON.stringify(result, null, 2), {
      httpMetadata: { contentType: "application/json" },
    });

    await env.DB.prepare(
      "UPDATE jobs SET status = ?, updated_at = ?, result_r2_key = ?, error = NULL WHERE id = ?"
    )
      .bind("forged", now(), resultKey, jobId)
      .run();
  } catch (err) {
    const msg = String(err && err.message ? err.message : err).slice(0, 500);
    await env.DB.prepare("UPDATE jobs SET status = ?, updated_at = ?, error = ? WHERE id = ?")
      .bind("failed", now(), msg, jobId)
      .run();
  }
}

async function handleApi(request, env, ctx) {
  const url = new URL(request.url);
  const path = url.pathname;

  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS });
  }

  if (!env.DB || !env.FILES) {
    return json({ error: "R2/D1 not bound" }, 503);
  }

  if (path === "/api/health" && request.method === "GET") {
    return json({
      ok: true,
      service: "study-forge",
      version: "0.3.0",
      host: "cloudflare",
      groq: Boolean(env.GROQ_API_KEY),
    });
  }

  if (path === "/api/jobs" && request.method === "GET") {
    const { results } = await env.DB.prepare(
      `SELECT id, filename, status, created_at, updated_at, notion_pushed, error, result_r2_key
       FROM jobs ORDER BY created_at DESC LIMIT 50`
    ).all();
    return json({ jobs: results || [] });
  }

  if (path === "/api/jobs" && request.method === "POST") {
    const form = await request.formData();
    const file = form.get("file");
    if (!file || typeof file === "string") {
      return json({ error: "file required" }, 400);
    }
    const filename = file.name || "upload.bin";
    const id = crypto.randomUUID();
    const key = `uploads/${id}/${filename}`;
    const buf = await file.arrayBuffer();
    await env.FILES.put(key, buf, {
      httpMetadata: { contentType: file.type || "application/octet-stream" },
    });
    const ts = new Date().toISOString();
    await env.DB.prepare(
      `INSERT INTO jobs (id, filename, r2_key, status, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?)`
    )
      .bind(id, filename, key, "queued", ts, ts)
      .run();

    // Process on Cloudflare (not the user's laptop)
    if (ctx && ctx.waitUntil) {
      ctx.waitUntil(processJob(env, id));
    } else {
      await processJob(env, id);
    }

    return json({ id, filename, status: "queued", r2_key: key }, 201);
  }

  // Force reprocess
  if (path.startsWith("/api/jobs/") && path.endsWith("/process") && request.method === "POST") {
    const id = path.split("/")[3];
    if (ctx && ctx.waitUntil) ctx.waitUntil(processJob(env, id));
    else await processJob(env, id);
    return json({ id, status: "forging" });
  }

  if (path.startsWith("/api/jobs/") && request.method === "GET") {
    const id = path.split("/").pop();
    const row = await env.DB.prepare("SELECT * FROM jobs WHERE id = ?").bind(id).first();
    if (!row) return json({ error: "not found" }, 404);
    return json({ job: row });
  }

  return json({ error: "not found" }, 404);
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    try {
      if (url.pathname.startsWith("/api/")) {
        return await handleApi(request, env, ctx);
      }
      if (env.ASSETS) return env.ASSETS.fetch(request);
      return new Response("UI not bound", { status: 404 });
    } catch (err) {
      return json({ error: String(err && err.message ? err.message : err) }, 500);
    }
  },
};
