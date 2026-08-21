# 🔨 Study Forge

> A local-first, private-inference-first study-material processing tool. Transform lecture PDFs, PowerPoints, Word documents, and other study materials into structured, color-coded study notes and send them to your Notion workspace.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

---

## 📌 What Is Study Forge?

Study Forge is a personal/student-focused study-material processing system.

Its purpose is to take study materials, extract their content, run that content through specialized AI agents, synthesize the results, semantically classify the information, and produce structured study output.

The project is designed around:

* Private/local inference as the preferred processing path
* Multiple local AI provider options
* Optional BYOK cloud fallback
* Modular AI agents
* Structured output
* Notion integration
* A $0-first development philosophy
* No required Study Forge subscription

Study Forge is free/open-source software under AGPL-3.0.

It is intentionally **not designed as a conventional SaaS product**.

---

# 🧭 Current Project State

Study Forge has moved beyond the initial repository scaffolding.

The current repository contains a functioning implementation foundation including:

* Project/package structure
* Centralized configuration
* Provider abstraction
* Ollama provider
* Groq provider
* Provider fallback manager
* PDF extraction
* DOCX extraction
* PPTX extraction
* TXT/Markdown extraction
* Specialized AI agents
* Judge/Synthesis agent
* Semantic Color Coder
* Sequential file processing
* Local result persistence
* Notion output integration
* Error handling and logging
* `.env.example`
* Requirements and licensing

The core architecture is now established.

The immediate goal is **verification, completion of missing providers, and a reliable end-to-end vertical slice**, not architectural reinvention.

---

# 🏗️ Architecture

The current processing architecture is:

```text
📄 Study Material
       ↓
📖 Text Extraction
       ↓
┌──────┼────────┬──────────┐
↓      ↓        ↓          ↓
📝     📌       🃏         📖
Summary Key     Flashcards Definitions
       ↓
       └────────┬─────────┘
                ↓
        ⚖️ Judge / Synthesis
                ↓
        🎨 Color Coder
                ↓
        💾 Local Result
                ↓
        📤 Optional Notion
```

The local result is preserved independently of Notion.

If Notion fails, generated study material should remain available locally.

---

# 🤖 Agent Architecture

Study Forge intentionally uses specialized agents rather than one giant prompt.

| Agent                 | Responsibility                                                     |
| --------------------- | ------------------------------------------------------------------ |
| **Summarizer**        | Creates a concise lecture summary                                  |
| **Key Points**        | Extracts approximately 5–8 important takeaways                     |
| **Flashcards**        | Generates Q&A pairs for active recall                              |
| **Definitions**       | Identifies and explains important terminology                      |
| **Judge / Synthesis** | Compares, filters, reconciles, and synthesizes specialized outputs |
| **Color Coder**       | Semantically classifies the synthesized material                   |

The Judge is an evaluation/synthesis stage, not simply another independent generator.

The Color Coder is a separate processing stage following synthesis.

---

# 🎨 Semantic Color System

Colors represent functional information classifications rather than UI decoration.

| Color         | Hex       | Category                                        |
| ------------- | --------- | ----------------------------------------------- |
| ⚫ Black       | `#000000` | Main Topics / Headers                           |
| 🔵 Blue       | `#0000FF` | Standard Notes                                  |
| 🩵 Light Blue | `#ADD8E6` | Scanning Protocols / Positioning                |
| 🔷 Navy       | `#000080` | Anatomical Structures / Pathologies             |
| 🟣 Purple     | `#800080` | Physics / Math / Formulas                       |
| 🩷 Pink       | `#FF69B4` | Clinical Red Flags / Contraindications / Safety |
| 🟢 Green      | `#008000` | Professor Tips / Clinical Application           |
| 🔴 Red        | `#FF0000` | Corrections / Professor Emphasis                |

These values are project-level semantic anchors and should not be arbitrarily replaced.

When output is sent to systems such as Notion that do not support arbitrary hexadecimal colors, Study Forge maps the project colors to the closest supported representation while preserving the original semantic classification.

---

# 🧠 Private / Local Inference Architecture

