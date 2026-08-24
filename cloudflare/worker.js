/**
 * Study Forge Worker
 * /api/* → D1 + R2 + optional Groq
 * else → static UI
 */

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

function json(data, status) {
  return new Response(JSON.stringify(data), {
    status: status || 200,
    headers: { "Content-Type": "application/json", ...CORS },
  });
}

async function groqChat(env, system, user) {
  if (!env.GROQ_API_KEY) throw new Error("GROQ_API_KEY not set (wrangler secret put GROQ_API_KEY)");
  const model = env.GROQ_MODEL || "llama-3.1-8b-instant";
  const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: "Bearer " + env.GROQ_API_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: model,
      temperature: 0.3,
      max_tokens: 2500,
      messages: [
        { role: "system", content: system },
        { role: "user", content: user },
      ],
    }),
  });
  if (!res.ok) {
    const t = await res.text();
    throw new Error("Groq " + res.status + ": " + t.slice(0, 300));
  }
  const data = await res.json();
  const text = (data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content) || "";
  if (!text.trim()) throw new Error("Groq empty response");
  return text.trim();
}

async function processJob(env, jobId) {
  const row = await env.DB.prepare("SELECT * FROM jobs WHERE id = ?").bind(jobId).first();
  if (!row) return;
  const now = new Date().toISOString();
  try {
    await env.DB.prepare("UPDATE jobs SET status = ?, updated_at = ?, error = NULL WHERE id = ?")
      .bind("forging", now, jobId).run();

    const obj = await env.FILES.get(row.r2_key);
    if (!obj) throw new Error("File missing in R2");
    const bytes = new Uint8Array(await obj.arrayBuffer());
    const text = new TextDecoder("utf-8").decode(bytes).trim();
    if (text.length < 10) throw new Error("Text too short — use a .txt study file");

    const notes = await groqChat(
      env,
      "Turn study material into clear student notes. Use headers: ## Summary, ## Key Points, ## Definitions, ## Flashcards, ## Study Notes. No preamble.",
      text.slice(0, 14000)
    );

    const result = {
      source_file: row.filename,
      full_notes: notes,
      provider_used: "groq",
      processed_at: new Date().toISOString(),
      host: "cloudflare",
    };
    const resultKey = "results/" + jobId + ".json";
    await env.FILES.put(resultKey, JSON.stringify(result, null, 2), {
      httpMetadata: { contentType: "application/json" },
    });
    await env.DB.prepare(
      "UPDATE jobs SET status = ?, updated_at = ?, result_r2_key = ?, error = NULL WHERE id = ?"
    ).bind("forged", new Date().toISOString(), resultKey, jobId).run();
  } catch (err) {
    const msg = String(err && err.message ? err.message : err).slice(0, 500);
    await env.DB.prepare("UPDATE jobs SET status = ?, updated_at = ?, error = ? WHERE id = ?")
      .bind("failed", new Date().toISOString(), msg, jobId).run();
  }
}

async function handleApi(request, env, ctx) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS });
  }

  const url = new URL(request.url);
  const path = url.pathname;

  if (!env.DB || !env.FILES) {
    return json({ error: "DB or FILES binding missing" }, 503);
  }

  if (path === "/api/health") {
    return json({
      ok: true,
      service: "study-forge",
      version: "0.5.0",
      host: "cloudflare",
      groq: Boolean(env.GROQ_API_KEY),
    });
  }

  if (path === "/api/jobs/clear-failed" && request.method === "POST") {
    const { results } = await env.DB.prepare("SELECT id, r2_key, result_r2_key FROM jobs WHERE status = 'failed'").all();
    for (const j of results || []) {
      try {
        if (j.r2_key) await env.FILES.delete(j.r2_key);
        if (j.result_r2_key) await env.FILES.delete(j.result_r2_key);
      } catch (e) {}
    }
    await env.DB.prepare("DELETE FROM jobs WHERE status = 'failed'").run();
    return json({ cleared: (results || []).length });
  }

  if (path === "/api/jobs" && request.method === "GET") {
    const { results } = await env.DB.prepare(
      "SELECT id, filename, status, created_at, updated_at, error, result_r2_key FROM jobs ORDER BY created_at DESC LIMIT 50"
    ).all();
    return json({ jobs: results || [] });
  }

  if (path === "/api/jobs" && request.method === "POST") {
    const form = await request.formData();
    const file = form.get("file");
    if (!file || typeof file === "string") return json({ error: "file required" }, 400);
    const filename = file.name || "upload.txt";
    const id = crypto.randomUUID();
    const key = "uploads/" + id + "/" + filename;
    await env.FILES.put(key, await file.arrayBuffer(), {
      httpMetadata: { contentType: file.type || "text/plain" },
    });
    const ts = new Date().toISOString();
    await env.DB.prepare(
      "INSERT INTO jobs (id, filename, r2_key, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)"
    ).bind(id, filename, key, "queued", ts, ts).run();

    if (ctx && ctx.waitUntil) ctx.waitUntil(processJob(env, id));
    else await processJob(env, id);

    return json({ id: id, filename: filename, status: "queued" }, 201);
  }

  // /api/jobs/:id/result
  const resultMatch = path.match(/^\/api\/jobs\/([^/]+)\/result$/);
  if (resultMatch && request.method === "GET") {
    const id = resultMatch[1];
    const row = await env.DB.prepare("SELECT * FROM jobs WHERE id = ?").bind(id).first();
    if (!row) return json({ error: "not found" }, 404);
    if (row.status !== "forged" || !row.result_r2_key) {
      return json({ error: "no notes yet", status: row.status, detail: row.error }, 404);
    }
    const obj = await env.FILES.get(row.result_r2_key);
    if (!obj) return json({ error: "result missing" }, 404);
    return json({ job: { id: row.id, filename: row.filename }, notes: await obj.json() });
  }

  // DELETE /api/jobs/:id
  const delMatch = path.match(/^\/api\/jobs\/([^/]+)$/);
  if (delMatch && request.method === "DELETE") {
    const id = delMatch[1];
    const row = await env.DB.prepare("SELECT * FROM jobs WHERE id = ?").bind(id).first();
    if (!row) return json({ error: "not found" }, 404);
    try {
      if (row.r2_key) await env.FILES.delete(row.r2_key);
      if (row.result_r2_key) await env.FILES.delete(row.result_r2_key);
    } catch (e) {}
    await env.DB.prepare("DELETE FROM jobs WHERE id = ?").bind(id).run();
    return json({ deleted: id });
  }

  return json({ error: "not found", path: path }, 404);
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    try {
      if (url.pathname.startsWith("/api/")) {
        return await handleApi(request, env, ctx);
      }
      if (env.ASSETS) {
        return env.ASSETS.fetch(request);
      }
      return new Response("Study Forge", { status: 200 });
    } catch (err) {
      return json({ error: String(err && err.message ? err.message : err) }, 500);
    }
  },
};
