from src.llm.provider import generate_swarm_response
from src.swarm.state import SwarmState
from src.swarm.tools.fs import SandboxedFS

def coder_node(state: SwarmState) -> dict:
    """
    The Execution Agent. 
    Retrieves the current task from the plan and attempts to write the code natively.
    """
    current_index = state.get("current_step", 0)
    plan = state.get("execution_plan", [])
    
    if current_index >= len(plan):
        return {"messages": ["Coder has no more tasks to execute."]}
        
    active_task = plan[current_index]
    
    system_prompt = (
        "You are the Swarm Execution Agent. You have been assigned a coding task. "
        "Because this is a prototype, output your response as a simple proposed file change in this format:\n"
        "FILE: path/to/file.py\nCONTENT:\nprint('hello')\nEND"
    )
    
    user_prompt = f"Task: {active_task}\nPlease provide the code."
    
    response = generate_swarm_response(system_prompt, user_prompt)
    
    # Very basic parsing for the prototype wrapper
    try:
        if "FILE: " in response and "CONTENT:" in response:
            filepath = response.split("FILE: ")[1].split("\n")[0].strip()
            content = response.split("CONTENT:\n")[1].split("\nEND")[0].strip()
            
            # Execute on the sandboxed file system!
            fs = SandboxedFS(state["target_directory"])
            fs_result = fs.write_file(filepath, content)
            
            return {
                "messages": [f"Coder modified {filepath}: {fs_result}"]
            }
    except Exception as e:
        pass
        
    return {"messages": [f"Coder attempted task but failed to parse output: {response[:50]}..."]}
