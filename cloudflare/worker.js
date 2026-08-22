/**
 * Study Forge Worker — primary route for studyforge.studio
 * - /api/* → R2 upload + D1 job rows
 * - everything else → static UI (web/)
 */

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json", ...CORS },
  });
}

async function handleApi(request, env) {
  const url = new URL(request.url);
  const path = url.pathname;

  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS });
  }

  if (!env.DB || !env.FILES) {
    return json(
      {
        error:
          "R2/D1 not bound. Create bucket studyforge + D1 studyforge-db, bind as FILES and DB, redeploy.",
      },
      503
    );
  }

  if (path === "/api/health" && request.method === "GET") {
    return json({ ok: true, service: "study-forge", version: "0.2.0", host: "cloudflare" });
  }

  if (path === "/api/jobs" && request.method === "GET") {
    const { results } = await env.DB.prepare(
      `SELECT id, filename, status, created_at, updated_at, notion_pushed, error
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
    await env.FILES.put(key, file.stream(), {
      httpMetadata: { contentType: file.type || "application/octet-stream" },
    });
    const now = new Date().toISOString();
    await env.DB.prepare(
      `INSERT INTO jobs (id, filename, r2_key, status, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?)`
    )
      .bind(id, filename, key, "queued", now, now)
      .run();
    return json({ id, filename, status: "queued", r2_key: key }, 201);
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
  async fetch(request, env) {
    const url = new URL(request.url);
    try {
      if (url.pathname.startsWith("/api/")) {
        return await handleApi(request, env);
      }
      if (env.ASSETS) {
        return env.ASSETS.fetch(request);
      }
      return new Response("Study Forge UI not bound (ASSETS).", { status: 404 });
    } catch (err) {
      return json({ error: String(err && err.message ? err.message : err) }, 500);
    }
  },
};
