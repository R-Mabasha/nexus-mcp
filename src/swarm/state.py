from typing import TypedDict, Annotated

class SwarmState(TypedDict):
    """
    The rigid state schema passed between macro-nodes in LangGraph.
    Tracks the overarching objective, orchestrates the micro-crew, and 
    enforces circuit-breaking retry limits.
    """
    task_description: str
    target_dir: str
    plan: str
    crew_result: str
    verification_errors: str
    retries: int
    status: str
