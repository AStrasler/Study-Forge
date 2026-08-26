/**
 * Study Forge Worker
 * 1) LM Studio (LMSTUDIO_BASE_URL)  2) Groq (GROQ_API_KEY)
 * Produces a full study pack: summary, points, definitions, cards, assistive quiz
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
    const text = (data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content) || "";
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
    const text = (data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content) || "";
    if (!text.trim()) throw new Error("Groq empty response");
    return { text: text.trim(), provider: "groq" };
  }

  throw new Error("No LLM configured. Set LMSTUDIO_BASE_URL or GROQ_API_KEY.");
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
    } else if (q && line && !am) {
      // continuation of answer or question
    }
  }
  if (q) cards.push({ q: q, a: "" });
  if (!cards.length && block.length > 20) {
    cards.push({ q: "Review this section", a: block.slice(0, 500) });
  }
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
      answer: ansM ? ansM[1].toUpperCase() : (opts[0] ? opts[0].key : ""),
    });
  }
  return items.slice(0, 8);
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
    if (text.length < 10) throw new Error("Text too short — use a .txt study file");

    const system =
      "You are Study Forge. Build a complete study pack for a student from their material.\n" +
      "Be accurate and assistive: help them learn, do not write answers meant for submitting as homework.\n" +
      "Use EXACTLY these markdown headers in order:\n" +
      "## Summary\n## Key Points\n## Definitions\n## Flashcards\n## Quiz\n## Study Notes\n\n" +
      "Flashcards format each as:\nQ: ...\nA: ...\n\n" +
      "Quiz: 4-6 multiple choice. For each:\n" +
      "1. Question text\nA) ...\nB) ...\nC) ...\nD) ...\nHint: one helpful nudge (not the full answer)\nAnswer: A\nExplanation: why that option is correct (teach the concept)\n\n" +
      "No preamble before ## Summary.";

    const out = await chat(env, system, text.slice(0, 14000));
    const md = out.text;

    const summary = section(md, "Summary");
    const key_points = section(md, "Key Points");
    const definitions = section(md, "Definitions");
    const flashBlock = section(md, "Flashcards");
    const quizBlock = section(md, "Quiz");
    const study_notes = section(md, "Study Notes") || md;

    const result = {
      source_file: row.filename,
      summary: summary,
      key_points: key_points,
      definitions: definitions,
      flashcards: parseFlashcards(flashBlock),
      quiz: parseQuiz(quizBlock),
      study_notes: study_notes,
      full_notes: md,
      provider_used: out.provider,
      processed_at: new Date().toISOString(),
      host: "cloudflare",
      assistive: true,
    };

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
      version: "0.7.0",
      host: "cloudflare",
      lmstudio: Boolean(env.LMSTUDIO_BASE_URL),
      groq: Boolean(env.GROQ_API_KEY),
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
