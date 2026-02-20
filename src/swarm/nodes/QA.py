from src.llm.provider import generate_swarm_response
from src.swarm.state import SwarmState
from src.swarm.tools.fs import SandboxedFS

def qa_node(state: SwarmState) -> dict:
    """
    The Reviewer Agent.
    Validates what the coder executed.
    """
    plan = state.get("execution_plan", [])
    current_index = state.get("current_step", 0)
    
    if current_index >= len(plan):
        return {} # Exit condition
    
    fs = SandboxedFS(state["target_directory"])
    files_tree = fs.list_files()
    
    system_prompt = (
        "You are the Swarm Quality Assurance Agent. You must review the current state of "
        "the user's workspace map to determine if the task was completed successfully. "
        "Respond strictly with 'PASS' or 'FAIL'. Providing any other output causes a crash."
    )
    
    user_prompt = f"Workspace Tree:\n{files_tree}\n\nTask requirement: {plan[current_index]}"
    
    response = generate_swarm_response(system_prompt, user_prompt)
    
    if "FAIL" in response.upper():
        return {
            "revision_count": state.get("revision_count", 0) + 1,
            "messages": ["QA failed the execution. Sending back to Coder."]
        }
    
    return {
        "current_step": current_index + 1,
        "messages": ["QA passed the execution. Moving to next task step."]
    }