Private inference is the preferred processing path.

The intended hierarchy is:

```text
                    STUDY FORGE
                         │
                         ▼
                Private Inference
                         │
             ┌───────────┼───────────┐
             ↓           ↓           ↓
          Ollama        Fox        Mullama
             │           │           │
             └───────────┼───────────┘
                         │
                         │ failure / unavailable
                         ⋮
                         ⋮
                         └───────────────┐
                                         ↓
                              Optional Cloud Fallback
```

The important distinction is:

**Private/local inference is the primary path.**

Cloud providers are the fallback path.

A successful private provider should prevent unnecessary cloud processing.

If multiple private providers are configured, the system should exhaust the configured private-provider options before moving to cloud fallback.

---

# 🔌 AI Provider Architecture

Study Forge uses a provider abstraction so the core application is not permanently tied to one AI runtime.

## Private / Local Providers

The intended local provider options are:

| Provider    | Role                              | Current Status         |
| ----------- | --------------------------------- | ---------------------- |
| **Ollama**  | Local inference runtime           | ✅ Implemented          |
| **Fox**     | Local inference option            | 🔮 Not yet implemented |
| **Mullama** | Local/in-process inference option | 🔮 Not yet implemented |

Ollama, Fox, and Mullama are intentional architectural choices.

Fox and Mullama should be implemented through the existing provider abstraction rather than being removed or treated as irrelevant.

Do not collapse the local-provider architecture into Ollama-only.

---

## ☁️ Optional Cloud Providers — BYOK

Cloud processing is optional.

Users provide their own credentials.

| Provider          | Role           | Current Status                                           |
| ----------------- | -------------- | -------------------------------------------------------- |
| **Groq**          | Cloud fallback | ✅ Implemented                                            |
| **Cloudflare AI** | Cloud fallback | 🚧 Configuration exists; provider implementation pending |
| **Google Gemini** | Cloud fallback | 🚧 Configuration exists; provider implementation pending |
| **Hugging Face**  | Cloud fallback | 🚧 Configuration exists; provider implementation pending |

Study Forge does not provide API keys.

Users are responsible for their own provider accounts, credentials, quotas, and provider-side costs.

---

# 🔄 Fallback Model

The fallback system should follow this conceptual hierarchy:

```text
Preferred Private Provider
        ↓ failure/unavailable
Next Configured Private Provider
        ↓ failure/unavailable
Next Configured Private Provider
        ↓ failure/unavailable
        ⋮
        ↓
Optional Cloud Fallback
        ↓
Groq
        ↓
Cloudflare AI
        ↓
Google Gemini
        ↓
Hugging Face
        ↓
Log failure
```

The exact order should remain configurable.

A provider failure means an actual execution failure such as:

* unavailable runtime
* connection failure
* timeout
* exception
* invalid/malformed provider response
* missing required configuration

Do not treat subjective output quality as a provider failure.

---

# 🔐 BYOK

BYOK means **Bring Your Own Key**.

Study Forge does not provide or centrally manage users' cloud API credentials.

Never:

* hard-code API keys
* commit real credentials
* place real credentials in documentation
* print credentials in logs
* create a centralized Study Forge API-key service

Credentials belong in the user's environment/configuration.

---

# 💰 $0-First Philosophy

Study Forge is developed with a **$0-first** constraint.

The project prioritizes:

1. Local/private inference
2. Free/open-source software
3. Free provider tiers where available
4. User-owned infrastructure
5. BYOK cloud services when necessary

Study Forge itself should not require a paid subscription.

Provider pricing and free-tier limits are controlled by the individual providers and may change.

---

# 🌐 Future Web / Deployment Architecture

Study Forge is being designed so that the processing engine is not permanently tied to the user's personal computer.

A future deployment may provide a web dashboard at:

`studyforge.studio`

The intended concept is:

```text
                    studyforge.studio
                           │
                           ▼
                    Web Dashboard
                           │
                           ▼
                   Study Forge Core
                           │
                           ▼
                 Private Inference
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
           Ollama         Fox        Mullama
                           │
                           ⋮
                           ⋮ optional fallback
                           └───────────────▶
                                      BYOK Cloud
```

