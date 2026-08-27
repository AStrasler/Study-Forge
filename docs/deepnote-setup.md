# Study Forge on Deepnote (your BYOS engine)

Cloudflare = browser UI + Access + R2/D1  
Deepnote = Python processing server (this guide)

Official incoming connections: https://deepnote.com/docs/incoming-connections  
Scheduling: https://deepnote.com/docs/scheduling

---

## After your shower — do this in order

### 1. Create the project

1. Open https://deepnote.com and sign in.
2. **Create project** → name it `Study Forge Engine`.
3. Stay in that project for all steps below.

### 2. Turn on Incoming connections

1. Open **project settings** (gear) for this project.
2. Find **Incoming connections**.
3. **Enable** it.
4. Copy the public URL Deepnote shows  
   (looks like `https://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.deepnoteproject.com`).
5. Save it in a notes app — you will need it for the Worker later.

Only **port 8080** is exposed. Our engine binds to `0.0.0.0:8080`.

### 3. Add environment variables (your secrets)

In the workspace/project **Environment variables** (or Integrations → Environment variables), add what you use:

| Name | Example / notes |
|------|------------------|
| `LMSTUDIO_BASE_URL` | Your Cloudflare tunnel URL, no trailing slash |
| `LMSTUDIO_MODEL` | Model id as shown in LM Studio (optional) |
| `GROQ_API_KEY` | Optional fallback |
| `ENGINE_AUTH_TOKEN` | Long random string; Worker will send it as `X-Engine-Token` |

Connect those env vars **to this project**.

### 4. Get the Study Forge code into Deepnote

**Option A — Terminal in Deepnote**

```bash
cd /work
git clone https://github.com/AStrasler/Study-Forge.git
cd Study-Forge
pip install -r requirements.txt
pip install -r deepnote/requirements-engine.txt
```

**Option B — Upload** the repo ZIP via Deepnote Files, then `pip install` as above.

### 5. Start the engine

In a Deepnote **terminal** (machine must be running):

```bash
cd /work/Study-Forge
python deepnote/engine_api.py
```

Leave this running.

### 6. Test from your laptop browser

```text
https://YOUR-ID.deepnoteproject.com/health
```

You want JSON with `"ok": true`.

Optional forge test (PowerShell):

```powershell
Invoke-RestMethod -Method POST `
  -Uri "https://YOUR-ID.deepnoteproject.com/forge" `
  -ContentType "application/json" `
  -Headers @{ "X-Engine-Token" = "YOUR_ENGINE_AUTH_TOKEN" } `
  -Body '{"text":"MRI safety notes. Pacemakers are contraindications. SAR limits tissue heating.","filename":"test.txt"}'
```

### 7. Schedule a warm-up (optional but useful)

1. Create a notebook in the project.
2. One code block:

```python
print("warmup ok")
```

Or run `deepnote/warmup.py`.

3. Click **Schedule notebook** (calendar icon).
4. Set times you usually study (your timezone), e.g. weekdays 5:30pm.
5. Save.

That **wakes the machine**. After idle it may sleep again — open the project or rely on the schedule before a long session.

### 8. Wire Cloudflare later

When health works:

```powershell
cd C:\Users\aaron_cufgo0v\OneDrive\Documents\GitHub\Study-Forge\cloudflare
wrangler secret put DEEPNOTE_ENGINE_URL
# paste https://YOUR-ID.deepnoteproject.com

wrangler secret put ENGINE_AUTH_TOKEN
# same value as Deepnote ENGINE_AUTH_TOKEN

wrangler deploy
```

Worker handoff to Deepnote can be enabled in a follow-up change once URL + token are set.

---

## Keep in mind

- This is **your** engine — not a public SaaS.
- Machine sleeps when idle; schedule + opening the project keeps it ready.
- LM Studio still needs your **tunnel** up if you use local models from Deepnote.
- Full multi-agent path uses repo `pipeline` when imports succeed; otherwise simple pack via LM Studio/Groq.

---

## Files in repo

| Path | Purpose |
|------|---------|
| `deepnote/engine_api.py` | FastAPI on port 8080 |
| `deepnote/warmup.py` | Schedule-friendly wake script |
| `deepnote/requirements-engine.txt` | fastapi + uvicorn |
| `docs/deepnote-setup.md` | This guide |
