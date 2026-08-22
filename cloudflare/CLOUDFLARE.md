# Study Forge on Cloudflare (primary web route)

**Browser → studyforge.studio (Pages UI) → Worker API → R2 (files) + D1 (job rows).**

AI stays **private-first** (Ollama / Fox / Mullama on infrastructure you control) or **BYOK** cloud. This Worker does **not** run the multi-agent pipeline by default.

## Your tasks (simple order)

1. Install Node if needed, then: `npm i -g wrangler`
2. `wrangler login` (browser opens Cloudflare)
3. Create R2 bucket named `studyforge` (Dashboard → R2 → Create bucket)
4. `wrangler d1 create studyforge-db` — copy `database_id` into `cloudflare/wrangler.toml`
5. `wrangler d1 execute studyforge-db --file=./cloudflare/schema.sql`
6. `cd cloudflare` → `wrangler deploy`
7. Pages: create project, upload/connect `web/`, custom domain `studyforge.studio`
8. After Worker URL exists, in browser console on the site:
   `localStorage.setItem('sf_api_base', 'https://YOUR-WORKER.workers.dev')`

## Local CLI (still works offline)

```bash
python main.py
```
