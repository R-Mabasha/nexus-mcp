from src.swarm.graph import build_graph
import logging

logging.basicConfig(level=logging.INFO)
print("Initializing Architecture Test...")

try:
    g = build_graph()
    print("Graph built successfully without topology errors!")
    
    # Optional: test basic syntax loading
    from src.llm.provider import get_llm
    from src.core.git_sandbox import GitSandbox
    print("Imports resolved successfully.")
except Exception as e:
    print(f"FAILED TO BUILD GRAPH OR RESOLVE IMPORTS: {e}")
