# 🔨 Study Forge

> A private-first study-material processing platform with a web dashboard, modular AI providers, multi-agent study processing, semantic color classification, and structured study output.



License: AGPL-3.0
Deployment model: BYOS (Bring Your Own Server)
Cloud AI model: BYOK (Bring Your Own Key)


---

What Is Study Forge?

Study Forge transforms course materials into structured study resources.

The system is designed around:

A browser-based dashboard

Server-side processing

Private-first AI inference

Modular AI providers

Optional cloud AI fallback

Multi-agent study processing

Judge/Synthesis

Semantic color classification

Notion output

User-controlled infrastructure


Study Forge is intended primarily for students and individual users.

It is free and open source under the AGPL-3.0 license.

It is not a subscription SaaS product.


---

Architecture

Study Forge separates the user interface from the processing infrastructure.

┌──────────────────────┐
                    │       Browser        │
                    │   Study Forge UI     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Web Dashboard      │
                    │      Cloudflare      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Study Forge API    │
                    └──────────┬───────────┘
                               │
                               ▼
                 ┌────────────────────────────┐
                 │       BYOS Server          │
                 │                            │
                 │    Study Forge Engine      │
                 │                            │
                 │  Ingestion → Agents →      │
                 │  Judge → Color Coder       │
                 └──────────────┬─────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ Private Inference    │
                    │                      │
                    │ Ollama / Fox /       │
                    │ Mullama              │
                    └──────────┬───────────┘
                               │
                               ┊ optional
                               ▼
                    ┌──────────────────────┐
                    │   Cloud AI Providers │
                    │   BYOK / Fallback    │
                    └──────────────────────┘

The important distinction

Study Forge is web-accessible, but it does not provide the server.

Study Forge uses a BYOS model: Bring Your Own Server.

The owner chooses where the processing engine runs.

Possible deployments include:

VPS

Dedicated server

Home server

Private cloud instance

Other user-controlled infrastructure


The same Study Forge engine can run in these environments.


---

🌐 Web Dashboard

The Study Forge dashboard has been built and is present in the repository.

The dashboard is intended to provide browser-based access to Study Forge rather than requiring the user to operate the application directly from a terminal.

Current status

Dashboard: ✅ Built
Public deployment: 🚧 Not yet live

The intended domain is:

studyforge.studio

Cloudflare is being used for the web-facing infrastructure, DNS, security, performance, and eventual deployment.

The dashboard being hosted on the web does not mean Study Forge becomes a centralized SaaS.

The dashboard is simply the interface.

The processing infrastructure remains BYOS.


---

🖥️ BYOS — Bring Your Own Server

Study Forge does not provide centralized AI compute.

The user supplies the infrastructure used to run the processing engine.

For example:

studyforge.studio
        │
        ▼
   Web Dashboard
        │
        ▼
    User's Server
        │
        ▼
 Study Forge Engine
        │
        ▼
Private AI Provider

This allows the user to avoid running large AI models directly on their laptop or desktop.

The server can be located wherever the owner chooses.

Why BYOS?

AI inference can consume significant:

RAM

CPU

GPU

Storage

Power


Moving the processing engine to a server means the user's everyday device primarily acts as the client.

The architecture therefore separates:

Access device

from

Processing infrastructure


---

🔐 Private-First Inference

Private-first refers to where AI inference is performed and who controls the inference infrastructure.

The preferred processing path is:

Study Material
      ↓
BYOS Study Forge Server
      ↓
Private AI Provider
      ↓
Study Forge Pipeline

The preferred private providers are:

Ollama

Fox

Mullama


Study material does not need to be sent to a third-party cloud AI provider simply because Study Forge is accessed through a web browser.


---

☁️ Optional Cloud Fallback

Cloud AI is an optional fallback rather than the primary architecture.

The intended relationship is:

Private Inference
   │
   ┊ optional fallback
   ▼
Cloud Provider

Potential cloud providers include:

Groq

Cloudflare AI

Google Gemini

Hugging Face


Cloud providers require BYOK: Bring Your Own Key.

Study Forge does not provide or centrally manage AI API keys.


---

🔑 BYOK — Bring Your Own Key

Users who enable cloud providers supply their own credentials.

Study Forge does not:

Provide AI API keys

Sell API access

Centrally collect user keys

Hard-code credentials

Commit credentials to the repository

Store credentials unnecessarily


Credentials are supplied through configuration/environment variables.