This would allow the Study Forge engine and private inference runtime to operate on server-side infrastructure rather than requiring the user's PC or laptop to carry the inference workload.

**This deployment model is not yet implemented.**

The current codebase should therefore remain deployment-agnostic and avoid hard-coding assumptions that inference must always run on `localhost`.

Do not introduce SaaS infrastructure, user accounts, billing, subscriptions, or multi-tenant systems merely to prepare for this future deployment.

---

# 📥 Supported Inputs

| Format        | Status        |
| ------------- | ------------- |
| PDF           | ✅ Implemented |
| DOCX          | ✅ Implemented |
| PPTX          | ✅ Implemented |
| TXT           | ✅ Implemented |
| MD / Markdown | ✅ Implemented |
| Images / OCR  | 🔮 Planned    |
| Audio / Video | 🔮 Planned    |

Future formats should be added through the ingestion layer rather than by expanding `main.py`.

---

# 📤 Outputs

| Output                  | Status        |
| ----------------------- | ------------- |
| Local JSON results      | ✅ Implemented |
| Local Markdown results  | ✅ Implemented |
| Summaries               | ✅ Implemented |
| Key Points              | ✅ Implemented |
| Flashcards              | ✅ Implemented |
| Definitions             | ✅ Implemented |
| Judge/Synthesized Notes | ✅ Implemented |
| Color-Coded Segments    | ✅ Implemented |
| Notion                  | ✅ Implemented |
| Obsidian                | 🔮 Future     |

---

# 📁 Repository Structure

The current project separates major responsibilities:

```text
Study-Forge/
│
├── agents/
│   ├── summarizer.py
│   ├── key_points.py
│   ├── flashcards.py
│   ├── definitions.py
│   ├── judge.py
│   └── color_coder.py
│
├── config/
│   └── settings.py
│
├── ingestion/
│   └── extractors.py
│
├── input/
│
├── output/
│   └── notion.py
│
├── pipeline/
│   └── processor.py
│
├── providers/
│   ├── base.py
│   ├── manager.py
│   ├── ollama.py
│   └── groq.py
│
├── results/
│
├── utils/
│
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── main.py
└── requirements.txt
```

`main.py` is intentionally an entry point/orchestrator rather than the location for application business logic.

---

# 📊 Implementation Status

## ✅ Implemented

* Repository/package structure
* Centralized configuration
* Environment-based configuration
* Provider abstraction
* Provider manager
* Ollama provider
* Groq provider
* PDF extraction
* DOCX extraction
* PPTX extraction
* TXT/Markdown extraction
* Sequential batch processing
* Specialized agents
* Judge/Synthesis
* Semantic Color Coder
* Local JSON result persistence
* Local Markdown result persistence
* Notion output
* Notion batching
* Error handling/logging
* `.env.example`
* AGPL-3.0 licensing

## 🚧 Current Development / Verification

* Complete local provider layer
* Fox provider
* Mullama provider
* Multi-local-provider fallback
* Cloudflare AI provider
* Gemini provider
* Hugging Face provider
* Full provider fallback verification
* End-to-end testing
* Provider failure testing
* Notion integration verification
* Output validation
* Configuration validation

## 🔮 Future

* Images / OCR
* Audio / Video ingestion
* Obsidian output
* Web dashboard
* Server-hosted Study Forge engine
* Remote/private inference deployment
* Additional deployment options

---

# 🎯 Immediate Development Priorities

The next implementation work should proceed in this order:

### 1. Complete the Private Provider Layer

Verify Ollama and implement:

* Fox
* Mullama

The provider abstraction already exists.

Do not redesign it unless a concrete technical limitation requires doing so.

### 2. Complete Local Fallback

Verify that:

```text
Ollama fails
    ↓
Fox
    ↓
Mullama
```

works before cloud fallback begins.

### 3. Complete Cloud Fallback Providers

Implement and verify:

* Groq
* Cloudflare AI
* Gemini
* Hugging Face

Cloud remains optional.

### 4. Verify the Core Pipeline

