import os
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class GitSandbox:
    """
    Ensures that the Swarm never edits the user's active working branch
    by forcing a git checkout into a temporary nexus feature branch.
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

    def enter_sandbox(self, task_id: str, isolate: bool = True) -> str:
        """
        If isolate=True (default), creates and pushes the Nexus to an isolated branch.
        If isolate=False, applies changes directly to the current branch.
        Returns the name of the active branch.
        """
        current_branch = self.run_cmd(["git", "branch", "--show-current"])
        
        if not isolate:
            logger.info(f"Direct Mode enabled. Nexus will operate on the current branch: {current_branch}")
            return current_branch

        branch_name = f"nexus-feature-{task_id}"
        
        # Verify it's a git repo
        if not (self.target_dir / ".git").exists():
             raise ValueError("The target directory is not a Git repository. To protect your file system, the Nexus MCP requires Git initialized projects.")

        logger.info(f"Host IDE is on branch: {current_branch}")
        try:
            # Stash any current uncommitted work to prevent bleeding into the nexus branch
            self.run_cmd(["git", "stash"])
        except Exception as e:
            logger.warning(f"Git stash threw a warning/error (often safe if nothing to stash): {e}")

        try:
            # Check if branch exists reliably
            branches_raw = self.run_cmd(["git", "branch"])
            existing_branches = [b.strip().replace("* ", "") for b in branches_raw.split("\n") if b.strip()]
            
            if branch_name in existing_branches:
                 self.run_cmd(["git", "checkout", branch_name])
                 logger.info(f"Nexus resumed on existing branch: {branch_name}")
            else:
                 self.run_cmd(["git", "checkout", "-b", branch_name])
                 logger.info(f"Nexus successfully isolated to branch: {branch_name}")
            return branch_name
        except Exception as e:
            logger.error(f"Failed to isolate or resume branch: {e}")
            return current_branch
            
    def prepare_pr_handoff(self) -> str:
        """
        Gathers the diff of what the nexus achieved to send back to the MCP Client
        """
        diff = self.run_cmd(["git", "diff", "HEAD"])
        return diff
