/**
 * Study Forge Worker — studyforge.studio
 * Upload → R2 + D1 → Groq BYOK → notes on screen (Notion is manual)
 */

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

const GROQ_URL = "https://api.groq.com/openai/v1/chat/completions";
// Fast + widely available on Groq free tier
const DEFAULT_MODEL = "llama-3.1-8b-instant";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json", ...CORS },
  });
}

async function groqChat(env, system, user, maxTokens = 1500) {
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
    throw new Error(`Groq HTTP ${res.status}: ${t.slice(0, 400)}`);
  }
  const data = await res.json();
  const text = data.choices?.[0]?.message?.content?.trim() || "";
  if (!text) throw new Error("Groq returned empty content");
  return text;
}

async function extractText(filename, bytes) {
  const lower = (filename || "").toLowerCase();
  const dec = new TextDecoder("utf-8", { fatal: false });
  if (
    lower.endsWith(".txt") ||
    lower.endsWith(".md") ||
    lower.endsWith(".markdown") ||
    lower.endsWith(".csv")
  ) {
    return dec.decode(bytes).trim();
  }
  const asText = dec.decode(bytes).trim();
  if (asText.length > 80 && !asText.includes("\u0000")) return asText;
  throw new Error(
    "Cloud path supports .txt / .md for now. Convert PDF/DOCX to text first."
  );
}

/** One Groq call → structured study notes (fewer failures than 5 sequential calls) */
async function processJob(env, jobId) {
  const row = await env.DB.prepare("SELECT * FROM jobs WHERE id = ?").bind(jobId).first();
  if (!row) return;

  const now = () => new Date().toISOString();
  try {
    await env.DB.prepare("UPDATE jobs SET status = ?, updated_at = ?, error = NULL WHERE id = ?")
      .bind("forging", now(), jobId)
      .run();

    const obj = await env.FILES.get(row.r2_key);
    if (!obj) throw new Error("File missing in R2");
    const bytes = new Uint8Array(await obj.arrayBuffer());
    const text = await extractText(row.filename, bytes);
    if (!text || text.length < 10) throw new Error("Extracted text too short");

    const clip = text.slice(0, 14000);
    const notes = await groqChat(
      env,
      `You turn study material into clear notes for a student.
Return plain text with these exact section headers:
## Summary
## Key Points
## Definitions
## Flashcards
## Study Notes
Be concise. No preamble before ## Summary.`,
      clip,
      2500
    );

    // Light split for UI sections
    function section(name) {
      const re = new RegExp(
        `##\\s*${name}\\s*\\n([\\s\\S]*?)(?=\\n##\\s|$)`,
        "i"
      );
      const m = notes.match(re);
      return m ? m[1].trim() : "";
    }

    const result = {
      source_file: row.filename,
      summary: section("Summary") || notes,
      key_points: section("Key Points"),
      definitions: section("Definitions"),
      flashcards: section("Flashcards"),
      synthesized: section("Study Notes") || notes,
      full_notes: notes,
      provider_used: "groq",
      model: env.GROQ_MODEL || DEFAULT_MODEL,
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
      version: "0.4.0",
      host: "cloudflare",
      groq: Boolean(env.GROQ_API_KEY),
    });
  }

  // Clear all failed jobs (+ optional R2 cleanup best-effort)
  if (path === "/api/jobs/clear-failed" && request.method === "POST") {
    const { results } = await env.DB.prepare(
      "SELECT id, r2_key, result_r2_key FROM jobs WHERE status = 'failed'"
    ).all();
    for (const j of results || []) {
      try {
        if (j.r2_key) await env.FILES.delete(j.r2_key);
        if (j.result_r2_key) await env.FILES.delete(j.result_r2_key);
      } catch (_) {}
    }
    await env.DB.prepare("DELETE FROM jobs WHERE status = 'failed'").run();
    return json({ cleared: (results || []).length });
  }

  if (path === "/api/jobs" && request.method === "GET") {
    const { results } = await env.DB.prepare(
      `SELECT id, filename, status, created_at, updated_at, error, result_r2_key
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

    if (ctx && ctx.waitUntil) ctx.waitUntil(processJob(env, id));
    else await processJob(env, id);

    return json({ id, filename, status: "queued", r2_key: key }, 201);
  }

  // GET notes for a forged job
  if (path.match(/^\/api\/jobs\/[^/]+\/result$/) && request.method === "GET") {
    const id = path.split("/")[3];
    const row = await env.DB.prepare("SELECT * FROM jobs WHERE id = ?").bind(id).first();
    if (!row) return json({ error: "not found" }, 404);
    if (row.status !== "forged" || !row.result_r2_key) {
      return json({ error: "no notes yet", status: row.status, detail: row.error }, 404);
    }
    const obj = await env.FILES.get(row.result_r2_key);
    if (!obj) return json({ error: "result file missing" }, 404);
    const result = await obj.json();
    return json({ job: { id: row.id, filename: row.filename, status: row.status }, notes: result });
  }

  // Reprocess
  if (path.match(/^\/api\/jobs\/[^/]+\/process$/) && request.method === "POST") {
    const id = path.split("/")[3];
    if (ctx && ctx.waitUntil) ctx.waitUntil(processJob(env, id));
    else await processJob(env, id);
    return json({ id, status: "forging" });
  }

  // Delete one job
  if (path.match(/^\/api\/jobs\/[^/]+$/) && request.method === "DELETE") {
    const id = path.split("/")[3];
    const row = await env.DB.prepare("SELECT * FROM jobs WHERE id = ?").bind(id).first();
    if (!row) return json({ error: "not found" }, 404);
    try {
      if (row.r2_key) await env.FILES.delete(row.r2_key);
      if (row.result_r2_key) await env.FILES.delete(row.result_r2_key);
    } catch (_) {}
    await env.DB.prepare("DELETE FROM jobs WHERE id = ?").bind(id).run();
    return json({ deleted: id });
  }

  if (path.match(/^\/api\/jobs\/[^/]+$/) && request.method === "GET") {
    const id = path.split("/")[3];
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
