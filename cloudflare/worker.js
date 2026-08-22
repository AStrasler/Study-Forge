/**
 * Study Forge API Worker (primary web route on Cloudflare)
 * R2: FILES | D1: DB
 * AI stays private-first or BYOK; this Worker handles upload + job metadata.
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

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    try {
      if (path === "/api/health" && request.method === "GET") {
        return json({ ok: true, service: "study-forge", version: "0.1.0", host: "cloudflare" });
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
    } catch (err) {
      return json({ error: String(err && err.message ? err.message : err) }, 500);
    }
  },
};
