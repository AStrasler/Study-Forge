```markdown
# 🔨 Study Forge

> Transform your lecture materials (PDFs, PowerPoints, Word docs) into organized, searchable study notes using a team of AI assistants working together.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

---

## 🎯 What This Does

Drop any lecture file into the `uploads` folder, and Study Forge:

1. **Extracts** the text from PDFs, PowerPoints, Word docs, or plain text files
2. **Processes** the content using a team of specialized AIs that collaborate:
   - One AI **summarizes** the lecture
   - Another **extracts key terms and definitions**
   - A third **generates flashcards** for review
   - A "judge" AI **combines** the best results
3. **Sends** the organized notes to Notion with:
   - Concise summary
   - Bullet-point key takeaways
   - Important definitions
   - Practice questions
   - Source file name and date

All of this runs **100% free** on your own computer — no API costs, no subscriptions.

---

## 📋 What You'll Need

| Tool | What It Does | Cost |
|------|--------------|------|
| **Python** | Runs the script that connects everything | Free |
| **Ollama** | Runs AI models on your computer | Free |
| **Notion** | Where your organized notes end up | Free (student plan) |
| **VS Code** (optional) | Makes editing code easier | Free |

**Time to set up:** ~30 minutes  
**Time to process each file:** ~10-30 seconds

---

## 🚀 Step-by-Step Setup (For Absolute Beginners)

### Part 1: Install Everything

#### Step 1: Install Python

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

#### Step 2: Install Ollama (The Free AI)

**Mac Users:**
1. In Terminal, type:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```
2. Press Enter, wait for it to finish

