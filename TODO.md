# Swarm MCP: Implementation TODOs

We have the entire architectural foundation built locally. Here is exactly how we are going to implement the final steps to make this production-ready:

### 1. Finalizing Environment & Testing
*   **What**: The `uv pip install` needs to finish pulling down the massive dependencies.
*   **How**: Wait for `mcp`, `langgraph`, and `crewai` wheels to complete. Once finished, run `python test_graph.py` to ensure the Macro and Micro Orchestrators fire up successfully without import errors.

### 2. Client Ide Integration
*   **What**: Hook the Swarm up to Cursor or Windsurf.
*   **How**: In the IDE's MCP Configuration, add the exact path to this repository:
    ```json
    "swarm-mcp": {
        "command": "python",
        "args": ["-m", "src.index"],
        "cwd": "C:/Multi-agent-orchestation"
    }
    ```

### 3. Dockerizing the `SafeBash` Verifier
*   **What**: Right now, `bash_safe.py` truncates outputs, but it still executes raw on the host machine (inside the Git sandbox). Top-tier developers use Docker for running agent-generated scripts.
*   **How**: Modify `SafeBash.run()` to spin up a lightweight, ephemeral python slim container mapped only to the Git sandbox branch, and execute `pytest` or `npm run build` there instead of `subprocess.run(shell=True)`.

### 4. Telemetry with Remote Agent Lightning
*   **What**: Right now, `lightning_optim.py` logs traces locally to `traces=[]`.
*   **How**: Hook the `_record_trace` method into the actual Agent Lightning cloud or OpenTelemetry endpoints so we can view graph execution waterfalls on a dashboard.

### ~~5. Elite Feature: Semantic Code Search (RAG)~~ (DONE)
*   Integrate ChromaDB or an MCP Search API. Create a `search_codebase` tool for the CrewAI agents.

### ~~6. Elite Feature: Visual QA (Playwright + Vision)~~ (DONE)
*   Ensure frontend code looks physically correct, not just syntactically correct.
*   Give the `QA Reviewer` agent a tool that spins up the dev server, takes a screenshot of `localhost`, and uses `gpt-4o` vision to verify UI bounds against the user prompt.

### ~~7. Elite Feature: Live CI/CD Automation~~ (DONE)
*   Add a GitHub tool to the `escalate_node` that automatically pushes the `swarm-task-xyz` branch and opens a Pull Request automatically.
