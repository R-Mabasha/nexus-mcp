import logging
from typing import Dict
from litellm import completion
from src.llm.provider import get_llm
from src.nexus.state import SwarmState
from src.nexus.nodes.crew_executor import execute_crew

logger = logging.getLogger(__name__)

def search_external_docs(query: str) -> str:
    """
    Mock implementation of a Context7/Tavily MCP call.
    In a full production environment, this would call the actual MCP tool 
    to retrieve up-to-date SDK documentation.
    """
    logger.info(f"[Web Fetcher] Retrieving live docs for: {query}")
    return f"Live Context from Web Planner: (Assume recent official docs returned for {query})"

def plan_node(state: SwarmState) -> Dict:
    logger.info("[Macro Node] Planning and Fetching Web Docs...")
    model = get_llm()
    
    docs_context = search_external_docs(state.get('task_description', ''))
    
    prompt = (
        f"Create a very brief, high-level approach to solve this task: {state.get('task_description')}\n"
        f"Use the following recently fetched web documentation for accuracy: {docs_context}"
    )
    # LiteLLM routing
    response = completion(model=model, messages=[{"role": "user", "content": prompt}])
    plan = response.choices[0].message.content
    return {"plan": plan, "status": "planning_complete"}

def crew_node(state: SwarmState) -> Dict:
    logger.info("[Macro Node] Dispatching Micro-Orchestrator (Crew)...")
    extended_task = f"Plan: {state.get('plan')}\nTask: {state.get('task_description')}"
    
    if state.get("verification_errors"):
         extended_task += f"\n\nCRITICAL FIX REQUIRED: Previous run failed with:\n{state.get('verification_errors')}"
         
    # Handoff to CrewAI
    result = execute_crew(extended_task, state.get("target_dir"), get_llm())
    return {"crew_result": result, "status": "execution_complete"}

def verify_node(state: SwarmState) -> Dict:
    logger.info("[Macro Node] Verifying the Crew's work...")
    # Mocking standard verification (e.g., test suite).
    # If the Crew output literally contains "FAIL", we flag it and increment retries.
    r_count = state.get("retries", 0)
    
    if "FAIL" in state.get("crew_result", "").upper():
        logger.warning(f"Verification Failed. Retry {r_count + 1}")
        return {
            "verification_errors": "Crew indicated failure or tests failed.", 
            "status": "verification_failed",
            "retries": r_count + 1
        }
    
    logger.info("Verification Passed.")
    return {"verification_errors": "", "status": "verification_passed"}

def escalate_node(state: SwarmState) -> Dict:
    logger.error("[Macro Node] MAX_RETRIES HIT. Escalating to human.")
    final_output = f"Escalation Report: Swarm could not verify changes after {state.get('retries')} attempts.\nLast Result: {state.get('crew_result')}"
    return {"status": "escalated", "crew_result": final_output}