Test:

```text
Input
 ↓
Extraction
 ↓
Summarizer
 ↓
Key Points
 ↓
Flashcards
 ↓
Definitions
 ↓
Judge
 ↓
Color Coder
 ↓
Local Result
 ↓
Notion
```

### 5. Verify Failure Boundaries

Test that:

* one provider failure does not destroy the pipeline
* local failures trigger the next configured local provider
* cloud fallback does not occur while a configured local provider can still process successfully
* a failed cloud provider moves to the next cloud provider
* malformed input does not stop the entire batch
* Notion failure does not destroy the generated local result
* secrets never appear in logs

### 6. End-to-End Vertical Slice

The first major completion milestone is:

> **One real study document successfully processed from ingestion through AI agents, Judge, Color Coder, local result persistence, and Notion, with verified private-provider fallback and optional cloud fallback.**

---

# 🧪 Testing Expectations

Testing should demonstrate actual behavior rather than assuming functionality works.

Minimum verification includes:

* [ ] Ollama responds
* [ ] Fox responds
* [ ] Mullama responds
* [ ] Private-provider fallback works
* [ ] Groq responds
* [ ] Cloudflare AI responds
* [ ] Gemini responds
* [ ] Hugging Face responds
* [ ] Cloud fallback works
* [ ] PDF extraction works
* [ ] DOCX extraction works
* [ ] PPTX extraction works
* [ ] TXT/MD extraction works
* [ ] Summarizer works
* [ ] Key Points works
* [ ] Flashcards works
* [ ] Definitions works
* [ ] Judge works
* [ ] Color Coder works
* [ ] Local result persistence works
* [ ] Notion authentication works
* [ ] Notion output works
* [ ] End-to-end processing works
* [ ] One failed input does not stop the batch
* [ ] Notion failure preserves local output
* [ ] Secrets are not exposed in logs

---

# ⚙️ Configuration

Configuration is centralized through `.env`.

Example variables include:

```text
LOCAL_PROVIDER=
LOCAL_MODEL=

OLLAMA_BASE_URL=

PROVIDER_FALLBACK_ORDER=

GROQ_API_KEY=
GROQ_MODEL=

CLOUDFLARE_API_TOKEN=
CLOUDFLARE_ACCOUNT_ID=

GEMINI_API_KEY=

HUGGINGFACE_API_KEY=

NOTION_API_TOKEN=
NOTION_DATABASE_ID=

INPUT_FOLDER=
OUTPUT_FOLDER=

PROVIDER_TIMEOUT=
LOG_LEVEL=
```

The exact variables should remain consistent with the implementation.

Never commit `.env` or real credentials.

---

# 🚀 Current Development Principle

Study Forge is a personal/student project.

The priority is:

**Working > useful > reliable > polished**

Do not introduce unnecessary complexity merely because it is common in commercial SaaS applications.

Avoid:

* user accounts
* subscriptions
* billing
* unnecessary databases
* unnecessary microservices
* telemetry
* analytics
* centralized API-key collection
* unnecessary cloud infrastructure

The architecture should remain modular and extensible without becoming bloated.

---

# 📜 Licensing

Study Forge intentionally uses **AGPL-3.0**.

Do not change the license.

The possibility of dual licensing is a future consideration, but no commercial licensing system is currently implemented.

See `LICENSE` for the complete license text.

---

# 🙏 Acknowledgments

Study Forge uses and/or is designed to integrate with open-source and third-party projects including:

* Ollama — Local AI inference
* Fox — Local inference
* Mullama — Local/in-process inference
* Groq — Cloud inference
* Cloudflare — Cloud AI infrastructure
* Google Gemini — Cloud AI
* Hugging Face — AI infrastructure/models
* Notion — Study-output integration
* GitHub Education — Student developer resources

These projects and services remain independently owned by their respective organizations and contributors.

---

# 🔨 Project Goal

Study Forge exists to make the boring part of studying easier:

**Give it the material.
Let the pipeline do the organizing.
Keep the student in control.**

The architecture should remain private-first, provider-agnostic, $0-first, modular, and practical.
