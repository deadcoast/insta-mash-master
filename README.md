# insta-mash

The simple but comprehensive scraping wrapper. Easier than not having to mash your potatoes.

An interactive CLI wrapper around [gallery-dl](https://github.com/mikf/gallery-dl) that provides a menu-driven interface for downloading media from Instagram and other platforms. No more memorizing flags.

## Features

- Interactive menu system with real-time command preview
- Batch mode for processing multiple URLs from a file
- Quick presets for common platforms (Instagram, Twitter, Reddit, Tumblr)
- Persistent configuration with profiles
- Rate limiting and polite scraping defaults
- Download archive tracking to skip duplicates
- Resume support for interrupted batch operations
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

### Batch Mode

Process multiple URLs from a file in a single operation:

```bash
# Run a batch file
mash batch run urls.txt

# With delay between downloads
mash batch run urls.txt --delay 2.0

# Dry run to test without downloading
mash batch run urls.txt --dry-run

# Resume interrupted batch
mash batch run urls.txt --resume

# Validate batch file before running
mash batch validate urls.txt
```

#### Batch File Format

Create a text file with one URL per line. Comments and empty lines are ignored:

```
# Instagram profiles
https://instagram.com/user1
https://instagram.com/user2 preset:instagram

# Twitter with custom profile
https://twitter.com/user3 profile:slow

# Mix presets and profiles
https://reddit.com/r/pics preset:reddit profile:archive

# Empty lines and comments are ignored

https://tumblr.com/blog/example preset:tumblr
```

**Format rules:**
- One URL per line (required)
- Lines starting with `#` are comments
- Empty lines are skipped
- Optional configuration: `preset:name` or `profile:name`
- Configuration is space-separated after the URL

#### Batch Features

**Progress Tracking**: Real-time display shows:
- Current progress (completed/total)
- Success and failure counts
- Current URL being processed
- Final summary report with error details

**Error Resilience**: If one download fails, the batch continues with the next URL. All errors are logged with details.

**Resume Support**: Interrupt with Ctrl+C and resume later:
```bash
# Start batch
mash batch run large-batch.txt

# Press Ctrl+C to interrupt
# Resume state is saved automatically

# Resume from where you left off
mash batch run large-batch.txt --resume
```

**Configuration Merging**: Per-URL settings override global defaults:
1. Config defaults (lowest priority)
2. Global batch settings
3. Profile options (if specified)
4. Preset options (if specified, highest priority)

**Validation**: Check your batch file before running:
```bash
mash batch validate urls.txt
```

Validation checks:
- Syntax errors (with line numbers)
- Non-existent preset references
- Non-existent profile references
- Reports total valid entries

#### Batch Examples

**Basic batch download:**
```bash
# Create batch file
cat > downloads.txt << EOF
https://instagram.com/photographer1
https://instagram.com/photographer2
https://instagram.com/photographer3
EOF

# Run it
mash batch run downloads.txt
```

**Mixed platforms with presets:**
```bash
cat > mixed.txt << EOF
# Social media
https://instagram.com/user1 preset:instagram
https://twitter.com/user2 preset:twitter
https://reddit.com/r/pics preset:reddit

# Custom profiles for specific needs
https://instagram.com/private_account profile:slow
EOF

mash batch run mixed.txt --delay 1.5
```

**Archive mode batch:**
```bash
cat > archive.txt << EOF
https://instagram.com/artist1 preset:archive
https://instagram.com/artist2 preset:archive
https://instagram.com/artist3 preset:archive
EOF

# Run with archive tracking to skip duplicates
mash batch run archive.txt
```

**Large batch with resume:**
```bash
# Start a large batch
mash batch run 1000-urls.txt --delay 2.0

# If interrupted, resume later
mash batch run 1000-urls.txt --resume --delay 2.0
```

#### Troubleshooting Batch Mode

**"Batch file not found" error:**
- Check the file path is correct
- Use absolute paths or paths relative to current directory
- Example: `mash batch run ./downloads/urls.txt`

**"Unknown preset" or "Unknown profile" errors:**
- Run `mash batch validate urls.txt` to check references
- List available presets: `mash preset --list`
- List available profiles: `mash config profiles`
- Fix typos in batch file (e.g., `preset:instagram` not `preset:insta`)

**Some downloads fail:**
- This is normal - batch mode continues on errors
- Check the final report for error details
- Common causes: private accounts, deleted content, rate limiting
- Use `--delay` to add pauses between downloads
- Try the failed URLs individually with `mash grab`

**Resume not working:**
- Resume state is saved as `.{filename}.resume` in same directory
- Example: `urls.txt` creates `.urls.txt.resume`
- Delete resume file to start fresh: `rm .urls.txt.resume`
- Resume state includes completed entry indices and timestamp

**Batch runs too fast / getting rate limited:**
- Add delay between downloads: `--delay 2.0`
- Use the `polite` preset: add `preset:polite` to entries
- Use a `slow` profile with higher sleep values
- Some platforms have stricter rate limits than others

**Want to test batch without downloading:**
- Use `--dry-run` flag: `mash batch run urls.txt --dry-run`
- Validates all entries and shows what would be downloaded
- No files are created in dry-run mode

**Batch file syntax errors:**
- Run validation first: `mash batch validate urls.txt`
- Each line must start with a valid URL
- Configuration format: `preset:name` or `profile:name`
- Use spaces to separate URL and configuration
- Comments start with `#`, empty lines are ignored

**Need different settings per URL:**
- Use presets for platform-specific settings
- Use profiles for custom configurations
- Example: `https://example.com preset:instagram profile:archive`
- Entry-specific settings override global defaults

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
| `mash batch run <file>` | Run batch downloads from file |
| `mash batch validate <file>` | Validate batch file syntax and references |
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

### Grab Options

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

### Batch Options

These work with `mash batch run`:

| Flag | Short | Description |
|------|-------|-------------|
| `--delay` | `-d` | Delay between downloads in seconds |
| `--dry-run` | `-n` | Simulate without downloading |
| `--resume` | `-r` | Resume from previous interrupted session |

## Requirements

- Python 3.10+
- gallery-dl (installed automatically)

## Roadmap

### Core Improvements

- **Progress display** — Real-time download progress with ETA and throughput

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
