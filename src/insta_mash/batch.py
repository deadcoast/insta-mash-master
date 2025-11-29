"""
Batch mode functionality for insta-mash.

Handles parsing and processing of batch files containing multiple URLs.
"""

from __future__ import annotations

from dataclasses import dataclass
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
