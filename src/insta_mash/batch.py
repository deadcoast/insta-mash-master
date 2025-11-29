"""
Batch mode functionality for insta-mash.

Handles parsing and processing of batch files containing multiple URLs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from insta_mash.config import Config, DownloadOptions


@dataclass
class ValidationError:
    """A validation error for a batch entry."""

    line_number: int
    message: str
    entry: Optional[BatchEntry] = None


@dataclass
class BatchEntry:
    """A single entry in a batch file."""

    line_number: int
    url: str
    preset: str = ""
    profile: str = ""

    @classmethod
    def parse(cls, line: str, line_number: int) -> Optional[BatchEntry]:
        """
        Parse a line from batch file into BatchEntry.

        Args:
            line: The line to parse
            line_number: Line number in the file (1-indexed)

        Returns:
            BatchEntry if valid, None if line should be skipped (comment/empty)
        """
        # Strip whitespace
        line = line.strip()

        # Skip empty lines
        if not line:
            return None

        # Skip comments
        if line.startswith("#"):
            return None

        # Split into tokens
        tokens = line.split()

        # First token must be URL
        url = tokens[0]

        # Parse optional configuration
        preset = ""
        profile = ""

        for token in tokens[1:]:
            if ":" in token:
                key, value = token.split(":", 1)
                if key == "preset":
                    preset = value
                elif key == "profile":
                    profile = value

        return cls(
            line_number=line_number,
            url=url,
            preset=preset,
            profile=profile,
        )

    def resolve_options(
        self,
        config: Config,
        global_options: Optional[DownloadOptions] = None,
    ) -> DownloadOptions:
        """
        Resolve final options for this batch entry.

        Merges configuration in priority order:
        1. Config defaults (lowest priority)
        2. Global batch options
        3. Profile options (if specified)
        4. Preset options (if specified, highest priority)

        Args:
            config: The configuration object
            global_options: Optional global batch settings to merge

        Returns:
            Resolved DownloadOptions for this entry
        """
        from insta_mash.config import DownloadOptions

        # Start with config defaults
        options = DownloadOptions()
        options = options.merge(config.defaults)

        # Apply global batch options
        if global_options:
            options = options.merge(global_options)

        # Apply profile if specified
        if self.profile:
            profile = config.get_profile(self.profile)
            if profile:
                options = options.merge(profile.options)

        # Apply preset if specified
        if self.preset:
            from insta_mash.config import PRESETS
            if self.preset in PRESETS:
                preset = PRESETS[self.preset]
                _, preset_opts = preset.apply()
                options = options.merge(preset_opts)

        return options


@dataclass
class BatchFile:
    """Parsed batch file with all entries."""

    path: Path
    entries: list[BatchEntry]

    @classmethod
    def load(cls, path: Path) -> BatchFile:
        """
        Load and parse a batch file.

        Args:
            path: Path to the batch file

        Returns:
            BatchFile with parsed entries

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        if not path.exists():
            raise FileNotFoundError(f"Batch file not found: {path}")

        entries = []

        with open(path, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                entry = BatchEntry.parse(line, line_number)
                if entry is not None:
                    entries.append(entry)

        return cls(path=path, entries=entries)

    def validate(self, config: Config) -> list[ValidationError]:
        """
        Validate all entries in the batch file.

        Checks for:
        - Syntax errors (already handled by parse, but we track invalid lines)
        - Non-existent preset references
        - Non-existent profile references

        Args:
            config: The configuration object to validate against

        Returns:
            List of validation errors (empty if all valid)
        """
        from insta_mash.config import PRESETS

        errors = []

        # Re-parse the file to catch syntax errors
        with open(self.path, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                stripped = line.strip()
                
                # Skip comments and empty lines
                if not stripped or stripped.startswith("#"):
                    continue
                
                # Try to parse
                entry = BatchEntry.parse(line, line_number)
                
                # If parse returned None for a non-comment/non-empty line, it's invalid
                # (This shouldn't happen with current implementation, but future-proof)
                if entry is None:
                    errors.append(ValidationError(
                        line_number=line_number,
                        message="Invalid syntax",
                    ))
                    continue
                
                # Check preset reference
                if entry.preset and entry.preset not in PRESETS:
                    errors.append(ValidationError(
                        line_number=line_number,
                        message=f"Unknown preset: {entry.preset}",
                        entry=entry,
                    ))
                
                # Check profile reference
                if entry.profile and entry.profile not in config.profiles:
                    errors.append(ValidationError(
                        line_number=line_number,
                        message=f"Unknown profile: {entry.profile}",
                        entry=entry,
                    ))

        return errors


@dataclass
class BatchProgress:
    """Tracks batch execution progress."""

    total: int
    completed: int = 0
    succeeded: int = 0
    failed: int = 0
    current_url: str = ""
    errors: list[tuple[str, str]] = field(default_factory=list)  # (url, error_message)

    def update(self, success: bool, url: str = "", error: str = "") -> None:
        """
        Update progress after completing a download.

        Args:
            success: Whether the download succeeded
            url: The URL that was processed
            error: Error message if the download failed
        """
        self.completed += 1
        if success:
            self.succeeded += 1
        else:
            self.failed += 1
            if url and error:
                self.errors.append((url, error))

    def set_current_url(self, url: str) -> None:
        """
        Set the current URL being processed.

        Args:
            url: The URL currently being processed
        """
        self.current_url = url

    def display(self) -> str:
        """
        Display current progress to console.

        Returns:
            Formatted progress string
        """
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text

        console = Console()
        
        # Build progress text
        progress_text = Text()
        progress_text.append(f"Progress: {self.completed}/{self.total}\n", style="bold cyan")
        progress_text.append(f"✓ Succeeded: {self.succeeded}  ", style="green")
        progress_text.append(f"✗ Failed: {self.failed}\n", style="red")
        
        if self.current_url:
            progress_text.append(f"\nCurrent: {self.current_url}", style="yellow")
        
        # Create panel
        panel = Panel(progress_text, title="Batch Progress", border_style="blue")
        
        # Render to string
        with console.capture() as capture:
            console.print(panel)
        
        return capture.get()

    def get_final_report(self) -> str:
        """
        Generate final report after batch completion.

        Returns:
            Formatted final report string
        """
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        console = Console()
        
        # Build summary
        summary = Text()
        summary.append("Batch Complete!\n\n", style="bold green")
        summary.append(f"Total: {self.total}\n", style="bold")
        summary.append(f"✓ Succeeded: {self.succeeded}\n", style="green")
        summary.append(f"✗ Failed: {self.failed}\n", style="red")
        
        # Add error details if any
        if self.errors:
            summary.append("\nErrors:\n", style="bold red")
            for url, error in self.errors:
                summary.append(f"  • {url}\n", style="yellow")
                summary.append(f"    {error}\n", style="dim")
        
        # Create panel
        panel = Panel(summary, title="Final Report", border_style="green" if self.failed == 0 else "red")
        
        # Render to string
        with console.capture() as capture:
            console.print(panel)
        
        return capture.get()


@dataclass
class ResumeState:
    """State for resuming interrupted batch operations."""

    batch_file_path: Path
    completed_indices: set[int]
    timestamp: datetime

    def save(self, path: Path) -> None:
        """
        Save resume state to file.

        Args:
            path: Path where the resume state should be saved
        """
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to JSON-serializable format
        data = {
            "batch_file_path": str(self.batch_file_path),
            "completed_indices": sorted(list(self.completed_indices)),
            "timestamp": self.timestamp.isoformat(),
        }

        # Write to file
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: Path) -> Optional[ResumeState]:
        """
        Load resume state from file.

        Args:
            path: Path to the resume state file

        Returns:
            ResumeState if file exists and is valid, None otherwise
        """
        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return cls(
                batch_file_path=Path(data["batch_file_path"]),
                completed_indices=set(data["completed_indices"]),
                timestamp=datetime.fromisoformat(data["timestamp"]),
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            # Invalid resume file
            return None


class BatchExecutor:
    """Executes batch downloads with progress tracking."""

    def __init__(
        self,
        batch_file: BatchFile,
        config: Config,
        delay: float = 0.0,
        dry_run: bool = False,
        resume_state: Optional[ResumeState] = None,
    ):
        """
        Initialize batch executor.

        Args:
            batch_file: The batch file to execute
            config: Configuration object
            delay: Delay in seconds between downloads
            dry_run: If True, simulate without downloading
            resume_state: Optional resume state to skip completed entries
        """
        self.batch_file = batch_file
        self.config = config
        self.delay = delay
        self.dry_run = dry_run
        self.resume_state = resume_state
        self.progress = BatchProgress(total=len(batch_file.entries))

    def execute(self) -> BatchProgress:
        """
        Execute all downloads in batch.

        Returns:
            BatchProgress object with final results
        """
        import subprocess
        import time
        from rich.console import Console

        console = Console()

        for index, entry in enumerate(self.batch_file.entries):
            # Skip if already completed (resume functionality)
            if self.resume_state and index in self.resume_state.completed_indices:
                continue

            # Set current URL in progress
            self.progress.set_current_url(entry.url)

            # Display progress
            console.print(self.progress.display())

            # Execute the entry
            success, error_msg = self.execute_entry(entry)

            # Update progress
            self.progress.update(success=success, url=entry.url, error=error_msg if not success else "")

            # Apply delay between downloads (except after last one)
            if self.delay > 0 and index < len(self.batch_file.entries) - 1:
                time.sleep(self.delay)

        return self.progress

    def execute_entry(self, entry: BatchEntry) -> tuple[bool, str]:
        """
        Execute a single batch entry.

        Args:
            entry: The batch entry to execute

        Returns:
            Tuple of (success, error_message). error_message is empty string if successful.
        """
        import subprocess
        import os
        from rich.console import Console

        console = Console()

        try:
            # Resolve options for this entry
            options = entry.resolve_options(self.config)

            # Build gallery-dl command
            cmd = ["gallery-dl"]
            cmd.extend(options.to_gallery_dl_args())

            if self.dry_run:
                cmd.append("-s")

            cmd.append(entry.url)

            # Create destination directory if not dry-run
            if options.destination and not self.dry_run:
                Path(os.path.expanduser(options.destination)).mkdir(parents=True, exist_ok=True)

            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per download
            )

            if result.returncode != 0:
                # Log error
                error_msg = result.stderr.strip() if result.stderr else f"Exit code {result.returncode}"
                console.print(f"[red]Error downloading {entry.url}:[/red] {error_msg}")
                return False, error_msg

            return True, ""

        except subprocess.TimeoutExpired:
            error_msg = "Download timed out after 5 minutes"
            console.print(f"[red]Error downloading {entry.url}:[/red] {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = str(e)
            console.print(f"[red]Error downloading {entry.url}:[/red] {error_msg}")
            return False, error_msg
