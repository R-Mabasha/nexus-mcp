import asyncio
import os
import sys

# Ensure project modules are importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.server import call_tool
from src.core.lightning_optim import optimizer

async def run_e2e_test():
    print("========================================")
    print("🚀 INITIALIZING E2E MCP SWARM TEST")
    print("========================================")
    
    # Mocking the MCP Client tool request
    tool_name = "delegate_to_lightning_crew"
    arguments = {
        "task": "Analyze the codebase components inside src/core and src/swarm. Pay attention to how getting the LLM inside provider connects to Groq using litellm. Write a full 'ARCHITECTURE.md' file at the root tracking these metrics.",
        "target_dir": "C:/Multi-agent-orchestation",
        "task_id": "codebase-documentation-direct",
        "isolate": False
    }
    
    print(f"\n[Client] Sending Tool Request: {tool_name}")
    print(f"[Client] Arguments: {arguments}\n")
    
    try:
        # Trigger the actual MCP exposed function
        results = await call_tool(name=tool_name, arguments=arguments)
        
        print("\n========================================")
        print("✅ E2E TEST COMPLETED SUCCESSFULLY")
        print("========================================")
        
        # Print the final message payload the IDE would receive
        if results and len(results) > 0:
            print("\n--- IDE LLM Context Received ---")
            print(results[0].text)
            print("--------------------------------\n")
        else:
            print("[Warning] No TextContent returned from the tool.")
            
    except Exception as e:
        print("\n========================================")
        print("❌ E2E TEST CRASHED")
        print("========================================")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_e2e_test())
