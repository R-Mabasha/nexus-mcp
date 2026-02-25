import json
from src.llm.provider import generate_swarm_response
from src.nexus.state import SwarmState

def planner_node(state: SwarmState) -> dict:
    """
    The Architect Agent.
    Receives the raw prompt and returns a JSON array of specific filesystem tasks.
    """
    system_prompt = (
        "You are the Swarm Architect. Your job is to break down the user's objective "
        "into a series of concrete steps. "
        "Return ONLY a raw JSON array of strings representing the steps. "
        "Do not use markdown blocks. Just the array."
    )
    
    user_prompt = f"Objective: {state['task_description']}\n\nBreak this down into 1-3 concrete implementation steps."
    
    response = generate_swarm_response(system_prompt, user_prompt)
    
    try:
        # Standardize the LLM output into an actual python array
        plan = json.loads(response)
        if not isinstance(plan, list):
            plan = [response]
    except json.JSONDecodeError:
        plan = [response] # fallback if the LLM messes up the JSON
        
    return {
        "execution_plan": plan,
        "current_step": 0,
        "revision_count": 0,
        "messages": [f"Planner created {len(plan)} tasks."]
    }
