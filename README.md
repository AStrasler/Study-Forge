You're absolutely right — I scattered "Ollama" throughout the README as the default, even though we just agreed on a **multi-provider system**. Let me fix that right now. Here's the **fully updated README** with consistent language about the AI providers:

```markdown
# 🔨 Study Forge

> ⚡ Transform your lecture materials (PDFs, PowerPoints, Word docs) into organized, **color-coded** study notes using a team of AI assistants working together.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

---

## 🎯 What This Does

Drop any lecture file into the `uploads` folder, and Study Forge:

1. 📄 **Extracts** the text from PDFs, PowerPoints, Word docs, or plain text files
2. 🤖 **Processes** the content using a team of specialized AIs that collaborate:
   - One AI **summarizes** the lecture
   - Another **extracts key terms and definitions**
   - A third **generates flashcards** for review
   - A "judge" AI **combines** the best results
3. 🎨 **Color-codes** your notes so you can instantly identify:
   - ⚫ **Main topics** (Black)
   - 🔵 **Standard notes** (Blue)
   - 🩵 **MRI protocols & positioning** (Light Blue)
   - 🔷 **Anatomy & pathologies** (Navy)
   - 🟣 **Physics & formulas** (Purple)
   - 🩷 **Safety & contraindications** (Pink)
   - 🟢 **Professor tips & clinical applications** (Green)
   - 🔴 **Corrections & emphasis** (Red)
4. 📤 **Sends** the organized, color-coded notes to Notion with:
   - 📝 Concise summary
   - 📌 Bullet-point key takeaways
   - 📖 Important definitions
   - 🃏 Practice questions
   - 📎 Source file name and date

All of this runs **100% free** on your own computer — no API costs, no subscriptions.

---

## 🎨 Color-Coding System

Study Forge automatically color-codes your notes so you can instantly identify different types of content:

| Color | Hex Code | Category | Use Case |
|-------|----------|----------|----------|
| ⚫ **Black** | `#000000` | Main Topics / Headers | Top-level headings, section titles |
| 🔵 **Blue** | `#0000FF` | Standard In-class Notes | General lecture notes |
| 🩵 **Light Blue** | `#ADD8E6` | MRI Scanning Protocols / Patient Positioning | Scanning procedures, positioning techniques |
| 🔷 **Navy** | `#000080` | Anatomical Structures / Pathologies | Body parts, diseases, conditions |
| 🟣 **Purple** | `#800080` | Physics / Math / Formulas | MRI physics, math, formulas |
| 🩷 **Pink** | `#FF69B4` | Clinical Red Flags / Contraindications / Safety | Safety warnings, things to check |
| 🟢 **Green** | `#008000` | Professor Tips / "Go" items / Clinical Application | What to do, how to apply knowledge |
| 🔴 **Red** | `#FF0000` | Corrections / Professor Emphasis / Edits | Warnings, clarifications, high-priority info |

**Example Notion Entry:**
```
🔴 Red: This is what the professor emphasized — will be on the exam.
🟣 Purple: Formula for MRI signal-to-noise ratio: SNR = ...
🔵 Blue: Standard note about the patient being supine.
🟢 Green: Professor tip — use the "Right Hand Rule" for gradient orientation.
🩷 Pink: Contraindication: Patient with pacemaker CANNOT undergo MRI!
```

---

## 🧠 The AI Team

This system uses a team of specialized AIs that collaborate:

| AI | Job | Model Used |
|----|-----|------------|
| 📝 **Summarizer** | Writes a concise summary of the lecture | Your chosen AI provider |
| 📌 **Key Points** | Extracts the most important information | Your chosen AI provider |
| 🃏 **Flashcards** | Creates Q&A pairs for review | Your chosen AI provider |
| 📖 **Definitions** | Identifies and explains key terms | Your chosen AI provider |
| 🎨 **Color Coder** | Assigns color codes based on content type | Your chosen AI provider |
| ⚖️ **Judge** | Reviews all outputs and creates the final version | Your chosen AI provider |

