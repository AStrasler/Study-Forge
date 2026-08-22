# Study Forge on Cloudflare

**UI (Pages) + API (Worker) + files (R2) + job rows (D1).**

AI stays private-first (Ollama/Fox/Mullama) or BYOK. This Worker does not run the agent pipeline by default.

## Your tasks

1. `npm i -g wrangler` then `wrangler login`
2. Create R2 bucket named `studyforge`
3. `wrangler d1 create studyforge-db` — put `database_id` in `cloudflare/wrangler.toml`
4. `wrangler d1 execute studyforge-db --file=./cloudflare/schema.sql`
5. `cd cloudflare && wrangler deploy`
6. Cloudflare Pages: deploy folder `web/`, attach domain `studyforge.studio`

## Local CLI (unchanged)

```bash
python main.py
```