---

🤖 AI Provider Architecture

Study Forge uses a provider abstraction so the processing pipeline is not permanently tied to one AI provider.

Private providers

Provider	Role

Ollama	Private/local inference
Fox	Private/local inference
Mullama	Private/local inference


Cloud providers

Provider	Role

Groq	Optional cloud fallback
Cloudflare AI	Optional cloud provider
Google Gemini	Optional cloud provider
Hugging Face	Optional cloud provider


Providers can be configured and reordered without rewriting the entire processing pipeline.


---

🔄 Provider Fallback

The fallback system is modular.

Conceptually:

Ollama
   ↓ unavailable/failure
Fox
   ↓ unavailable/failure
Mullama
   ┊
   ┊ optional cloud fallback
   ▼
Groq
   ↓ failure
Cloudflare AI
   ↓ failure
Google Gemini
   ↓ failure
Hugging Face

The exact provider order is configurable.

A provider may be considered unavailable when it:

Is not configured

Cannot be reached

Times out

Returns an error

Fails authentication

Produces an unusable response


Failures should be logged without exposing credentials.


---

🧠 Multi-Agent Processing

Study Forge does not rely on one giant prompt.

The processing pipeline uses specialized agents.

Study Material
      ↓
Text Extraction
      ↓
 ┌──────────────┬──────────────┬──────────────┬──────────────┐
 │              │              │              │
 ▼              ▼              ▼              ▼
Summary      Key Points    Flashcards    Definitions
 │              │              │              │
 └──────────────┴──────────────┴──────────────┘
                       ↓
                 Judge / Synthesis
                       ↓
                  Color Coder
                       ↓
                Structured Output
                       ↓
                     Notion

Summarizer

Creates a concise study summary.

Key Points

Extracts the most important takeaways.

Flashcards

Creates question-and-answer material designed for active recall.

Definitions

Identifies important terminology and explanations.

Judge / Synthesis

The Judge evaluates the specialized outputs.

It:

Compares results

Removes weak information

Removes unnecessary duplication

Resolves conflicts

Produces a coherent synthesis


The Judge is an evaluator/synthesizer, not simply another generic generation step.

Color Coder

Applies semantic classifications to the resulting study material.


---

🎨 Semantic Color System

The color system is functional.

These colors represent different categories of information.

Hex	Meaning

#000000	Main Topics / Headers
#0000FF	Standard Notes
#ADD8E6	Scanning Protocols / Positioning
#000080	Anatomical Structures / Pathologies
#800080	Physics / Math / Formulas
#FF69B4	Clinical Red Flags / Contraindications / Safety
#008000	Professor Tips / Clinical Application
#FF0000	Corrections / Professor Emphasis


Classification should be semantic/contextual rather than relying exclusively on simplistic keyword matching.


---

📥 Input Formats

The current ingestion system supports:

PDF

DOCX

PPTX

TXT

Markdown


The architecture can be extended later for:

Images/OCR

Audio

Video

Additional document formats


Future formats should not unnecessarily complicate the core processing pipeline.


---

📤 Output

Study Forge produces structured study results that can be preserved locally and/or sent to Notion.

The processing pipeline is designed so that an output-service failure does not unnecessarily destroy generated study material.


---

📝 Notion

Notion is the current primary external study-output destination.

Users provide:

NOTION_API_TOKEN=
NOTION_DATABASE_ID=

Notion is optional.

Study Forge should still preserve generated results when Notion is unavailable.


---

☁️ Cloudflare

Cloudflare provides the web-facing infrastructure for the Study Forge dashboard.

The repository contains Cloudflare components for:

Web hosting

Worker/API infrastructure

R2 storage

D1 metadata storage


Cloudflare is not intended to replace the BYOS processing server.

Its primary role is the web-facing layer and supporting infrastructure.


---

🔒 Security

The web deployment requires appropriate protection because Study Forge processes potentially sensitive academic material.

The deployment should use:

HTTPS

Authentication/access control

Secure credential handling

Server-side validation

Secure file handling

No credentials in source code

No credentials in logs


Cloudflare Zero Trust is intended to provide access control for the private Study Forge deployment.

The dashboard is not intended to be an unrestricted public upload endpoint.


---

💰 Cost Philosophy

Study Forge follows a $0-first philosophy.

The software itself should not require users to purchase a Study Forge subscription.

Preferred options include:

Open-source software

Self-hosted infrastructure