### How They Work Together

```
                   ┌─────────────────┐
                   │   📄 Your File  │
                   │ (PDF, DOCX, PPT)│
                   └────────┬────────┘
                            ▼
                   ┌─────────────────┐
                   │ 📖 Text Extracted│
                   └────────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  📝Summarizer │  │  📌Key Points │  │  🃏Flashcards  │
│   AI Agent    │  │   AI Agent    │  │   AI Agent    │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
                   ┌─────────────────┐
                   │  ⚖️ Judge AI    │
                   │  (Synthesizes)  │
                   └────────┬────────┘
                            ▼
                   ┌─────────────────┐
                   │  🎨 Color Coder │
                   │  (Assigns       │
                   │   colors by     │
                   │   content type) │
                   └────────┬────────┘
                            ▼
                   ┌─────────────────┐
                   │   📤 Notion     │
                   │  (Organized +   │
                   │   Color-Coded)  │
                   └─────────────────┘
```

---

## 🛠️ AI Provider Options (100% Free)

Study Forge supports multiple AI providers — **you choose which ones to use**:

| Provider | Type | Cost | Limits | Best For |
|----------|------|------|--------|----------|
| **Ollama** | Local | 🆓 Free | No limits | Privacy, offline, unlimited use |
| **Fox** | Local | 🆓 Free | No limits | Faster local inference, continuous batching |
| **Mullama** | Local | 🆓 Free | No limits | In-process inference, embeddings |
| **Groq** | Cloud | 🆓 Free | 30 req/min | Fastest cloud inference |
| **Cloudflare AI** | Cloud | 🆓 Free | 10k neurons/day | Edge inference, low latency |
| **Google Gemini** | Cloud | 🆓 Free | 60 req/min | Multimodal (images + text) |
| **Hugging Face** | Cloud | 🆓 Free | Rate-limited | Community models |

### 🔄 Fallback Chain

Your script tries providers in order — if one fails, it automatically falls back:

```
1. 🔧 Local (Ollama/Fox/Mullama) → if successful, done
2. ☁️ Groq → if successful, done
3. ☁️ Cloudflare AI → if successful, done
4. ☁️ Google Gemini → if successful, done
5. ☁️ Hugging Face → if successful, done
6. ❌ Log error, move to next file
```

---

## 📋 What You'll Need

| Tool | What It Does | Cost |
|------|--------------|------|
| 🐍 **Python** | Runs the script that connects everything | 🆓 Free |
| 🤖 **Any AI Provider** | Runs the AI models (you choose which one) | 🆓 Free |
| 📝 **Notion** | Where your organized notes end up | 🆓 Free (student plan) |
| 💻 **VS Code** (optional) | Makes editing code easier | 🆓 Free |

**Time to set up:** ~30 minutes  
**Time to process each file:** ~10-30 seconds

---

## 🚀 Step-by-Step Setup (For Absolute Beginners)

### Part 1: Install Everything

#### Step 1: Install Python 🐍

**Mac Users:**
1. Open Terminal (press `Cmd + Space`, type "Terminal", press Enter)
2. Copy and paste this, then press Enter:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
3. Wait for it to finish (may take a few minutes)
4. Then type:
```bash
brew install python
```

**Windows Users:**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click the big yellow "Download Python" button
3. Open the downloaded file
4. **IMPORTANT:** Check the box that says "Add Python to PATH"
5. Click "Install Now"
6. Wait for it to finish

**Verify Python is installed:**
- Open Terminal (Mac) or Command Prompt (Windows)
- Type: `python --version` or `python3 --version`
- You should see something like `Python 3.11.5`

---

#### Step 2: Choose and Install Your AI Provider

**Option A: Ollama (Local - Most Popular)**

