# 🔨 Study Forge

> A local-first personal study-material processing tool. Transform lecture PDFs, PowerPoints, and Word docs into structured, color-coded notes for your Notion workspace.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

---

## 📌 What Is Study Forge?

Study Forge is a **local-first** tool that processes your personal study materials. You drop files into a folder, and it extracts text, analyzes the content, and generates organized study notes.

**It is not:**
- A SaaS product or platform
- A startup or commercial venture
- A replacement for studying, professors, or textbooks

**It is:**
- A tool for individual students to process their own materials
- Local-first by design, with optional cloud fallback
- Free and open-source software

---

## 🎯 Why Does It Exist?

Students often spend hours re-reading lecture slides, manually creating flashcards, and organizing notes. Study Forge automates the extraction and organization so you can focus on understanding, not formatting.

**It helps with:**
- Summarizing lecture content
- Extracting key points
- Generating flashcards for review
- Identifying and defining key terms
- Color-coding information by type (MRI protocols, anatomy, physics, safety, etc.)

---

## 🧠 Planned Architecture

*Note: This is the design being implemented. See the Implementation Status section below for what's currently available.*

```

📄 Your File (PDF, DOCX, PPT)
↓
📖 Text Extraction
↓
┌────┼────┬────┐
↓         ↓         ↓         ↓
📝Summarizer  📌Key Points  🃏Flashcards  📖Definitions
↓         ↓         ↓         ↓
└────┴────┴────┘
↓
⚖️ Judge (Compare, Filter, Reconcile, Synthesize)
↓
🎨 Color Coder (Semantic Classification)
↓
📤 Notion (Organized + Color-Coded)

```

### What Each Agent Does

| Agent | Job |
|-------|-----|
| **Summarizer** | Creates a concise summary of the lecture |
| **Key Points** | Extracts the 5-8 most important takeaways |
| **Flashcards** | Generates Q&A pairs for active recall |
| **Definitions** | Identifies and explains key terms |
| **Color Coder** | Classifies content by type (protocols, anatomy, physics, safety, etc.) |
| **Judge** | Compares, filters, reconciles, and synthesizes outputs from specialized agents into a coherent final result |

### Why Multiple Agents?

Each agent has a **distinct, focused job**. Specialization helps keep individual tasks focused rather than having one model do everything.

The **Judge/Synthesis** agent isn't just another generator — it compares, filters, reconciles, and synthesizes outputs from the specialized agents to produce a coherent final result.

---

## 🎨 Semantic Color System

Colors represent **information classifications**, not UI decoration:

| Color | Hex | Category |
|-------|-----|----------|
| ⚫ Black | `#000000` | Main Topics / Headers |
| 🔵 Blue | `#0000FF` | Standard Notes |
| 🩵 Light Blue | `#ADD8E6` | Scanning Protocols / Positioning |
| 🔷 Navy | `#000080` | Anatomical Structures / Pathologies |
| 🟣 Purple | `#800080` | Physics / Math / Formulas |
| 🩷 Pink | `#FF69B4` | Clinical Red Flags / Contraindications / Safety |
| 🟢 Green | `#008000` | Professor Tips / Clinical Application |
| 🔴 Red | `#FF0000` | Corrections / Professor Emphasis |

This preserves meaning when material is transferred into your study workflow.

---

## 🛠️ Local-First Architecture

```

Local-First
│
├── Local model available?
│       └── Yes → process locally (no API key required)
│
└── No / failure / insufficient capability
└── Optional cloud fallback
│
└── User's own API credentials

```

**Local processing is the preferred/default path.** Cloud fallback exists for situations where local inference is unavailable, insufficient, or fails.

**Privacy note:** Local inference does not require sending study material to a cloud AI provider.

---

## 🛠️ AI Provider Options (Local-First, BYOK)

Study Forge supports multiple AI providers. **You choose which ones to use, and you supply your own credentials for cloud options.**

### Local Providers (Run on Your Computer)

| Provider | Description | Credentials Required? |
|----------|-------------|----------------------|
| **Ollama** | Local inference engine | No — runs locally, no API key needed |
| **Fox** | Faster local inference, continuous batching | No — runs locally, no API key needed |
| **Mullama** | In-process inference, embeddings | No — runs locally, no API key needed |

**Local providers require no API keys, no internet connection for inference, and no third-party data sharing.**

### Cloud Providers (Optional Fallback — BYOK)

| Provider | Type | Credentials Required? |
|----------|------|----------------------|
| **Groq** | Cloud | Yes — user provides API key |
| **Cloudflare AI** | Cloud | Yes — user provides API key |
| **Google Gemini** | Cloud | Yes — user provides API key |
| **Hugging Face** | Cloud | Yes — user provides API key |

