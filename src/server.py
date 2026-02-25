from mcp.server import Server
import mcp.types as types
from typing import Any

from src.core.git_sandbox import GitSandbox
from src.swarm.graph import build_graph

import logging
logger = logging.getLogger(__name__)

server = Server("lightning-crew-mcp")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="delegate_to_lightning_crew",
            description="DELEGATE TASK: Use this tool to send a complex coding task to an autonomous agent swarm. By default, it isolates changes to a safe Git branch. Set 'isolate=False' to apply changes directly to the current branch/main.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "The complex task description."},
                    "target_dir": {"type": "string", "description": "Absolute path to the project root."},
                    "task_id": {"type": "string", "description": "Unique slug for the task."},
                    "isolate": {"type": "boolean", "description": "Defaults to True. If False, modifications happen directly on the active branch without stashing.", "default": True}
                },
                "required": ["task", "target_dir", "task_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    if name != "delegate_to_lightning_crew":
        raise ValueError(f"Tool {name} not found")

    task = arguments["task"]
    target_dir = arguments["target_dir"]
    task_id = arguments["task_id"]
    isolate = arguments.get("isolate", True)
    
    logger.info(f"Received Delegation for Task: {task_id} (Isolate: {isolate})")
    
    # 1. Absolute Isolation (Optional)
    sandbox = GitSandbox(target_dir)
    branch = sandbox.enter_sandbox(task_id, isolate=isolate)
    
    # 2. Multi-Orchestrator Invocation
    graph = build_graph()
    initial_state = {
        "task_description": task,
        "target_dir": target_dir,
        "retries": 0,
        "status": "started",
        "plan": "",
        "crew_result": "",
        "verification_errors": ""
    }
    
    logger.info("Executing Macro-Orchestrator...")
    final_state = graph.invoke(initial_state)
    logger.info(f"Macro-Orchestrator finished with status: {final_state.get('status')}")
    
    # 3. Pull Handoff
    try:
        diff = sandbox.prepare_pr_handoff()
        if not diff:
            diff = "No codebase changes detected upon verification."
            
        pr_link = "No GITHUB_TOKEN or GITHUB_REPO env var found. Skipped Auto-PR."
        import os
        github_token = os.getenv("GITHUB_TOKEN")
        repo_name = os.getenv("GITHUB_REPO")
        if github_token and repo_name:
            try:
                from github import Github, Auth
                import subprocess
                subprocess.run(["git", "push", "-u", "origin", branch], cwd=target_dir)
                auth = Auth.Token(github_token)
                g = Github(auth=auth)
                repo = g.get_repo(repo_name)
                pr = repo.create_pull(
                    title=f"[Lightning-Crew] Auto-PR: {task_id}", 
                    body=f"Automated PR from Swarm.\nStatus: {final_state.get('status')}", 
                    head=branch, 
                    base="main", 
                    draft=True
                )
                pr_link = f"✅ Draft Pull Request Created Automatically! {pr.html_url}"
            except Exception as e:
                pr_link = f"Attempted to create PR but failed: {e}"
                
    except Exception as e:
        diff = f"Failed to retrieve git diff: {e}"
        pr_link = "Skipped PR creation due to diff failure."
        
    final_status = final_state.get('status')
    escalation_notes = final_state.get('verification_errors', '')
    
    message = (
        f"Task Complete. Swarm cleanly isolated to branch: '{branch}'.\n\n"
        f"Final Architecture Status: {final_status}\n"
        f"Escalation Notes / Errors: {escalation_notes}\n\n"
        f"--- GitHub DevOps Automation ---\n{pr_link}\n\n"
        f"--- Resulting Git Diff ---\n{diff}\n"
        f"\n(Please review the diff. Then, run `git merge {branch}` if satisfied.)"
    )
    
    return [types.TextContent(type="text", text=message)]
