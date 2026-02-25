import logging
import json
from litellm import completion
from src.swarm.tools.fs import SandboxedFS
from src.swarm.tools.bash_safe import SafeBash
from src.core.lightning_optim import optimizer
from src.llm.provider import get_llm

logger = logging.getLogger(__name__)

def execute_crew(task_description: str, target_dir: str, llm_model: str = "gpt-4o") -> str:
    """Entrypoint from LangGraph to run the micro-swarm purely via explicit Litellm loops (CrewAI-free)."""
    fs = SandboxedFS(target_dir)
    bash = SafeBash(target_dir)
    llm = get_llm()

    logger.info("Handing off to Native LangGraph Micro-Orchestrator...")

    # Define minimal tools for LiteLLM
    tools = [
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Writes content explicitly to a file in the sandbox.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "Name of the file, e.g. hello_world.py"},
                        "content": {"type": "string", "description": "The exact script or text to write"}
                    },
                    "required": ["filepath", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "run_bash",
                "description": "Runs a terminal command (like python -m pytest) to verify code compilation and tests.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Bash command, like python test.py"}
                    },
                    "required": ["command"]
                }
            }
        }
    ]

    messages = [
        {"role": "system", "content": "You are the Senior Coder Agent. Your job is to analyze the user's task and immediately use the 'write_file' tool to fulfill the request. Be precise. You may then use 'run_bash' to test it."},
        {"role": "user", "content": task_description}
    ]

    # Optimization wrapper for tracking telemetry
    def native_llm_execution():
        response = completion(
            model=llm,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        # Actually wire the tool call routing
        if hasattr(message, 'tool_calls') and message.tool_calls:
            results = []
            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                if fn_name == "write_file":
                    logger.info(f"[Agent] Executing write_file on {args['filepath']}")
                    r = fs.write_file(args['filepath'], args['content'])
                    results.append(r)
                elif fn_name == "run_bash":
                    logger.info(f"[Agent] Executing run_bash on {args['command']}")
                    r = bash.run(args['command'])
                    results.append(r)
                    
            return f"Agent successfully called tools. Results: {'; '.join(results)}"
        else:
            return f"Agent responded without making tool calls: {message.content}"

    result = optimizer.trace_execution(
        agent_name="Native_Litellm_Agent",
        task_name=f"Litellm_{task_description[:20]}",
        func=native_llm_execution
    )
    
    return str(result)
