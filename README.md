# 🚀 Nexus MCP: Multi-Orchestrator Agent Nexus

The **Nexus MCP** is a high-performance, model-agnostic coding server designed to execute complex, multi-agent tasks on your local codebase. It combines **LangGraph** (Macro-Orchestration) and **LiteLLM** (Micro-Orchestration) to perform surgical code modifications with extreme reliability.

---

## 🔥 Key Features

- **Multi-Orchestrator**: Uses a Graph state machine to manage complex workflows and a fluid LLM loop for task execution.
- **Git Sandbox**: Automatically isolates work on feature branches (optional) to protect your main codebase.
- **Model Agnostic**: Purely powered by [LiteLLM](https://github.com/BerriAI/litellm). Optimized for **Groq** (Llama 3.3 70B) for lightning-fast speeds.
- **AST-Aware Reading**: Reads code outlines (classes/functions) before fetching raw code to minimize context tokens.
- **Direct Mode**: Toggle `isolate: false` to apply changes directly to your current working branch.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Git initialized in your target project.

### 2. Install Dependencies
```bash
pip install mcp langgraph litellm python-dotenv pydantic
```

### 3. Configure Environment
Create a `.env` file in the root:
```env
GROQ_API_KEY=gsk_your_key_here
SWARM_MODEL="groq/llama-3.3-70b-versatile"
```

### 4. Run the Server
```bash
python src/server.py
```

---

## 🔌 Connecting to IDEs

### Cursor / Windsurf
1. Open **Settings** -> **MCP**.
2. Add a new server:
   - **Name**: `Nexus-MCP`
   - **Type**: `command`
   - **Command**: `python c:/absolute/path/to/src/server.py`

### Claude Desktop
Add the following to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "nexus-mcp": {
      "command": "python",
      "args": ["c:/absolute/path/to/src/server.py"]
    }
  }
}
```

---

## 🌍 Open Source Hosting

### 1. GitHub
Push this repository to GitHub. Ensure `.env` is in `.gitignore` to protect your API keys.

### 2. Smithery.ai
Register your MCP on [Smithery](https://smithery.ai) to make it searchable by the global MCP community.

### 3. PyPI (Coming Soon)
We recommend distributing as a Python package for `pip install nexus-mcp`.

---

## 📜 License
MIT
