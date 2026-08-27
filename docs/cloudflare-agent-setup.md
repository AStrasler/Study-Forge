# Cloudflare agent setup (Study Forge)

Official source: https://developers.cloudflare.com/agent-setup/prompt.md

## What was added in this repo

- `.vscode/mcp.json` — GitHub Copilot / VS Code MCP servers
- `.cursor/mcp.json` — Cursor MCP servers

Servers:

- https://mcp.cloudflare.com/mcp
- https://docs.mcp.cloudflare.com/mcp (public, no auth)
- https://bindings.mcp.cloudflare.com/mcp
- https://builds.mcp.cloudflare.com/mcp
- https://observability.mcp.cloudflare.com/mcp

OAuth runs on first use of a Cloudflare MCP tool (except docs).

## On your machine (skills)

```powershell
cd C:\Users\aaron_cufgo0v\OneDrive\Documents\GitHub\Study-Forge
git pull origin main
npx -y skills add cloudflare/skills --skill "*" --yes
```

## Cursor / VS Code

1. `git pull origin main`
2. Restart Cursor or VS Code
3. Accept MCP / OAuth when prompted for Cloudflare

## Claude Code (if you use it)

```text
claude plugin marketplace add cloudflare/skills
claude plugin install cloudflare@cloudflare
```

Then run `/reload-plugins` inside Claude Code.

## Note for this Grok chat

Grok does not load Cursor/Claude MCP plugins inside this chat. MCP config is for your **local** editors. Deploy and secrets stay:

```powershell
cd cloudflare
wrangler secret put LMSTUDIO_BASE_URL
wrangler secret put GROQ_API_KEY
wrangler deploy
```