**Windows Users:**
1. Go to [ollama.ai/download](https://ollama.ai/download)
2. Click "Download for Windows"
3. Open the downloaded file and install it

**Download the AI models:**
1. Open Terminal (Mac) or Command Prompt (Windows)
2. Type:
```bash
ollama pull llama3.2:3b
```
3. You'll see a progress bar as it downloads (~3GB, takes 5-10 minutes)
4. Once done, type:
```bash
ollama pull mistral:7b
```
5. Wait for this to download too (~4GB)

**Test that Ollama works:**
```bash
ollama run llama3.2:3b "Hello, are you working?"
```
You should get a response from the AI!

---

#### Step 3: Set Up Notion

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
git clone https://github.com/YOUR_USERNAME/study-forge.git
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
```

**How to fill this in:**
- `NOTION_TOKEN`: The secret key you copied from Notion (starts with `secret_`)
- `NOTION_DATABASE`: The database ID you copied from the URL
- `UPLOAD_FOLDER`: The path to the `uploads` folder in this project

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

---

## 🎓 How It Works (The AI Team)

This system uses a team of specialized AIs that collaborate:

### The Team Members

| AI | Job | Model Used |
|----|-----|------------|
| **Summarizer** | Writes a concise summary of the lecture | llama3.2:3b |
| **Key Points** | Extracts the most important information | llama3.2:3b |
| **Flashcards** | Creates Q&A pairs for review | mistral:7b |
| **Definitions** | Identifies and explains key terms | llama3.2:3b |
| **Judge** | Reviews all outputs and creates the final version | mistral:7b |

### How They Work Together

```
                   ┌─────────────────┐
                   │   Your File     │
                   │ (PDF, DOCX, PPT)│
                   └────────┬────────┘
                            ▼
                   ┌─────────────────┐
                   │ Text Extracted  │
                   └────────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  Summarizer   │  │  Key Points   │  │  Flashcards   │
│   AI Agent    │  │   AI Agent    │  │   AI Agent    │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
                   ┌─────────────────┐
                   │  Judge AI       │
                   │  (Synthesizes)  │
                   └────────┬────────┘
                            ▼
                   ┌─────────────────┐
                   │   Notion        │
                   │  (Organized)    │
                   └─────────────────┘
```

### Why This Is Better Than One AI

| One AI | Team of AIs |
|--------|-------------|
| Does everything itself | Each AI has one specialized job |
| Can get confused by complex content | Each expert focuses on what it does best |
| One perspective | Multiple perspectives on your lecture |
| Harder to verify correctness | Judge AI reviews and improves the output |

---

## 📁 Project Structure

```
study-forge/
├── main.py              # The main script — run this
├── requirements.txt     # Python dependencies
├── .env.example         # Template for your secrets
├── .gitignore           # Files Git should ignore
├── LICENSE              # AGPL v3.0 license
├── README.md            # This guide
└── uploads/             # Drop your files here
```

---

## 📅 Daily Workflow

1. **Before studying:** Drop your lecture PDF/PPT in the `uploads` folder
2. **Run the script:** `python main.py` in Terminal
3. **Open Notion:** Your notes are already organized and summarized
4. **Study:** Review the summary, key points, and flashcards

---

## 🛠️ Troubleshooting

### "Command not found: python" / "python is not recognized"
- **Mac:** Try `python3` instead of `python`
- **Windows:** Reinstall Python and make sure to check "Add to PATH"

### "No module named 'xxx'"
- Run `pip install -r requirements.txt` again
- Try `pip3 install -r requirements.txt`

### "Can't find Ollama"
- Open a new Terminal window
- Run `ollama serve` to start Ollama
- Then run your script in a different Terminal window

### "Notion API error"
- Check your `NOTION_TOKEN` starts with `secret_`
- Make sure you added your integration to the database
- Verify your `NOTION_DATABASE` ID is correct

### "No files found in uploads folder"
- Make sure `UPLOAD_FOLDER` in `.env` points to the right path
- Check that there are actually files in the `uploads` folder

### The AI output is gibberish
- Try using a different model:
  1. Download a different one: `ollama pull phi3`
  2. Update the model names in `main.py`
- Your notes might be too short — try a longer document

### Processing is slow
- The first run is always slow (models load into memory)
- Try using smaller models: `llama3.2:1b` instead of `llama3.2:3b`
- Close other programs to free up memory

---

## 🔧 Customizing the AI Team

Want to change how the AIs work? Open `main.py` and look for these sections:

### Change the Models
```python
SUMMARIZER_MODEL = "llama3.2:3b"      # Change to any downloaded model
KEY_POINTS_MODEL = "llama3.2:3b"      # Change to any downloaded model
FLASHCARDS_MODEL = "mistral:7b"       # Change to any downloaded model
JUDGE_MODEL = "mistral:7b"            # Change to any downloaded model
```

### Download More Models
```bash
ollama pull phi3           # Smaller, faster
ollama pull llama3.2:1b    # Very fast, less accurate
ollama pull llama3.1:8b    # Bigger, more accurate
ollama pull llama3.3:70b   # Huge, most accurate (needs lots of RAM)
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
| Processing time | 10-30 seconds per page |
| RAM usage | 4-8 GB (more for bigger models) |
| Disk space | 7 GB for the two recommended models |
| Cost | $0 |
| Privacy | 100% local — no data leaves your computer |

---

## 🎁 Bonus: Quick Start Commands

Save these for later:

```bash
# Go to your project folder
cd ~/Desktop/study-forge

# Process files
python main.py

# Download a new AI model
ollama pull MODEL_NAME

# List installed models
ollama list

# See what Ollama is doing
ollama ps
```

---

## 📚 Next Steps

Once this is working, you can add:

1. **Process images** — Use Tesseract OCR to extract text from scanned PDFs
2. **Audio/video transcription** — Use Whisper to transcribe lectures
3. **Weekly review** — Run the script on a whole week of notes at once
4. **Obsidian sync** — Push notes to Obsidian with the Local REST API plugin
5. **Web interface** — A simple drag-and-drop UI

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
- [Notion](https://notion.so) — For the API that organizes our notes
- [GitHub Education](https://education.github.com) — For supporting student developers

---

**🎉 Congratulations! You now have a multi-AI study assistant that will save you hours of studying!**

```

---

This README is now complete and ready to be the main documentation for your Study Forge repository. It includes:

- ✅ Complete beginner-friendly setup guide
- ✅ Clear explanation of how the AI team works
- ✅ Visual diagrams
- ✅ Troubleshooting section
- ✅ Customization instructions
- ✅ License and contribution info

Once you create the repository, you can copy-paste this into the README.md file. Let me know when you're ready for the `main.py` code and other files!
