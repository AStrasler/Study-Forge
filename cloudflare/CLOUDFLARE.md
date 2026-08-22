# Wire upload (R2 + D1)

## Your tasks

### 1. Create R2 bucket
Dashboard → **R2 Object Storage** → **Create bucket** → name: `studyforge`

### 2. Create D1 database
```bash
npm i -g wrangler
wrangler login
wrangler d1 create studyforge-db
```
Copy the printed `database_id` into `cloudflare/wrangler.toml` (replace `REPLACE_AFTER_CREATE`).

### 3. Apply schema
```bash
wrangler d1 execute studyforge-db --remote --file=./cloudflare/schema.sql
```

### 4. Deploy Worker (from repo root or cloudflare/)
```bash
cd cloudflare
wrangler deploy
```

### 5. Test
1. Open https://studyforge.studio (pass Cloudflare Access if prompted)
2. Enter the forge
3. Upload a small .txt or .pdf
4. Queue should show the file as **queued**

Upload stores the file in R2 and a row in D1. AI processing still runs via local `python main.py` until wired later.
