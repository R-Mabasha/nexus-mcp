# 🚀 Nexus MCP: The Multi-Orchestrator AI Coding Agent

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Ready-success)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Nexus MCP** is a high-performance, model-agnostic **Model Context Protocol (MCP) Server** designed to transform your IDE into an autonomous multi-agent coding assistant. 

Integrating directly with **Claude Desktop**, **Cursor AI**, and **Windsurf**, Nexus MCP orchestrates complex codebase refactoring using **LangGraph** and **LiteLLM**. Instead of relying on a single zero-shot prompt, this framework deploys a specialized swarm of AI agents to strategically plan, confidently verify, and surgically write code within a secure Git Sandbox.

---

## 🌟 Why Nexus MCP? (Features)

When searching for an **MCP Agent** or **AI Coding Assistant**, you usually find single-prompt algorithms that risk hallucinating over large codebases. Nexus MCP solves this by combining deterministic graphs with fluid LLM swarms:

- 🧠 **Multi-Orchestrator Architecture**: Uses a graph state machine (LangGraph) to manage complex developer workflows and prevent infinite agent loops.
- 🛡️ **Git Sandbox Security**: Automatically isolates autonomous AI work on separate feature branches (optional) to protect your main codebase from destructive edits.
- ⚡ **Model Agnostic & Local Ready**: Purely powered by [LiteLLM](https://github.com/BerriAI/litellm). Native support for **Claude**, **OpenAI**, **Local LLMs**, and hyper-optimized for **Groq** (Llama 3.3 70B).
- 🔍 **AST-Aware File Context**: Reads the Abstract Syntax Tree (classes/functions) before fetching raw code strings to minimize context token overwhelm.
- 🎯 **Direct Editing Mode**: Toggle `isolate: false` in the MCP Tool schema to have the AI swarm apply code modifications directly to your current working branch.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Git initialized in your target project directory.

### 2. Install Dependencies
```bash
pip install mcp langgraph litellm python-dotenv pydantic
```

### 3. Configure Environment
Create a `.env` file in the root of your workspace:
```env
# Fast/Free Groq example
GROQ_API_KEY=gsk_your_key_here
SWARM_MODEL="groq/llama-3.3-70b-versatile"
```

### 4. Run the Agent Server
```bash
python src/server.py
```

---

## 🔌 Connecting to IDEs (MCP Integration)

Connect this AI Agent tool directly into your daily development environment:

### Cursor / Windsurf
1. Open **Settings** -> **MCP**.
2. Add a new server:
   - **Name**: `Nexus-MCP`
   - **Type**: `command`
   - **Command**: `python c:/absolute/path/to/src/server.py`

### Claude Desktop
Add the following configuration to your `claude_desktop_config.json`:
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

## 🌍 Open Source & Distribution

Nexus MCP is built natively for the open-source **Smithery.ai** MCP registry and GitHub discovery algorithms. Ensure you configure your `.gitignore` correctly before pushing your own forks!

See the [OPENSOURCE.md](OPENSOURCE.md) guide for more details on integrating this repo.

---

## 📜 License
MIT License.

---
*Keywords for discovery: Model Context Protocol, MCP Server, AI Agent, Multi-Agent System, Coding Assistant, LangGraph orchestrated agent, Claude tool integration, Cursor AI MCP, Windsurf, coding swarm, autonomous developer.*
