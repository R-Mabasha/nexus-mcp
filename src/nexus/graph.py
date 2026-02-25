from langgraph.graph import StateGraph, START, END
from src.nexus.state import SwarmState
from src.nexus.nodes.macro import plan_node, crew_node, verify_node, escalate_node

MAX_RETRIES = 3

def verify_router(state: SwarmState) -> str:
    """Routing logic after Verification."""
    if state.get("status") == "verification_passed":
        return END
        
    if state.get("retries", 0) >= MAX_RETRIES:
        return "escalate"
        
    return "crew" # Loop back to fix

def build_graph():
    """
    Compiles the Swarm into an executable structure.
    """
    workflow = StateGraph(SwarmState)

    # Define nodes
    workflow.add_node("plan", plan_node)
    workflow.add_node("crew", crew_node)
    workflow.add_node("verify", verify_node)
    workflow.add_node("escalate", escalate_node)

    # Define edges (The loops)
    workflow.add_edge(START, "plan")
    workflow.add_edge("plan", "crew")
    workflow.add_edge("crew", "verify")
    
    # Conditional edge enforcing our Circuit Breaker algorithm
    workflow.add_conditional_edges("verify", verify_router, {
        "crew": "crew",
        "escalate": "escalate",
        END: END
    })
    
    workflow.add_edge("escalate", END)

    return workflow.compile()
