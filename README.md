# insta-mash

The simple but comprehensive scraping wrapper. Easier than not having to mash your potatoes.

An interactive CLI wrapper around [gallery-dl](https://github.com/mikf/gallery-dl) that provides a menu-driven interface for downloading media from Instagram and other platforms. No more memorizing flags.

## Features

- Interactive menu system with real-time command preview
- Quick presets for common platforms (Instagram, Twitter, Reddit, Tumblr)
- Persistent configuration with profiles
- Rate limiting and polite scraping defaults
- Download archive tracking to skip duplicates
- Dry-run simulation mode
- macOS terminal native (also works on Linux/Windows)

## Quickstart

### Install with uv

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/yourusername/insta-mash.git
cd insta-mash
uv sync

# Run
uv run mash
```

### Install with pip

```bash
pip install insta-mash
mash
```

### One-liner (no install)

```bash
uvx insta-mash
```

## Usage

### Interactive Mode

Just run:

```bash
mash
```

You'll get a menu. Navigate with arrow keys. The current configuration and command preview are always visible.

### Direct Commands

Skip the menu when you know what you want:

```bash
# Download a public Instagram profile
mash grab https://instagram.com/username

# Use a preset
mash preset instagram username

# Download with a saved profile
mash grab --profile slow https://instagram.com/username

# Dry run
mash grab --dry-run https://instagram.com/username

# Show current config
mash config show

# Set a default
mash config set destination ~/Pictures/scrapes
```

### Presets

Built-in presets configure sensible defaults for each platform:

| Preset | What it does |
|--------|--------------|
| `instagram` | 1-2s sleep, date-prefixed filenames |
| `twitter` | Media timeline, original filenames |
| `reddit` | Subreddit or user, handles galleries |
| `tumblr` | Blog archive with metadata |
| `polite` | 2-4s sleep, 500k rate limit |
| `archive` | Tracks downloads, writes metadata JSON |

```bash
mash preset instagram myusername
mash preset polite  # just applies rate limiting to current config
```

### Profiles

Save configurations for reuse:

```bash
# Save current config as a profile
mash config save-profile myprofile

# List profiles
mash config profiles

# Load a profile
mash config load-profile myprofile

# Delete a profile
mash config delete-profile myprofile

# Use a profile inline
mash grab --profile myprofile https://example.com/gallery
```

## Configuration

Config lives at `~/.config/insta-mash/config.toml` (or `$XDG_CONFIG_HOME/insta-mash/config.toml`).

```toml
[defaults]
destination = "~/Downloads/insta-mash"
sleep = "1.0-2.0"
retries = 4
write_metadata = false

[profiles.slow]
sleep = "3.0-5.0"
rate_limit = "200k"
retries = 2

[profiles.archive]
archive_file = "~/.local/share/insta-mash/archive.txt"
write_metadata = true
```

See [docs/CONFIG.md](docs/CONFIG.md) for full configuration reference.

## Command Reference

| Command | Description |
|---------|-------------|
| `mash` | Launch interactive mode |
| `mash grab <url>` | Download from URL |
| `mash preset <name> [target]` | Apply preset, optionally with target |
| `mash config show` | Display current configuration |
| `mash config set <key> <value>` | Set a default value |
| `mash config unset <key>` | Remove a default |
| `mash config edit` | Open config in $EDITOR |
| `mash config path` | Print config file location |
| `mash config profiles` | List saved profiles |
| `mash config save-profile <name>` | Save current config as profile |
| `mash config load-profile <name>` | Load a profile |
| `mash config delete-profile <name>` | Delete a profile |
| `mash sites` | List supported sites |
| `mash version` | Show version info |

## Options

These work with `mash grab`:

| Flag | Short | Description |
|------|-------|-------------|
| `--destination` | `-d` | Download directory |
| `--filename` | `-f` | Filename format |
| `--rate-limit` | `-r` | Max download rate (e.g., 500k, 2M) |
| `--sleep` | `-s` | Delay between downloads (e.g., 2.0, 1-3) |
| `--retries` | `-R` | Max retries for failed requests |
| `--cookies` | `-c` | Browser to load cookies from |
| `--archive` | `-a` | Archive file for tracking downloads |
| `--range` | | Download only items in range (e.g., 1-10) |
| `--metadata` | `-m` | Write metadata JSON files |
| `--zip` | `-z` | Output as ZIP archive |
| `--dry-run` | `-n` | Simulate without downloading |
| `--profile` | `-p` | Use saved profile |
| `--verbose` | `-v` | Verbose output |
| `--quiet` | `-q` | Suppress output |

## Requirements

- Python 3.10+
- gallery-dl (installed automatically)

## Roadmap

### Core Improvements

- **Batch mode** — Input file support for downloading multiple URLs in sequence
- **Progress display** — Real-time download progress with ETA and throughput
- **Resume support** — Graceful interrupt handling with automatic resume on restart

### Platform Intelligence

- **Smart presets** — Auto-detect platform from URL and apply appropriate preset
- **Platform-specific options** — Surface relevant gallery-dl options per platform (e.g., Instagram stories vs posts vs reels)
- **Authentication wizard** — Guided setup for cookie extraction when private content access is needed

### Configuration

- **Profile inheritance** — Profiles that extend other profiles
- **Environment variable overrides** — `MASH_DESTINATION`, `MASH_SLEEP`, etc.
- **Per-directory config** — `.mashrc` files for project-specific defaults

### Output & Organization

- **Custom filename templates** — More intuitive template syntax on top of gallery-dl's
- **Post-download hooks** — Run scripts after downloads complete (organize, convert, notify)
- **Deduplication** — Content-hash based duplicate detection across directories

### Quality of Life

- **Shell completions** — Bash, zsh, fish autocompletions
- **Update checker** — Notify when new versions are available
- **Export/import config** — Share configurations between machines

## License

MIT

## Acknowledgments

This is a wrapper around [gallery-dl](https://github.com/mikf/gallery-dl) by mikf. All the heavy lifting is done there.