Free tiers

Local/private inference

BYOK cloud providers


Users may choose paid infrastructure or provider plans if they want them.

Those costs belong to the user's chosen infrastructure/provider and are not required by Study Forge itself.


---

⚙️ Configuration

Study Forge uses centralized configuration.

Typical configuration includes:

LOCAL_PROVIDER=
LOCAL_MODEL=

OLLAMA_BASE_URL=

FOX_BASE_URL=
FOX_MODEL=
FOX_TIMEOUT=

MULLAMA_BASE_URL=
MULLAMA_MODEL=

GROQ_API_KEY=
CLOUDFLARE_API_TOKEN=
CLOUDFLARE_ACCOUNT_ID=
GEMINI_API_KEY=
HUGGINGFACE_API_KEY=

NOTION_API_TOKEN=
NOTION_DATABASE_ID=

PROVIDER_FALLBACK_ORDER=

INPUT_FOLDER=
OUTPUT_FOLDER=

The exact variables are defined by the implementation and .env.example.

Never commit real credentials.


---

📁 Repository Structure

The repository is organized around separated responsibilities:

Study-Forge/
├── agents/
├── cloudflare/
├── config/
├── ingestion/
├── input/
├── output/
├── pipeline/
├── providers/
├── utils/
├── web/
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── main.py
└── requirements.txt

The core Python processing engine and web infrastructure are intentionally separated.


---

📊 Implementation Status

Component	Status

Project structure	✅
Configuration system	✅
Environment template	✅
Provider abstraction	✅
Provider manager	✅
Ollama	✅
Fox	✅
Mullama	✅
Groq	✅
PDF ingestion	✅
DOCX ingestion	✅
PPTX ingestion	✅
TXT/Markdown ingestion	✅
Summarizer	✅
Key Points	✅
Flashcards	✅
Definitions	✅
Judge/Synthesis	✅
Color Coder	✅
Result preservation	✅
Notion output	✅
Web dashboard	✅ Built
Cloudflare infrastructure	🚧 Deployment
studyforge.studio	🚧 Not live
Web → processing integration	🚧
BYOS server deployment	🚧
Hosted private inference	🚧
Cloudflare AI provider	🔮
Gemini provider	🔮
Hugging Face provider	🔮
Image/OCR processing	🔮
Audio/Video processing	🔮
Obsidian output	🔮



---

🎯 Current Development Target

The immediate objective is not rebuilding the Study Forge engine.

The core processing system already exists.

The next stage is connecting the existing pieces:

Browser
   ↓
Completed Web Dashboard
   ↓
Cloudflare Web/API Layer
   ↓
BYOS Processing Server
   ↓
Existing Study Forge Engine
   ↓
Private Inference
   ↓
Agent Pipeline
   ↓
Judge
   ↓
Color Coder
   ↓
Structured Output
   ↓
Notion

The goal is to make the entire workflow usable through the browser while keeping compute under the user's control.


---

🚀 Deployment Direction

Study Forge is transitioning from:

Run everything directly on my computer

to:

Open Study Forge in a browser
        ↓
Web dashboard
        ↓
User-controlled server
        ↓
Private inference
        ↓
Study Forge processing

This reduces the resource burden on the user's everyday computer while preserving the private-first architecture.

The deployment model is therefore:

Web UI

Hosted/accessed through the web

Processing

BYOS

Private AI

Preferred

Cloud AI

Optional BYOK fallback

Study Forge itself

Free/open source

SaaS subscription

Not required


---

📜 License

Study Forge is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

The AGPL license is intentional.

Do not replace it with MIT, Apache, BSD, or another license without an explicit project-owner decision.

Future dual-licensing possibilities are outside the current implementation scope.

See LICENSE for the complete license.


---

🔨 Project Principle

Study Forge is built around a simple idea:

> Make powerful study-material processing accessible to students without requiring them to surrender control of their infrastructure or pay for access to the software.



The architecture reflects that:

STUDY FORGE
                     │
          ┌──────────┴──────────┐
          │                     │
      Web Access             BYOS
          │                     │
          │              User-controlled
          │                processing
          │                     │
          └──────────┬──────────┘
                     │
              Private-first AI
                     │
              Optional BYOK
               cloud fallback
                     │
                     ▼
              Study Materials
                     │
                     ▼
             Structured Study
                     │
                     ▼
                  Notion

Your interface.
Your server.
Your keys.
Your data.

🔨