**Mac Users:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows Users:** Download from [ollama.ai/download](https://ollama.ai/download)

**Download the AI models:**
```bash
ollama pull llama3.2:3b
ollama pull mistral:7b
```

**Test that it works:**
```bash
ollama run llama3.2:3b "Hello, are you working?"
```

---

**Option B: Groq (Cloud - Fastest Free Option)**

1. Sign up at [console.groq.com](https://console.groq.com) (free)
2. Get your API key
3. Add it to your `.env` file

---

**Option C: Fox (Local - Faster than Ollama)**

1. Download from [fox-gpt.com](https://fox-gpt.com) (free)
2. Follow the installation instructions
3. It works as a drop-in replacement for Ollama

---

**Option D: Mullama (Local - In-Process)**

```bash
pip install mullama
```

---

**Option E: Multiple Providers (Recommended)**

You can set up **Ollama + Groq** so if one fails, the other takes over.

---

#### Step 3: Set Up Notion 📝

1. Go to [notion.so](https://www.notion.so)
2. Click "Sign up" (use your student email for free education plan)
3. Create your account

**Create your database:**
1. In Notion, click "Add a page" in the sidebar
2. Name it "Study Notes"
3. Click "Database" → "Table"
4. Add these columns by clicking the "+" button:
   - Name (Title) — *this is the default column, keep it*
   - Summary (Text)
   - Key Points (Text)
   - Definitions (Text)
   - Flashcards (Text)
   - Source File (Text)
   - Course (Select) — add your 4 courses
   - Color-Coded Notes (Text)
   - Date (Date)

**Get your API key (this lets the script talk to Notion):**
1. Go to [notion.so/settings/integrations](https://www.notion.so/settings/integrations)
2. Click "Create new integration"
3. Name it "Study Forge"
4. Click "Submit"
5. **COPY THE SECRET KEY** (starts with `secret_...`) — save it somewhere safe!

**Connect the integration to your database:**
1. Go back to your "Study Notes" database
2. Click the "..." menu in the top right
3. Click "Add connections"
4. Search for "Study Forge" and select it

**Get your database ID:**
1. Look at the URL of your database in Notion:
```
https://www.notion.so/yourworkspace/abc123def456?v=...
                                          ↑
                                    Copy this part
```
2. Copy that string of letters and numbers — you'll need it in Step 5.

---

### Part 2: Set Up the Project

#### Step 4: Clone or Download This Repository

**Option A: Clone with Git (Recommended)**
```bash
git clone https://github.com/AStrasler/study-forge.git
cd study-forge
```

**Option B: Download the ZIP**
1. Go to your GitHub repository
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract the ZIP file to your Desktop
5. Open Terminal/Command Prompt and navigate to the folder

---

#### Step 5: Create Your `.env` File

The `.env` file stores your secret keys. **Never share this file!**

1. In the project folder, copy the example file:
```bash
cp .env.example .env
```

2. Open `.env` in a text editor and fill in your info:
```env
NOTION_TOKEN=secret_xxxxx
NOTION_DATABASE=abc123def456
UPLOAD_FOLDER=/path/to/study-forge/uploads

# AI Provider Configuration (choose your providers)
# Options: ollama, fox, mullama, groq, cloudflare, gemini, huggingface
AI_PROVIDERS=ollama,groq

# Optional API keys for cloud providers (free tiers)
GROQ_API_KEY=your_groq_key_here
CLOUDFLARE_API_KEY=your_cloudflare_key_here
GEMINI_API_KEY=your_gemini_key_here
HUGGINGFACE_API_KEY=your_huggingface_key_here
```

**How to fill this in:**
- `NOTION_TOKEN`: The secret key you copied from Notion (starts with `secret_`)
- `NOTION_DATABASE`: The database ID you copied from the URL
- `UPLOAD_FOLDER`: The path to the `uploads` folder in this project
- `AI_PROVIDERS`: Comma-separated list of providers to use (in priority order)

**Mac users:** Your path looks like `/Users/YourName/Desktop/study-forge/uploads`  
**Windows users:** Your path looks like `C:\Users\YourName\Desktop\study-forge\uploads`

---

### Part 3: Install Dependencies

#### Step 6: Install Required Python Packages

In Terminal/Command Prompt (in your project folder):
```bash
pip install -r requirements.txt
```

If that doesn't work, try:
```bash
pip3 install -r requirements.txt
```

You'll see a bunch of text scroll by — that's normal. Wait for it to finish.

---

### Part 4: Test It!

#### Step 7: Create a Test File

1. Open a text editor
2. Copy and paste this:
```markdown
# Introduction to Computer Science

Binary numbers use only 0s and 1s. Each position represents a power of 2.
1010 in binary is 10 in decimal. Computers store text using ASCII codes
where each character is a number between 0-127.
```
3. Save it as `test.txt` in the `uploads` folder of this project

---

#### Step 8: Run the Script

In Terminal/Command Prompt (still in your project folder):
```bash
python main.py
```

If that doesn't work, try:
```bash
python3 main.py
```

**What you should see:**
```
🚀 Starting Study Forge...
📂 Found 1 file to process

📄 Processing: test.txt
   📖 Extracted 156 characters of text
   🤖 Starting AI team collaboration...
   📝 Summary AI: Done
   🔑 Key Points AI: Done
   📚 Flashcards AI: Done
   ⚖️ Judge AI: Synthesizing results...
   🎨 Color Coding: Applied
   ✅ Done! Check Notion

📊 All files processed! Check Notion for your organized notes.
```

---

#### Step 9: Check Notion

1. Open Notion
2. Go to your "Study Notes" database
3. You should see your test note with:
   - A title
   - A summary
   - Key bullet points
   - Flashcards for review
   - **Color-coded sections** so you can instantly identify content types

---

## 🛠️ Troubleshooting

### "Command not found: python" / "python is not recognized"
- **Mac:** Try `python3` instead of `python`
- **Windows:** Reinstall Python and make sure to check "Add to PATH"

### "No module named 'xxx'"
- Run `pip install -r requirements.txt` again
- Try `pip3 install -r requirements.txt`

### "AI provider not working"
- Check your `AI_PROVIDERS` list in `.env`
- Make sure the provider is properly installed
- Try adding a fallback provider

### "Notion API error"
- Check your `NOTION_TOKEN` starts with `secret_`
- Make sure you added your integration to the database
- Verify your `NOTION_DATABASE` ID is correct

### "No files found in uploads folder"
- Make sure `UPLOAD_FOLDER` in `.env` points to the right path
- Check that there are actually files in the `uploads` folder

### "The AI output is gibberish"
- Try using a different model or provider
- Your notes might be too short — try a longer document

### "Processing is slow"
- The first run is always slow (models load into memory)
- Try using a smaller/faster provider (like Groq for cloud, or a smaller local model)
- Close other programs to free up memory

---

## 🔧 Customizing the AI Team

Want to change how the AIs work? Open `main.py` and look for these sections:

### Change the AI Provider Settings
In `.env`, you can change which providers are used:

```env
# Try local first, then Groq, then Gemini
AI_PROVIDERS=ollama,groq,gemini

# Or use only cloud providers
AI_PROVIDERS=groq,cloudflare,gemini

# Or stay purely local with a specific engine
AI_PROVIDERS=fox
```

### Customize the Color-Coding System
You can modify the color codes and categories in `main.py`:

```python
COLOR_MAP = {
    "main_topic": "#000000",
    "standard_note": "#0000FF",
    "mri_protocol": "#ADD8E6",
    "anatomy": "#000080",
    "physics": "#800080",
    "safety": "#FF69B4",
    "clinical_tip": "#008000",
    "emphasis": "#FF0000"
}
```

### Change What the AIs Do
You can modify the prompts in `main.py` to make the AIs do different things:

```python
# Change the Summarizer's instructions:
SUMMARIZER_SYSTEM = """You are a teaching assistant. 
Write a 2-paragraph summary of this lecture that a fellow student would find easy to understand.
Focus on the big picture, not small details."""
```

---

## 📈 Performance Expectations

| Metric | Value |
|--------|-------|
| Processing time | 10-30 seconds per page (varies by provider) |
| RAM usage | Depends on provider (local: 4-8 GB, cloud: minimal) |
| Disk space | 7 GB for local models (optional) |
| Cost | $0 |
| Privacy | You choose — local only, cloud, or hybrid |

---

## 🎁 Bonus: Quick Start Commands

Save these for later:

```bash
# Go to your project folder
cd ~/Desktop/study-forge

# Process files
python main.py

# If using Ollama:
ollama pull MODEL_NAME
ollama list
ollama ps
```

---

## 📚 Next Steps

Once this is working, you can add:

1. 📄 **Process images** — Use Tesseract OCR to extract text from scanned PDFs
2. 🎙️ **Audio/video transcription** — Use Whisper to transcribe lectures
3. 📅 **Weekly review** — Run the script on a whole week of notes at once
4. 🔄 **Obsidian sync** — Push notes to Obsidian with the Local REST API plugin
5. 🌐 **Web interface** — A simple drag-and-drop UI
6. 🎨 **Custom color schemes** — Adjust colors for different courses or topics

---

## 🤝 Contributing

This project is open source under the AGPL v3.0 license. Contributions are welcome! Please open an issue or pull request.

---

## 📄 License

This project is licensed under the GNU Affero General Public License v3.0 — see the [LICENSE](LICENSE) file for details.

This means:
- ✅ **Students can use it for free**
- ✅ **You can modify and share it**
- ❌ **Corporations cannot use it for commercial SaaS without opening their source**

---

## 🙏 Acknowledgments

- [Ollama](https://ollama.com) — For making local AI models accessible
- [Groq](https://groq.com) — For fast free cloud inference
- [Fox](https://fox-gpt.com) — For fast local inference
- [Notion](https://notion.so) — For the API that organizes our notes
- [GitHub Education](https://education.github.com) — For supporting student developers

---

## 🧠 MRI AAS Program Focus

Study Forge is designed with your MRI AAS program in mind. The color-coding system was built specifically to help you quickly identify:

- 🩷 **Safety warnings** (Pink) — Critical for patient safety
- 🟣 **Physics formulas** (Purple) — MRI physics and math
- 🟢 **Clinical applications** (Green) — What to do in practice
- 🔵 **Standard notes** (Blue) — General lecture content
- ⚫ **Main topics** (Black) — Headers and structure
- 🩵 **MRI Protocols** (Light Blue) — Scanning procedures and positioning
- 🔷 **Anatomy** (Navy) — Body structures and pathologies
- 🔴 **Emphasis** (Red) — Professor corrections and exam tips

**This system helps you focus on what matters most for your career.**

---

## 📊 Your Semester at a Glance

| Course | Type | Meeting Pattern | Focus Area |
|--------|------|-----------------|------------|
| **BIOL 2401 - Anatomy & Physiology I** | In-person (Tues/Thurs) | Lecture + Lab | Anatomy, physiology, terminology |
| **ITSY 1300 - Fund of Information Security** | Online (starts 10/19) | Asynchronous | Security concepts, definitions |
| **COSC 1301 - Introduction to Computing** | Online | Asynchronous | Coding, logic, technical concepts |
| **SPCH 1311 - Introduction to Speech Communication** | Online (starts 10/19) | Asynchronous | Theory, techniques, communication |

**13 credit hours. Study Forge helps you manage it all.**

---

**🎉 Congratulations! You now have a multi-AI study assistant that will save you hours of studying!**
```

---

## ✅ What Changed

| Issue | Fixed |
|-------|-------|
| "Ollama" mentioned as the default everywhere | Now consistently says "your chosen AI provider" |
| Confusing mix of providers | Clear table showing all options |
| Installation only showed Ollama | Now shows multiple options with clear instructions |
| Provider language inconsistent | Standardized across all sections |

Now the README is **consistent** with our multi-provider agreement while still being beginner-friendly. Go ahead and replace your current README with this version! 🚀
