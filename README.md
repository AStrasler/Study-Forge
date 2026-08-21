# 🔨 Study Forge

> A local-first, private-inference-first study-material processing system. Transform lecture PDFs, PowerPoints, Word documents, and other study materials into structured, color-coded study notes and send them to your Notion workspace.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

---

## 📌 What Is Study Forge?

Study Forge is a personal/student-focused study-material processing system.

Its purpose is to:

1. Accept study materials.
2. Extract their content.
3. Process that content through specialized AI agents.
4. Judge and synthesize the resulting outputs.
5. Semantically classify the information.
6. Preserve the generated study material.
7. Optionally send the result to Notion.

Study Forge is designed around:

- Private/local inference as the preferred AI-processing path
- Multiple private inference provider options
- Optional BYOK cloud fallback
- Modular AI agents
- Structured study output
- Notion integration
- A $0-first philosophy
- User-controlled infrastructure
- No required Study Forge subscription
- No centralized collection of user study material or API keys

Study Forge is free/open-source software under **AGPL-3.0**.

It is intentionally **not designed as a conventional SaaS platform**.

---

# 🧭 Core Architectural Principle

## Local-first does not mean laptop-only.

Study Forge is **local-first at the inference and privacy level**.

The preferred AI-processing path is private inference using:

- Ollama
- Fox
- Mullama

Cloud AI providers are optional BYOK fallbacks.

The Study Forge engine itself is deployment-agnostic.

It can run:

- Locally on a personal computer
- On a home server
- On a VPS
- On other infrastructure controlled by the user
- Behind a secure tunnel
- As the backend for a web dashboard

The current direction is moving toward a **web-hosted personal instance** so the user does not have to run the entire inference stack directly on their laptop or desktop.

The important distinction is:

> **Private inference is the preferred processing path. The physical machine running that inference can change.**

---

# 🌐 Web Deployment Direction

Study Forge is being developed toward a web-accessible personal instance at:

`studyforge.studio`

The intended architecture is:

