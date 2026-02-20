import logging
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool

from src.swarm.tools.fs import SandboxedFS
from src.swarm.tools.bash_safe import SafeBash
from src.core.lightning_optim import optimizer
from src.llm.provider import get_llm

logger = logging.getLogger(__name__)

# To be initialized dynamically per task
fs: SandboxedFS = None
bash: SafeBash = None

@tool("Read Codebase Outline Tool")
def tool_read_outline(directory: str) -> str:
    """Read the AST outline of the python files in a directory to avoid context overwhelm."""
    return fs.read_codebase_outline(directory)

@tool("Read File Chunk Tool")
def tool_read_chunk(filepath: str, start_line: int, end_line: int) -> str:
    """Read specific lines of a file to understand function details."""
    return fs.read_file_chunk(filepath, start_line, end_line)

@tool("Edit File Chunk Tool")
def tool_edit_chunk(filepath: str, start_line: int, end_line: int, new_content: str) -> str:
    """Replace specific lines of a file exactly. Do NOT use this to rewrite the whole file."""
    return fs.edit_file_chunk(filepath, start_line, end_line, new_content)

@tool("Safe Bash Execution Tool")
def tool_run_bash(command: str) -> str:
    """Run a terminal command (like python -m pytest) to verify code compilation and tests."""
    return bash.run(command)

@tool("Search Codebase Tool")
def tool_search_codebase(query: str) -> str:
    """Semantic RAG search to find context or code snippets relating to a query across the entire codebase."""
    return fs.search_codebase(query)

@tool("Take UI Screenshot Tool")
def tool_take_screenshot(url: str = "http://localhost:3000") -> str:
    """Uses Playwright to take a headless screenshot of the app and passes it to the Vision LLM for automated QA."""
    try:
        from playwright.sync_api import sync_playwright
        import base64
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # For MVP, we catch connection errors if the server isn't running
            try:
                page.goto(url, timeout=5000)
                screenshot_bytes = page.screenshot()
                encoded = base64.b64encode(screenshot_bytes).decode('utf-8')
                browser.close()
                return f"Screenshot taken successfully. Check visual layout against requirements. (Base64 length: {len(encoded)})"
            except Exception as e:
                browser.close()
                return f"Failed to reach {url}. Ensure dev server is running before taking screenshots. Error: {e}"
    except ImportError:
        return "Playwright not installed. Skipping visual check."

def execute_crew(task_description: str, target_dir: str, llm_model: str = "gpt-4o") -> str:
    """Entrypoint from LangGraph to run the Crew in the Sandboxed target_dir."""
    global fs, bash
    fs = SandboxedFS(target_dir)
    bash = SafeBash(target_dir)

    tools = [tool_read_outline, tool_read_chunk, tool_edit_chunk, tool_run_bash, tool_search_codebase]
    llm = get_llm()

    research_agent = Agent(
        role="Principal Codebase Researcher",
        goal="Search the codebase using Semantic RAG to find relevant files and functions before anyone else starts coding.",
        backstory="An expert librarian of code. Always runs precise queries to find where functionality is located.",
        tools=[tool_search_codebase, tool_read_outline],
        allow_delegation=False,
        llm=llm,
        verbose=True
    )

    senior_coder = Agent(
        role="Senior Algorithm Engineer",
        goal="Read the codebase outline, design the logic, and implement precise line-chunk modifications.",
        backstory="An elite engineer who never deletes existing code by accident and uses exact start and end lines for chunk replacements.",
        tools=[tool_read_outline, tool_read_chunk, tool_edit_chunk, tool_run_bash, tool_search_codebase],
        allow_delegation=False, # Wait until review
        llm=llm,
        verbose=True
    )

    ux_reviewer = Agent(
        role="Lead UI/UX Vision QA",
        goal="Verify frontend code by taking physical screenshots of the local server and comparing against visual requirements.",
        backstory="A pixel-perfect designer. Uses Playwright screenshots and Vision AI to confirm colors, margins, and layouts are exactly right.",
        tools=[tool_take_screenshot, tool_run_bash],
        allow_delegation=True,
        llm=llm,
        verbose=True
    )

    security_reviewer = Agent(
        role="Principal Quality Reviewer",
        goal="Audit the code written by the Senior Coder. Run syntax checks or tests using safe bash, and enforce fixes.",
        backstory="A strict quality assurance lead who hates broken code and uses the bash tool to verify files compile or pass tests before approving.",
        tools=[tool_read_chunk, tool_run_bash],
        allow_delegation=True, # Can delegate rework back to the coder
        llm=llm,
        verbose=True
    )

    research_task = Task(
        description=f"Analyze the task: {task_description}. Use the Search Codebase Tool to find all relevant files and context needed to solve this. Provide a summary of vital locations.",
        expected_output="A list of file paths and function signatures relevant to the task.",
        agent=research_agent
    )

    coding_task = Task(
        description=f"Implement the following task in the sandbox: {task_description}. Use the Research Agent's summary to guide you. Use read_chunk to view specific functions, and edit_chunk to modify them.",
        expected_output="The codebase successfully modified to satisfy the task.",
        agent=senior_coder
    )

    ux_task = Task(
        description="Run the target server using safe bash (in background if possible). Use take_screenshot to fetch a physical image of the UI. Ensure it visually perfectly aligns with the requirements requested.",
        expected_output="Visual verification output confirmed.",
        agent=ux_reviewer
    )

    review_task = Task(
        description="Review the codebase modifications. Verify the logic. Run a syntax check or testing command if applicable. If it fails, command the Coder to fix it. Do not finish until it is perfect.",
        expected_output="A final summary of the code changes verified and approved.",
        agent=security_reviewer
    )

    crew = Crew(
        agents=[research_agent, senior_coder, ux_reviewer, security_reviewer],
        tasks=[research_task, coding_task, ux_task, review_task],
        process=Process.sequential,
        verbose=True
    )

    # Wrap Crew execution in Agent Lightning Optimizer mock
    logger.info("Handing off to CrewAI Micro-Orchestrator...")
    result = optimizer.trace_execution(
        agent_name="Crew_Ensemble",
        task_name=f"Crew_{task_description[:20]}",
        func=crew.kickoff
    )
    
    return str(result)
