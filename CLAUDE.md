# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

insta-mash is an interactive CLI wrapper around gallery-dl that provides a menu-driven interface for downloading media from Instagram and other platforms. It abstracts away gallery-dl's complexity with presets, profiles, and persistent configuration.

## Development Commands

### Setup
```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --all-extras
```

### Running the CLI
```bash
# Run interactive mode (main entry point)
uv run mash

# Run specific commands
uv run mash grab <url>
uv run mash config show
uv run mash preset instagram username
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage report
uv run pytest -v --cov=insta_mash --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_config.py

# Run specific test
uv run pytest tests/test_config.py::TestConfig::test_resolve_options_priority
```

### Code Quality
```bash
# Run linter
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Run type checker
uv run mypy src/insta_mash
```

## Architecture

### Module Structure

The codebase has four main modules under `src/insta_mash/`:

1. **`config.py`** - Configuration system (largest module ~630 lines)
   - `DownloadOptions`: Dataclass representing all gallery-dl options
   - `Config`: Main config container with defaults and profiles
   - `Profile`: Named configuration that can inherit from other profiles
   - `Preset`: Built-in platform-specific configurations (Instagram, Twitter, etc.)
   - `PRESETS`: Dictionary of 8 built-in presets
   - Path helpers: `get_config_dir()`, `get_config_path()`, `get_data_dir()`
   - Validation: `validate_options()` checks format of sleep, rate_limit, retries, etc.
   - Environment variable overrides via `MASH_*` prefix

2. **`cli.py`** - Click-based CLI commands (~490 lines)
   - `@cli`: Main group that launches interactive mode when no subcommand
   - `@grab`: Download command with all options as flags
   - `@preset`: Apply presets and optionally download
   - `@config`: Config management group with subcommands (show, set, unset, edit, etc.)
   - `@sites`: List supported sites from gallery-dl
   - `@version`: Show version information

3. **`interactive.py`** - Questionary-based TUI (~660 lines)
   - `InteractiveSession`: State manager for interactive mode
   - Menu functions: `menu_set_url()`, `menu_options()`, `menu_presets()`, etc.
   - Real-time command preview panel
   - Auto-suggestions (e.g., detects Instagram URLs and suggests destinations)

4. **`__init__.py`** - Package exports

### Configuration Resolution

Options are merged with this priority (lowest to highest):
1. Built-in defaults in `DownloadOptions`
2. Config file `[defaults]` section
3. Profile options (if `--profile` specified)
4. Preset options (if preset applied)
5. Environment variables (`MASH_*`)
6. CLI arguments

Profile inheritance is supported via the `extends` field. Use `Config.get_profile()` to resolve the full inherited chain.

### Gallery-dl Integration

insta-mash builds gallery-dl command-line arguments via `DownloadOptions.to_gallery_dl_args()`, then executes with `subprocess.run()`. It does NOT use gallery-dl as a Python library.

Key mapping:
- `destination` → `-D`
- `filename_format` → `-f`
- `rate_limit` → `-r`
- `sleep` → `--sleep`
- `cookies_browser` → `--cookies-from-browser`
- `archive_file` → `--download-archive`
- `write_metadata` → `--write-metadata`
- Boolean flags map to presence/absence of flag

### XDG Directory Compliance

Config and data paths follow XDG Base Directory specification:
- Config: `~/.config/insta-mash/config.toml` (or `$XDG_CONFIG_HOME`)
- Data: `~/.local/share/insta-mash/` (or `$XDG_DATA_HOME`)
- Windows uses `%APPDATA%` and `%LOCALAPPDATA%`

## Common Patterns

### Adding a New Preset

Edit `PRESETS` dict in `config.py`:

```python
PRESETS["newsite"] = Preset(
    name="newsite",
    description="Description shown in menus",
    url_template="https://example.com/{target}",  # or "" for modifier presets
    destination_template="./{target}_newsite",
    options=DownloadOptions(
        sleep="1.0-2.0",
        filename_format="{date:%Y-%m-%d}_{filename}",
    ),
)
```

Modifier presets (like "polite", "archive") have empty url_template and only set options.

### Adding a New CLI Option

1. Add field to `DownloadOptions` dataclass in `config.py`
2. Add mapping in `to_gallery_dl_args()` method
3. Add click option to `@grab` command in `cli.py`
4. Add menu entry in `menu_options()` in `interactive.py`
5. Add test in `tests/test_config.py`

### Adding Environment Variable Override

Add to `ENV_MAPPINGS` dict in `config.py` and update `apply_env_overrides()` function if special handling needed.

## Testing Strategy

Tests use pytest with the following structure:
- `TestDownloadOptions`: Dataclass behavior, merging, serialization
- `TestConfig`: Loading, saving, profile inheritance, option resolution
- `TestPresets`: Built-in preset behavior
- `TestValidation`: Format validation for sleep, rate_limit, retries, etc.

Use `tempfile.TemporaryDirectory()` for config file tests to avoid polluting user config.

## Dependencies

Core:
- `gallery-dl` - The underlying downloader (external process)
- `click` - CLI framework
- `rich` - Terminal formatting and panels
- `questionary` - Interactive prompts with styled menus
- `tomli-w` - TOML writing (read is stdlib in 3.11+)

Dev:
- `pytest` + `pytest-cov` - Testing
- `ruff` - Linting and formatting
- `mypy` - Type checking

## Entry Points

The package defines two console scripts in `pyproject.toml`:
- `mash = "insta_mash.cli:main"`
- `insta-mash = "insta_mash.cli:main"` (alias)

Both invoke `cli()` which launches interactive mode by default or runs subcommands.

## Configuration File Format

Config is TOML with two top-level sections:

```toml
[defaults]
destination = "~/Downloads"
sleep = "1.0-2.0"

[profiles.profilename]
description = "Optional description"
extends = "otherprofile"  # Optional inheritance
sleep = "3.0-5.0"
rate_limit = "500k"
```

All `DownloadOptions` fields are valid under `[defaults]` and `[profiles.*]`.
