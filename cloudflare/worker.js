/**
 * Study Forge Worker — orchestration only when Deepnote is configured.
 * Prefer: DEEPNOTE_ENGINE_URL + ENGINE_AUTH_TOKEN → full Python pipeline
 * Legacy fallback: in-worker LM Studio / Groq (until Deepnote is wired)
 */

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Engine-Token",
};

function json(data, status) {
  return new Response(JSON.stringify(data), {
    status: status || 200,
    headers: { "Content-Type": "application/json", ...CORS },
  });
}

async function forgeViaDeepnote(env, text, filename) {
  const base = (env.DEEPNOTE_ENGINE_URL || "").replace(/\/$/, "");
  const token = env.ENGINE_AUTH_TOKEN || "";
  if (!base) return null;

  const res = await fetch(base + "/forge", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Engine-Token": token,
    },
    body: JSON.stringify({ text: text.slice(0, 180000), filename: filename || "upload.txt" }),
  });
  const data = await res.json().catch(function () {
    return {};
  });
  if (!res.ok) {
    throw new Error("Deepnote HTTP " + res.status + ": " + (data.detail || data.error || res.statusText));
  }
  if (!data.ok) {
    throw new Error(data.error || "Deepnote forge failed");
  }
  const pack = data.pack || {};
  pack.host = "deepnote";
  pack.provider_used = data.provider_used || pack.provider_used || "deepnote";
  pack.processed_at = data.processed_at || pack.processed_at || new Date().toISOString();
  if (!pack.full_notes && pack.synthesized) pack.full_notes = pack.synthesized;
  if (!pack.study_notes && pack.synthesized) pack.study_notes = pack.synthesized;
  return pack;
}

async function chat(env, system, user) {
  const lmBase = (env.LMSTUDIO_BASE_URL || "").replace(/\/$/, "");
  const lmModel = env.LMSTUDIO_MODEL || "local-model";

  if (lmBase) {
    const url = lmBase.indexOf("/v1") >= 0 ? lmBase + "/chat/completions" : lmBase + "/v1/chat/completions";
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: lmModel,
        temperature: 0.3,
        max_tokens: 3200,
        messages: [
          { role: "system", content: system },
          { role: "user", content: user },
        ],
      }),
    });
    if (!res.ok) throw new Error("LM Studio " + res.status + ": " + (await res.text()).slice(0, 300));
    const data = await res.json();
    const text =
      (data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content) || "";
    if (!text.trim()) throw new Error("LM Studio empty response");
    return { text: text.trim(), provider: "lmstudio" };
  }

  if (env.GROQ_API_KEY) {
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
        max_tokens: 3200,
        messages: [
          { role: "system", content: system },
          { role: "user", content: user },
        ],
      }),
    });
    if (!res.ok) throw new Error("Groq " + res.status + ": " + (await res.text()).slice(0, 300));
    const data = await res.json();
    const text =
      (data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content) || "";
    if (!text.trim()) throw new Error("Groq empty response");
    return { text: text.trim(), provider: "groq" };
  }

  throw new Error("No engine: set DEEPNOTE_ENGINE_URL or GROQ_API_KEY");
}

function section(md, name) {
  const re = new RegExp("##\\s*" + name + "\\s*\\n([\\s\\S]*?)(?=\\n##\\s|$)", "i");
  const m = md.match(re);
  return m ? m[1].trim() : "";
}

function parseFlashcards(block) {
  const cards = [];
  if (!block) return cards;
  const lines = block.split("\n");
  let q = null;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    const qm = line.match(/^(?:Q\s*[:.)\-]|\d+[.)]\s*)(.+)/i);
    const am = line.match(/^A\s*[:.)\-]\s*(.+)/i);
    if (qm) {
      if (q) cards.push({ q: q, a: "" });
      q = qm[1].trim();
    } else if (am && q) {
      cards.push({ q: q, a: am[1].trim() });
      q = null;
    }
  }
  if (q) cards.push({ q: q, a: "" });
  return cards.slice(0, 12);
}

