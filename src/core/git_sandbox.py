import os
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class GitSandbox:
    """
    Ensures that the Swarm never edits the user's active working branch
    by forcing a git checkout into a temporary swarm feature branch.
    """
    def __init__(self, target_dir: str):
        self.target_dir = Path(target_dir).resolve()
        if not self.target_dir.exists() or not self.target_dir.is_dir():
            raise ValueError(f"Target directory {self.target_dir} does not exist.")
            
    def run_cmd(self, cmd: list[str]) -> str:
        """Run a subprocess command inside the target directory."""
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.target_dir),
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Git Sandbox Command Failed: {cmd} -> {e.stderr}")
            raise RuntimeError(f"Git constraint error: {e.stderr}")

    def enter_sandbox(self, task_id: str) -> str:
        """
        Creates and pushes the Swarm to an isolated branch.
        Returns the name of the new branch.
        """
        branch_name = f"swarm-feature-{task_id}"
        
        # Verify it's a git repo
        if not (self.target_dir / ".git").exists():
             raise ValueError("The target directory is not a Git repository. To protect your file system, the Swarm MCP requires Git initialized projects.")

        current_branch = self.run_cmd(["git", "branch", "--show-current"])
        logger.info(f"Host IDE is on branch: {current_branch}")
        try:
            # Stash any current uncommitted work to prevent bleeding into the swarm branch
            self.run_cmd(["git", "stash"])
        except Exception as e:
            logger.warning(f"Git stash threw a warning/error (often safe if nothing to stash): {e}")

        try:
            # Try to create a new branch based on the current state
            self.run_cmd(["git", "checkout", "-b", branch_name])
            logger.info(f"Swarm successfully isolated to branch: {branch_name}")
            return branch_name
        except RuntimeError:
            # If the branch already exists, just check it out
            self.run_cmd(["git", "checkout", branch_name])
            logger.info(f"Swarm resumed on existing branch: {branch_name}")
            return branch_name
            
    def prepare_pr_handoff(self) -> str:
        """
        Gathers the diff of what the swarm achieved to send back to the MCP Client
        """
        diff = self.run_cmd(["git", "diff", "HEAD"])
        return diff