**Cloud providers are optional fallbacks only.** Study Forge does not provide API keys. Users are responsible for their own provider usage, quotas, and potential costs.

### 🔄 Fallback Chain

Your script tries providers in order — if one fails, it automatically falls back:

1. 🔧 Local (Ollama/Fox/Mullama) → if successful, done
2. ☁️ Groq → if successful, done
3. ☁️ Cloudflare AI → if successful, done
4. ☁️ Google Gemini → if successful, done
5. ☁️ Hugging Face → if successful, done
6. ❌ Log error, move to next file

### How to Choose

- **Privacy-first?** Use local providers (Ollama, Fox, or Mullama) — no data leaves your computer, no API keys needed
- **Speed-first?** Try a local provider first, then optionally add Groq as a fast cloud fallback
- **Reliability-first?** Use multiple providers with fallback chain
- **Offline?** Use local providers only (Ollama, Fox, or Mullama)

---

## 💰 Cost & Licensing

Study Forge is **free/open-source software** (AGPL-3.0).

- **Local operation:** Can run without paid API services
- **Optional cloud fallbacks:** Require users to provide their own provider credentials and may incur provider charges
- Provider pricing and free-tier availability are **provider-dependent** — not guaranteed by Study Forge

---

## 📥 Supported Inputs

| Format | Status |
|--------|--------|
| PDF | 🔮 Planned |
| DOCX | 🔮 Planned |
| PPTX | 🔮 Planned |
| TXT / MD | 🔮 Planned |
| Images (OCR) | 🔮 Planned |
| Audio / Video | 🔮 Planned |

## 📤 Outputs

| Output | Status |
|--------|--------|
| Notion Database | 🔮 Planned |
| Summaries | 🔮 Planned |
| Key Points | 🔮 Planned |
| Flashcards | 🔮 Planned |
| Definitions | 🔮 Planned |
| Color-Coded Notes | 🔮 Planned |

---

## 🚀 Installation & Setup

**Prerequisites:**
- Python 3.11+
- A local AI provider (Ollama, Fox, or Mullama) — or a cloud provider if you prefer
- Notion account with API/integration access, if using Notion output

### Step 1: Clone the Repository

```bash
git clone https://github.com/AStrasler/study-forge.git
cd study-forge
```

Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Step 3: Configure

Copy the example environment file and fill in your settings:

```bash
cp .env.example .env
```

Edit .env with your:

· Notion API token (you create this in Notion)
· Notion database ID
· Upload folder path
· Your chosen AI provider(s) and any required API keys

Step 4: Run

```bash
python main.py
```

---

🔧 Configuration

Users configure:

· Local model / runtime (Ollama, Fox, or Mullama)
· Optional cloud providers (via their own API keys)
· Their own API credentials
· Output settings

Never commit .env files or real credentials.

---

🔐 Security

· API keys are user-provided
· Never commit .env files or credentials
· Cloud providers are optional
· Users should review provider privacy/data policies before enabling cloud fallback
· Study Forge does not provide or collect users' API credentials

---

📊 Implementation Status

Component Status
Planning & Documentation ✅ Implemented
README.md ✅ Implemented
LICENSE ✅ Implemented
.gitignore ✅ Implemented
Python Script (main.py) 🚧 In Development
requirements.txt 🚧 In Development
.env.example 🚧 In Development
File Processing (PDF/DOCX/PPTX) 🔮 Planned
Multi-Agent Pipeline 🔮 Planned
Notion Integration 🔮 Planned
Color Coding System 🔮 Planned
Obsidian Sync 🔮 Planned

---

🛠️ Troubleshooting

Common issues and solutions:

· "python: command not found" — Try python3 instead, or reinstall Python with "Add to PATH" checked
· "No module named 'xxx'" — Run pip install -r requirements.txt again
· "Can't find Ollama" — Run ollama serve in a separate terminal (or check your chosen provider's docs)
· "Notion API error" — Check your token starts with secret_, verify database ID, ensure integration is added

---

🤝 Contributing

This project is open source under the AGPL-3.0 license. Contributions are welcome! Please open an issue or pull request.

---

📄 License

GNU Affero General Public License v3.0 — see LICENSE for the full text.

Key points of AGPL-3.0:

· You may copy, distribute, and modify the software
· If you distribute or make the software available over a network, you must provide source code to users
· Modifications must also be released under AGPL-3.0
· The software is provided "AS IS" with no warranty

---

🙏 Acknowledgments

· Ollama — Local AI inference
· Fox — Fast local inference
· Groq — Fast cloud inference (optional)
· Notion — API for organizing notes
· GitHub Education — Supporting student developers