function parseQuiz(block) {
  const items = [];
  if (!block) return items;
  const chunks = block.split(/\n(?=\d+[.)]\s)/);
  for (let i = 0; i < chunks.length; i++) {
    const c = chunks[i].trim();
    if (!c) continue;
    const qm = c.match(/^\d+[.)]\s*(.+?)(?:\n|$)/);
    if (!qm) continue;
    const question = qm[1].trim();
    const opts = [];
    const optRe = /([A-D])[.)]\s*(.+)/gi;
    let om;
    while ((om = optRe.exec(c)) !== null) {
      opts.push({ key: om[1].toUpperCase(), text: om[2].trim() });
    }
    const hintM = c.match(/Hint\s*[:\-]\s*(.+)/i);
    const expM = c.match(/(?:Explain|Explanation|Why)\s*[:\-]\s*(.+)/i);
    const ansM = c.match(/(?:Answer|Correct)\s*[:\-]\s*([A-D])/i);
    items.push({
      question: question,
      options: opts,
      hint: hintM ? hintM[1].trim() : "",
      explanation: expM ? expM[1].trim() : "",
      answer: ansM ? ansM[1].toUpperCase() : opts[0] ? opts[0].key : "",
    });
  }
  return items.slice(0, 8);
}

async function processJobLegacy(env, text, filename) {
  const system =
    "You are Study Forge. Build a complete study pack.\n" +
    "Assistive learning only — not homework answer keys.\n" +
    "## Summary\n## Key Points\n## Definitions\n## Flashcards\n## Quiz\n## Study Notes\n";
  const out = await chat(env, system, text.slice(0, 14000));
  const md = out.text;
  return {
    source_file: filename,
    summary: section(md, "Summary"),
    key_points: section(md, "Key Points"),
    definitions: section(md, "Definitions"),
    flashcards: parseFlashcards(section(md, "Flashcards")),
    quiz: parseQuiz(section(md, "Quiz")),
    study_notes: section(md, "Study Notes") || md,
    full_notes: md,
    provider_used: out.provider,
    processed_at: new Date().toISOString(),
    host: "cloudflare-legacy",
    assistive: true,
  };
}

async function processJob(env, jobId) {
  const row = await env.DB.prepare("SELECT * FROM jobs WHERE id = ?").bind(jobId).first();
  if (!row) return;
  try {
    await env.DB.prepare("UPDATE jobs SET status = ?, updated_at = ?, error = NULL WHERE id = ?")
      .bind("forging", new Date().toISOString(), jobId)
      .run();

    const obj = await env.FILES.get(row.r2_key);
    if (!obj) throw new Error("File missing in R2");
    const text = new TextDecoder("utf-8").decode(new Uint8Array(await obj.arrayBuffer())).trim();
    if (text.length < 10) throw new Error("Text too short — use a text-based study file for now");

    let result;
    if (env.DEEPNOTE_ENGINE_URL) {
      result = await forgeViaDeepnote(env, text, row.filename);
    } else {
      result = await processJobLegacy(env, text, row.filename);
    }

    const resultKey = "results/" + jobId + ".json";
    await env.FILES.put(resultKey, JSON.stringify(result, null, 2), {
      httpMetadata: { contentType: "application/json" },
    });
    await env.DB.prepare(
      "UPDATE jobs SET status = ?, updated_at = ?, result_r2_key = ?, error = NULL WHERE id = ?"
    )
      .bind("forged", new Date().toISOString(), resultKey, jobId)
      .run();
  } catch (err) {
    const msg = String(err && err.message ? err.message : err).slice(0, 500);
    await env.DB.prepare("UPDATE jobs SET status = ?, updated_at = ?, error = ? WHERE id = ?")
      .bind("failed", new Date().toISOString(), msg, jobId)
      .run();
  }
}

async function handleApi(request, env, ctx) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS });
  }

  const path = new URL(request.url).pathname;
  if (!env.DB || !env.FILES) return json({ error: "DB or FILES binding missing" }, 503);

  if (path === "/api/health") {
    return json({
      ok: true,
      service: "study-forge",
      version: "0.8.0",
      host: "cloudflare",
      deepnote: Boolean(env.DEEPNOTE_ENGINE_URL),
      legacy_inference: Boolean(env.LMSTUDIO_BASE_URL || env.GROQ_API_KEY),
      free: true,
    });
  }

  if (path === "/api/jobs/clear-failed" && request.method === "POST") {
    const { results } = await env.DB.prepare(
      "SELECT id, r2_key, result_r2_key FROM jobs WHERE status = 'failed'"
    ).all();
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
    )
      .bind(id, filename, key, "queued", ts, ts)
      .run();
    if (ctx && ctx.waitUntil) ctx.waitUntil(processJob(env, id));
    else await processJob(env, id);
    return json({ id: id, filename: filename, status: "queued" }, 201);
  }

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
    try {
      const url = new URL(request.url);
      if (url.pathname.startsWith("/api/")) return await handleApi(request, env, ctx);
      if (env.ASSETS) return env.ASSETS.fetch(request);
      return new Response("Study Forge", { status: 200 });
    } catch (err) {
      return json({ error: String(err && err.message ? err.message : err) }, 500);
    }
  },
};
