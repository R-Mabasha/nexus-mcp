# Integrating Swarm MCP with Traditional Extensions (Amazon Q, Copilot, etc.)

This guide explains how to connect your powerful multi-orchestrator Swarm to IDE extensions that do not natively support the Model Context Protocol (MCP) yet.

## 1. The Challenge
Extensions like **Amazon Q**, **GitHub Copilot**, and standard **CodeWhisperer** operate as "Black Box" interfaces. They can read your code, but they don't have a standardized way to talk to external MCP servers like this one.

## 2. Integration Strategies

### Strategy A: The CLI Bridge (Best for Scripting)
Since the Swarm is built in Python, you can trigger it directly from your terminal while these extensions are open.
- **Workflow**:
    1. Ask Amazon Q to explain a problem.
    2. Run `python e2e_mcp_test.py` (or a dedicated CLI wrapper) to let the Swarm execute the actual code changes on a new branch.
    3. Amazon Q will see the new branch/files and help you review the Swarm's work.

### Strategy B: Native MCP Hosts (Cursor, Windsurf, Claude Desktop)
These modern AI tools natively support the `swarm-mcp` server. 
- You simply add this server URL to their settings.
- When you ask them to "delegate" a task, they invoke our Swarm directly.

### Strategy C: Extension-to-Extension Communication
If you are developing a custom extension or using a programmable one (like `Continue.dev`):
- Point their "External Tools" or "Slash Commands" to call our `src/server.py` via standard MCP JSON-RPC.

## 3. Future Roadmap
As more tools adopt the MCP spec, this server will automatically become visible to them. Currently, the most effective way to use this swarm alongside Amazon Q is to treat the swarm as an **Autonomous Backend Service** that handles the heavy lifting, while Amazon Q handles the interactive chat.
