import subprocess
import logging

logger = logging.getLogger(__name__)

class SafeBash:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def run(self, cmd: str, timeout: int = 30) -> str:
        """
        Runs a terminal command in the sandboxed root directory.
        If the output exceeds 500 lines, it truncates the middle to preserve context window limits.
        """
        try:
            result = subprocess.run(
                cmd,
                cwd=self.root_dir,
                shell=True,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output = result.stdout + "\n" + result.stderr
            lines = output.splitlines()
            
            # Truncation logic to prevent context overwhelm
            if len(lines) > 500:
                head = lines[:200]
                tail = lines[-300:]
                return "\n".join(head + ["\n... [TRUNCATED 500+ LINES - OUTPUT TOO LARGE] ...\n"] + tail)
            
            return "\n".join(lines)
            
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds."
        except Exception as e:
            logger.error(f"Safe Bash failed: {e}")
            return str(e)