```text
                     Browser
                        │
                        ▼
              studyforge.studio
                        │
                        ▼
              Secure Access Layer
                        │
                        ▼
              Study Forge Dashboard
                        │
                        ▼
               Study Forge API/Core
                        │
                        ▼
              ┌───────────────────┐
              │ Private Inference │
              └───────────────────┘
                   │     │     │
                   ▼     ▼     ▼
                Ollama  Fox  Mullama
                   │
                   │
                   ⋮
                   ⋮  optional fallback
                   ⋮
                   └ - - - - - - - - - - - - - - - - ▶
                                      Cloud AI
                                         │
                              ┌──────────┼──────────┐
                              ▼          ▼          ▼
                            Groq     Cloudflare   Gemini
                                         │
                                         ▼
                                   Hugging Face


The dashed relationship represents the optional cloud fallback path.

A successful private inference provider should prevent unnecessary cloud processing.

The web dashboard does not change the local-first architecture.

Instead, it provides a browser-based interface to a Study Forge instance running on infrastructure controlled by the owner.

The goal

Keep the engine private-first while removing the requirement that the user's personal computer carry the inference workload.

This means the user can access their Study Forge instance from a browser without requiring Ollama or another inference runtime to consume resources on their everyday laptop.

🔐 Privacy Model

Study Forge is designed around user-controlled processing.

When private inference is available:

Study Material
      ↓
Study Forge
      ↓
Private Inference
      ↓
Generated Study Material

The study material does not need to be sent to a third-party AI provider.

Cloud AI is only used when:

The user has configured a cloud provider.
The provider is enabled.
The configured private inference path has failed or is otherwise unavailable according to the fallback configuration.

Notion is an explicit output destination and therefore requires user configuration.

Study Forge does not intentionally add:

Telemetry
Analytics
Advertising
Centralized document collection
Centralized AI API-key storage
Unnecessary tracking
🎯 Intended Workflow
📄 Study Material
        ↓
📖 Text Extraction
        ↓
┌───────┼──────────┬────────────┐
↓       ↓          ↓            ↓
📝      📌         🃏           📖
Summary Key Points Flashcards Definitions
        ↓
        └──────────┬────────────┘
                   ↓
            ⚖️ Judge / Synthesis
                   ↓
             🎨 Color Coder
                   ↓
          💾 Local/Instance Result
                   ↓
          📤 Optional Notion

The generated result should be preserved independently of Notion.

If Notion is unavailable, the generated study material should remain available.

🤖 Multi-Agent Architecture

Study Forge intentionally uses specialized agents rather than one giant prompt.

Agent	Responsibility
Summarizer	Creates a concise lecture summary
Key Points	Extracts approximately 5–8 important takeaways
Flashcards	Generates Q&A pairs for active recall
Definitions	Identifies and explains important terminology
Judge / Synthesis	Compares, filters, reconciles, and synthesizes agent outputs
Color Coder	Semantically classifies the synthesized material
Judge

The Judge is not simply another independent generator.

It receives the specialized agent outputs and:

Compares them
Identifies weak or redundant information
Reconciles conflicts
Produces the synthesized result

The Judge may use the configured provider system, but it must remain a distinct processing stage with its own role and prompt.

Color Coder

The Color Coder is a separate stage after synthesis.

It receives the Judge's output and applies the semantic color classifications defined by Study Forge.

🎨 Semantic Color System

Colors represent functional information classifications, not UI decoration.

These values are project-level semantic anchors and should not be arbitrarily replaced.

Color	Hex	Category
⚫ Black	#000000	Main Topics / Headers
🔵 Blue	#0000FF	Standard Notes
🩵 Light Blue	#ADD8E6	Scanning Protocols / Positioning
🔷 Navy	#000080	Anatomical Structures / Pathologies
🟣 Purple	#800080	Physics / Math / Formulas
🩷 Pink	#FF69B4	Clinical Red Flags / Contraindications / Safety
🟢 Green	#008000	Professor Tips / Clinical Application
🔴 Red	#FF0000	Corrections / Professor Emphasis

Classification should be contextual and semantic rather than relying solely on simplistic keyword matching where practical.

When an output destination cannot represent arbitrary hexadecimal colors, Study Forge may map the semantic classification to the closest supported representation while preserving the underlying classification.
🧠 Private Inference Architecture

Private inference is the preferred AI-processing path.

The intended private provider layer is:

              Study Forge
                   │
                   ▼
          Private Provider Layer
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
     Ollama       Fox       Mullama

These are intentional architectural choices.

Ollama

Local inference runtime and the initial private-provider implementation.

Fox

Intentional alternative private inference provider.

Mullama

Intentional alternative private/in-process inference provider.

Fox and Mullama are not obsolete or optional ideas to be removed simply because Ollama is implemented first.

They are part of the intended provider architecture.

The implementation should close the current Fox/Mullama gap through the existing provider abstraction rather than redesigning the application around Ollama alone.

🔌 Provider Abstraction

Study Forge uses a provider abstraction so the core pipeline is not permanently tied to a single AI runtime.

A provider should expose a consistent interface capable of supporting operations such as:

generate(...)
is_available(...)
name(...)

The exact implementation may evolve as required by the actual provider APIs.

The core application should not need to know provider-specific implementation details.

The provider layer should allow:

Providers to be enabled or disabled
Providers to be reordered
Providers to be replaced
Providers to be tested independently
Private providers to be exhausted before cloud fallback

Do not hard-code the application around one provider.

☁️ Optional Cloud Providers — BYOK

Cloud AI is an optional fallback, not the primary architecture.

The intended cloud providers are:

Provider	Role	Status
Groq	Cloud fallback	✅ Implemented
Cloudflare AI	Cloud fallback	🚧 Pending completion
Google Gemini	Cloud fallback	🚧 Pending completion
Hugging Face	Cloud fallback	🚧 Pending completion

Cloud providers use BYOK.

Study Forge does not provide API keys.

Users are responsible for:

Their provider accounts
Their API credentials
Provider quotas
Provider-side limits
Provider-side costs

Provider free tiers and pricing may change and should be verified against current provider documentation.

🔄 Fallback Architecture

The fallback chain is intentionally modular.

Conceptually:

Private Provider
      ↓
failure / unavailable
      ↓
Next configured Private Provider
      ↓
failure / unavailable
      ↓
Next configured Private Provider
      ↓
failure / unavailable
      ↓
- - - - - - - - - - - - - - - - -
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

The exact order should be configurable.

Provider Failure

A provider is considered failed when there is an actual execution/configuration problem, such as:

Provider unavailable
Connection failure
Timeout
Runtime exception
Invalid provider response
Malformed expected response
Missing required configuration

A subjective judgment that an AI response is "not good enough" is not automatically a provider failure.

Provider quality evaluation is a separate concern.

🔐 BYOK Security

BYOK means:

Bring Your Own Key

Study Forge does not centrally collect or manage users' cloud credentials.

Never:

Hard-code API keys
Commit real credentials
Put real credentials in README.md
Put real credentials in source code
Print credentials in logs
Create a centralized Study Forge API-key service

Use environment variables or secure deployment configuration.

.env must remain excluded from version control.

.env.example contains placeholders only.

💰 $0-First Philosophy

Study Forge is developed under a $0-first constraint.

Priority is:

Private/local inference
Free and open-source tooling
Free provider tiers where available
User-controlled infrastructure
BYOK cloud providers when needed

Study Forge itself should not require:

A paid subscription
A Study Forge account
A Study Forge-hosted API
A Study Forge billing system

Users may independently choose paid infrastructure or provider plans if they want them.

📥 Supported Inputs
Format	Status
PDF	✅ Implemented
DOCX	✅ Implemented
PPTX	✅ Implemented
TXT	✅ Implemented
Markdown	✅ Implemented
Images / OCR	🔮 Planned
Audio / Video	🔮 Planned

Future formats should be implemented through the ingestion layer.

They should not require expanding main.py into format-specific logic.

📤 Outputs
Output	Status
Local JSON results	✅ Implemented
Local Markdown results	✅ Implemented
Summary	✅ Implemented
Key Points	✅ Implemented
Flashcards	✅ Implemented
Definitions	✅ Implemented
Judge/Synthesized Notes	✅ Implemented
Color-Coded Content	✅ Implemented
Notion	✅ Implemented
Obsidian	🔮 Future

Notion is currently the primary external output.

Obsidian is intentionally a future output target rather than a first-version requirement.

📁 Repository Structure

The project separates major responsibilities:

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
│   ├── groq.py
│   ├── fox.py
│   └── mullama.py
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

The exact filenames may evolve with implementation.

The architectural separation should not.

main.py should remain an entry point/orchestrator rather than becoming a monolithic application file.

📊 Current Implementation Status
✅ Implemented
Repository/package structure
Centralized configuration
Environment-based configuration
Provider abstraction
Provider manager
Ollama provider
Groq provider
PDF extraction
DOCX extraction
PPTX extraction
TXT/Markdown extraction
Sequential file processing
Specialized agents
Judge/Synthesis
Semantic Color Coder
Local result persistence
Markdown result generation
JSON result generation
Notion output
Error handling/logging
.env.example
AGPL-3.0 licensing
🚧 Current Development / Verification
Fox provider
Mullama provider
Multi-private-provider fallback
Cloudflare AI provider
Google Gemini provider
Hugging Face provider
Complete provider fallback verification
End-to-end verification
Failure-path testing
Configuration validation
Notion integration verification
Output validation
Web/API layer
🔮 Future
Web dashboard
Browser-based upload workflow
Secure remote access
Server-hosted Study Forge engine
Server-hosted private inference
Images / OCR
Audio / Video ingestion
Obsidian output
Additional deployment options
🎯 Immediate Development Priorities

The next development work should proceed in this order.

1. Complete the Private Provider Layer

Verify the existing Ollama implementation.

Then implement:

Fox
Mullama

Do not remove either provider from the architecture simply because implementation begins with Ollama.

2. Complete Private Provider Fallback

Verify that the system can move between configured private providers.

Example:

Ollama
   ↓ failure
Fox
   ↓ failure
Mullama
   ↓ failure
Optional Cloud Fallback

Private providers should be exhausted before cloud fallback begins.

3. Complete Cloud Providers

Implement and verify:

Groq
Cloudflare AI
Google Gemini
Hugging Face

Cloud remains optional.

4. Verify the Core Pipeline

Test:

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
Local/Instance Result
 ↓
Notion
5. Verify Failure Boundaries

Test that:

One provider failure does not destroy the pipeline.
Private-provider failures trigger the next configured private provider.
Cloud fallback does not occur while an available private provider can process successfully.
A failed cloud provider moves to the next configured cloud provider.
A malformed input does not stop the entire batch.
Notion failure does not destroy generated local/instance output.
Missing credentials produce useful errors.
Secrets never appear in logs.
🌐 Web/API Direction

The web interface is being developed as a presentation and control layer over the Study Forge engine.

The browser should communicate with the Study Forge backend through an API.

Conceptually:

Browser
   │
   ▼
Study Forge Web/API
   │
   ├── Upload
   ├── Queue
   ├── Processing Status
   ├── Provider Status
   ├── Results
   └── Settings
   │
   ▼
Study Forge Core
   │
   ▼
Provider Layer
   │
   ▼
Private / Optional Cloud AI

The core processing pipeline should remain independent from the web interface.

This is important because the same Study Forge engine should remain capable of running:

Locally
On a server
Behind a tunnel
As the backend of the web dashboard

The web layer should not require rewriting the core pipeline.

🔒 Web Access Model

The planned personal web instance is intended to be protected by a secure access layer such as Cloudflare Zero Trust.

The project is not introducing a public signup system.

The intended model is:

Authorized User
      ↓
Secure Access
      ↓
Personal Study Forge Instance

This is a personal/user-controlled deployment model.

It is not intended to become:

Public Signup
      ↓
Multi-Tenant SaaS
      ↓
Study Forge Managed Accounts
      ↓
Study Forge Billing

Those systems are explicitly outside the current project scope.

🧪 Testing Expectations

Testing should demonstrate actual behavior rather than assuming functionality works.

Minimum verification includes:

 Ollama responds
 Fox responds
 Mullama responds
 Private-provider fallback works
 Groq responds
 Cloudflare AI responds
 Gemini responds
 Hugging Face responds
 Cloud fallback works
 PDF extraction works
 DOCX extraction works
 PPTX extraction works
 TXT/MD extraction works
 Summarizer works
 Key Points works
 Flashcards works
 Definitions works
 Judge works
 Color Coder works
 Local/instance result persistence works
 Notion authentication works
 Notion output works
 End-to-end processing works
 Failed input does not stop the batch
 Notion failure preserves generated output
 Secrets are not exposed in logs
 Web/API upload works
 Web/API processing status works
 Web/API result retrieval works
 Private inference works through the deployed instance
⚙️ Configuration

Configuration is centralized.

Example configuration categories include:

LOCAL_PROVIDER=
LOCAL_MODEL=


OLLAMA_BASE_URL=


PROVIDER_FALLBACK_ORDER=


GROQ_API_KEY=
GROQ_MODEL=


CLOUDFLARE_API_TOKEN=
CLOUDFLARE_ACCOUNT_ID=


GEMINI_API_KEY=
GEMINI_MODEL=


HUGGINGFACE_API_KEY=
HUGGINGFACE_MODEL=


NOTION_API_TOKEN=
NOTION_DATABASE_ID=


INPUT_FOLDER=
OUTPUT_FOLDER=


PROVIDER_TIMEOUT=
LOG_LEVEL=

The exact variables should remain consistent with the implementation.

Never commit:

.env

or real credentials.

🛡️ Error Handling

Study Forge should fail gracefully.

Examples:

Provider unavailable
Provider unavailable
        ↓
Log useful error
        ↓
Try next configured provider
Malformed document
Bad document
    ↓
Log error
    ↓
Skip document
    ↓
Continue processing remaining files
Notion failure
Generated study material
        ↓
Notion unavailable
        ↓
Preserve local/instance result
        ↓
Report Notion error

Errors must not be silently swallowed.

Logs should contain enough information to diagnose failures without exposing credentials or sensitive secrets.

📜 Licensing

Study Forge is licensed under:

GNU Affero General Public License v3.0 (AGPL-3.0)

The AGPL-3.0 license is intentional.

Do not replace it with:

MIT
Apache-2.0
BSD
Another permissive license

Do not add dependencies with incompatible licensing without identifying the issue first.

Future dual licensing is a possible consideration, but it is not part of the current implementation.

AGPL-3.0 is the current licensing Reality Anchor.

See LICENSE for the complete license text.

🚫 Scope Boundaries

Study Forge is intentionally not building:

User subscription systems
Billing
Public SaaS accounts
Multi-tenant enterprise infrastructure
Centralized API-key management
Telemetry
Analytics
Advertising
Unnecessary microservices
Unnecessary databases
Enterprise identity infrastructure
A centralized Study Forge AI service

The goal is a powerful personal/student study-processing system, not an enterprise SaaS platform.

🗺️ Development Philosophy

The priority is:

Working → Useful → Reliable → Polished

Not:

Overengineered → Expensive → Complicated

Build the smallest system that correctly implements the architecture.

When a feature is not required for the core pipeline, classify it as Phase 2 rather than allowing it to block the first working version.

🚀 First Major Completion Milestone

The first major milestone is a verified end-to-end vertical slice:

Real Study Document
        ↓
Text Extraction
        ↓
Private AI Provider
        ↓
Specialized Agents
        ↓
Judge / Synthesis
        ↓
Semantic Color Coder
        ↓
Generated Study Result
        ↓
Notion

with verified failure behavior:

Private Provider
       ↓ failure
Next Private Provider
       ↓ failure
Optional BYOK Cloud Provider
       ↓ failure
Next Cloud Provider

The system should work before optional polish or future integrations are prioritized.

🔨 Project Direction

Study Forge is evolving from a primarily local execution model toward a web-accessible, user-controlled deployment model.

The architectural hierarchy remains:

                USER-CONTROLLED INSTANCE
                         │
                         ▼
                 Study Forge Core
                         │
                         ▼
                PRIVATE INFERENCE
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           Ollama       Fox       Mullama
                         │
                         ⋮
                         ⋮
                         └ - - - - - - - - - - - - ▶
                              OPTIONAL BYOK CLOUD

The browser is simply a new interface to the system.

The privacy model, provider hierarchy, multi-agent pipeline, semantic color system, Notion output, AGPL license, and $0-first philosophy remain intact.

Same engine. Same pipeline. Same provider architecture.
Different deployment surface.

🙏 Acknowledgments

Study Forge is built using and alongside open-source software and AI tooling.

Credit belongs to the projects, maintainers, and communities whose work makes this project possible.

🔨 Final Principle

Your instance. Your infrastructure. Your keys. Your data.

Study Forge should remain private-first, modular, free/open-source, and useful to students without requiring them to buy into a SaaS platform.
