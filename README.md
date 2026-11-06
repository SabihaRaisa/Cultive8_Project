# Local AI Security Log Analyzer

A simple local tool that analyzes server logs and identifies possible security threats using AI.

The application uses **React, FastAPI, SQLite, and Ollama**. It processes log files in smaller chunks, analyzes them one by one, and generates a combined security report.

## 1. Architecture

- **React + Vite:** User dashboard
- **FastAPI:** Backend API
- **Ollama:** Runs the AI model locally
- **Hugging Face:** Tokenizer and text splitting
- **SQLite:** Stores analysis results
- **Report Generator:** Combines findings from all chunks

## 2. Requirements

- Python 3.10+
- Node.js 18+
- npm
- Ollama
- Internet for initial downloads
- Sufficient RAM to run the selected model

The default model is `qwen2.5:0.5b-instruct`, with its matching Hugging Face tokenizer.

**Note:** The assessment mentions Qwen3.5 0.8B/2B and Gemma 4 E2B. My current model is different, so its acceptability should be confirmed.

## 3. Install Ollama

Install Ollama and run:

```bash
ollama pull qwen2.5:0.5b-instruct
ollama list
```

Ollama runs locally at `http://localhost:11434`.

## 4. Backend Setup

Open the terminal in VS Code:

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

API: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## 5. Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

To check the production build:

```bash
npm run build
```

## 6. How It Works

1. Upload a `.log` or `.txt` file.
2. The backend splits the file into smaller chunks.
3. Each chunk is sent to the local AI model.
4. The AI identifies possible security issues.
5. Results are saved in SQLite.
6. Findings from all chunks are combined into one report.

The dashboard displays severity, evidence, line numbers, reasons, and suggested actions.

## 7. Token Management

The model uses a 2,048-token context window.

The analyzer keeps space for instructions, previous findings, log content, and AI responses. It also checks token usage before sending each request.

Long log files are split while keeping their original line numbers.

## 8. Security Features

- Accepts only `.log` and `.txt` files.
- Maximum upload size: 10 MB.
- Validates AI responses before saving.
- Processes chunks sequentially.
- Stores results in SQLite.
- Treats uploaded logs as untrusted input.
- Checks Ollama and model availability before analysis.

## 9. Testing

Run the following tests from the backend folder:

```bash
python test_security_components.py
python test_correlation.py
python test_database.py
python test_chunking.py
python test_ollama.py
python test_ai_analyzer.py
```

Some tests require Ollama and the tokenizer to be installed.

## 10. Limitations

- AI results may not always be accurate.
- Small models may miss some security threats.
- Restarting the backend can interrupt an ongoing analysis.
- Offline operation requires the model and tokenizer to be downloaded beforehand.
- The application is a prototype, not a production-ready security platform.

## 11. Responsible Use

This tool is intended for defensive security analysis. Only analyze logs you are authorized to access. Always verify AI findings before taking action.