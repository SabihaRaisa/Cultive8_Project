# AI Usage Disclosure

I used AI tools during the development of this project to help with coding, debugging, and improving the application.

## 1. AI Tools Used

- ChatGPT (GPT-6): Helped with coding, fixing errors, connecting the frontend and backend, and writing documentation.
- Ollama: Runs the AI model locally for log analysis.
- Qwen2.5 0.5B: The model currently used for log analysis.
- Hugging Face Tokenizer: Used for token counting and splitting log files.

Note: The assessment mentions Qwen3.5 and Gemma 4 E2B models. My project currently uses Qwen2.5 0.5B.

## 2. How I Used ChatGPT

I used ChatGPT to understand the requirements, organize the project, develop backend and frontend components, implement log chunking, connect Ollama, fix errors, and prepare documentation.

I developed the project step by step and tested different components along the way.

## 3. How AI Works in the Application

The application uses Ollama to analyze uploaded .log and .txt files.

Large files are divided into smaller chunks and sent to the local AI model one by one. The model identifies possible security issues and returns findings in JSON format.

The backend validates the results, saves them in SQLite, and generates a combined report.

## 4. Token Management

The model uses a 2,048-token context window. The available tokens are divided between instructions, previous findings, log content, and AI responses.

The backend checks token usage before sending each request to avoid exceeding the limit.

## 5. Security and Privacy

- Only .log and .txt files are accepted.
- Maximum upload size is 10 MB.
- Uploaded logs are treated as untrusted data.
- AI responses are validated before saving.
- Results are stored locally in SQLite.
- Ollama runs locally without using a cloud AI inference API.

## 6. Limitations

The AI may sometimes miss threats or produce incorrect findings. Offline operation also requires downloading the model and tokenizer beforehand.

The application still needs testing on the target computer to verify memory usage and complete offline functionality.

## 7. Final Statement

ChatGPT was used as a coding assistant, while Ollama performs the actual log analysis. I am responsible for reviewing, testing, and understanding the submitted project.