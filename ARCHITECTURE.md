# Swarm MCP: Technical Architecture & Development Path

## 1. Project Overview
**Location:** `c:\Multi-agent-orchestation`
**Goal:** Build a Python-based MCP Server that orchestrates a multi-agent Swarm via LangGraph, optimized via Agent Lightning, and isolated via Git Worktrees.

## 2. Directory Structure Roadmap
We will strictly follow this architecture to separate concerns.

```text
C:\Multi-agent-orchestation\
├── .env                    # User's API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY)
├── pyproject.toml          # Uv / Poetry package definitions
├── README.md               # User guide for connecting IDEs
├── src/
│   ├── index.py            # Entry point (FastAPI or StdIO MCP wrapper)
│   ├── server.py           # The MCP Tool Definitions (`delegate_to_swarm`)
│   │
│   ├── core/               # System Boundaries
│   │   ├── git_sandbox.py  # Branch isolation & PR handoff logic
│   │   ├── config.py       # Pydantic env validation
│   │   └── logger.py       # Debugging & Tracing config
│   │
│   ├── swarm/              # LangGraph Orchestration
│   │   ├── graph.py        # The cyclical state machine topology
│   │   ├── state.py        # TypedDict definitions for graph state
│   │   │
│   │   ├── nodes/          # The specific Agent functions
│   │   │   ├── planner.py  # Architect Agent
│   │   │   ├── coder.py    # Execution Agent
│   │   │   └── QA.py       # Reviewer Agent
│   │   │
│   │   └── tools/          # Tools available *to* the Swarm internally
│   │       ├── fs.py       # Sandboxed local file reading/writing
│   │       └── bash.py     # Subprocess execution (linting/testing)
│   │
│   └── llm/                # Model Routing
│       └── provider.py     # LiteLLM wrapper for provider-agnostic bridging
```

## 3. Data Flow & Security Constraints

The application must operate linearly under the strict Git Sandbox requirement:
1. **Invocation:** IDE calls `delegate_to_swarm(task="build login", target_dir="C:/app")`
2. **Quarantine Phase:** `src/core/git_sandbox.py` runs. 
   - Uses `cd C:/app`
   - Executes `git checkout -b swarm-task-1234`
   - Maps the isolated directory into LangGraph state.
3. **Planning Phase:** `planner.py` uses LiteLLM to break the task into discrete `fs` operations.
4. **Execution Phase:** `coder.py` invokes `fs.py`. `fs.py` validates absolute paths to ensure it never navigates `../` outside of the Git repo.
5. **Optimization Phase:** `agentlightning` records traces of `coder.py` outputs.
6. **Handoff Phase:** MCP returns success string to IDE: `"Task complete on branch 'swarm-task-1234'. Please diff and merge."`

## 4. Execution Backlog (Step-by-Step)
This is our strict development roadmap. We will not deviate or skip steps to prevent hallucination.

*   [ ] **Phase 1: Environment Setup** 
    *   Initialize `pyproject.toml` with `uv`
    *   Install `mcp`, `langgraph`, `litellm`, `pydantic`, `agentlightning` (if compatible)
*   [ ] **Phase 2: Core Isolation Logic**
    *   Implement `src/core/git_sandbox.py` (Must prove we can branch safely)
    *   Implement `src/swarm/tools/fs.py` (Must prove path traversal blocking)
*   [ ] **Phase 3: The Model Router**
    *   Implement `src/llm/provider.py` using `litellm` to test simple API connectivity.
*   [ ] **Phase 4: The Graph Topology**
    *   Implement `planner.py`, `coder.py`, and `QA.py`
    *   Wire them together in `graph.py`
*   [ ] **Phase 5: The MCP Wrapper**
    *   Implement `src/server.py` to wrap the Graph into an MCP `mcp.tool()`
    *   Test by linking it to standard `mcp_config.json`
