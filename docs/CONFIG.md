# Configuration Reference

insta-mash stores configuration in TOML format at `~/.config/insta-mash/config.toml`.

## File Locations

| Platform | Config Path | Data Path |
|----------|-------------|-----------|
| macOS | `~/.config/insta-mash/config.toml` | `~/.local/share/insta-mash/` |
| Linux | `~/.config/insta-mash/config.toml` | `~/.local/share/insta-mash/` |
| Windows | `%APPDATA%\insta-mash\config.toml` | `%LOCALAPPDATA%\insta-mash\` |

XDG paths are respected if `$XDG_CONFIG_HOME` or `$XDG_DATA_HOME` are set.

## Configuration File Structure

```toml
[defaults]
# Default options applied to all downloads

[profiles.NAME]
# Named configuration profiles
```

## Default Options

All options under `[defaults]` are applied to every download unless overridden.

```toml
[defaults]
destination = "~/Downloads/insta-mash"
filename_format = "{date:%Y-%m-%d}_{filename}"
sleep = "1.0-2.0"
retries = 4
```

### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `destination` | string | `"./downloads"` | Download directory |
| `filename_format` | string | `""` | Filename template (see gallery-dl docs) |
| `rate_limit` | string | `""` | Max download rate (e.g., `500k`, `2M`) |
| `sleep` | string | `""` | Delay between downloads (e.g., `2.0`, `1-3`) |
| `sleep_request` | string | `""` | Delay between HTTP requests |
| `retries` | int | `4` | Max retries for failed requests |
| `timeout` | float | `30.0` | HTTP timeout in seconds |
| `cookies_browser` | string | `""` | Browser to load cookies from |
| `cookies_file` | string | `""` | Path to cookies file |
| `archive_file` | string | `""` | Archive file for duplicate tracking |
| `range_filter` | string | `""` | Item range filter (e.g., `1-10`) |
| `filesize_min` | string | `""` | Minimum file size (e.g., `100k`) |
| `filesize_max` | string | `""` | Maximum file size (e.g., `50M`) |
| `write_metadata` | bool | `false` | Write metadata JSON files |
| `zip_output` | bool | `false` | Output as ZIP archive |
| `no_skip` | bool | `false` | Overwrite existing files |
| `no_mtime` | bool | `false` | Don't set file modification times |
| `user_agent` | string | `""` | Custom user agent |
| `proxy` | string | `""` | Proxy URL |
| `extra_options` | list | `[]` | Additional gallery-dl options |

## Profiles

Profiles are named configurations that can be loaded on demand.

```toml
[profiles.slow]
description = "Polite scraping with long delays"
sleep = "3.0-5.0"
sleep_request = "1.0"
rate_limit = "200k"
retries = 2

[profiles.archive]
description = "Track all downloads"
archive_file = "~/.local/share/insta-mash/archive.txt"
write_metadata = true

[profiles.instagram-private]
description = "Instagram with auth"
cookies_browser = "chrome"
sleep = "2.0-4.0"
```

### Profile Inheritance

Profiles can extend other profiles:

```toml
[profiles.base]
sleep = "1.0-2.0"
retries = 3

[profiles.slow]
extends = "base"
sleep = "3.0-5.0"  # Overrides base
# retries = 3 inherited from base
```

## Using Profiles

### CLI

```bash
# Use a profile
mash grab --profile slow https://instagram.com/username

# Apply profile as new defaults
mash config load-profile slow
```

### Interactive Mode

Select "Load Profile" from the main menu.

## Environment Variables

Environment variables override config file settings:

| Variable | Overrides |
|----------|-----------|
| `MASH_DESTINATION` | `destination` |
| `MASH_SLEEP` | `sleep` |
| `MASH_RATE_LIMIT` | `rate_limit` |
| `MASH_RETRIES` | `retries` |
| `MASH_COOKIES_BROWSER` | `cookies_browser` |
| `MASH_ARCHIVE` | `archive_file` |
| `MASH_PROXY` | `proxy` |

Example:
```bash
MASH_SLEEP="2.0-3.0" mash grab https://instagram.com/username
```

## Option Priority

Options are applied in this order (later overrides earlier):

1. Built-in defaults
2. Config file `[defaults]`
3. Profile options (if `--profile` specified)
4. Preset options (if `--preset` specified)
5. Environment variables
6. CLI arguments

## Example Configurations

### Minimal

```toml
[defaults]
destination = "~/Pictures/scrapes"
```

### Comprehensive

```toml
[defaults]
destination = "~/Pictures/scrapes"
sleep = "1.0-2.0"
retries = 3
archive_file = "~/.local/share/insta-mash/archive.txt"

[profiles.instagram]
description = "Instagram defaults"
sleep = "1.5-3.0"
filename_format = "{date:%Y-%m-%d}_{id}"

[profiles.fast]
description = "No delays, risky"
sleep = ""
retries = 1

[profiles.stealth]
description = "Extra slow and careful"
sleep = "5.0-10.0"
sleep_request = "2.0"
rate_limit = "100k"
```

## Filename Format

The `filename_format` option uses gallery-dl's template syntax. Common placeholders:

| Placeholder | Description |
|-------------|-------------|
| `{filename}` | Original filename |
| `{id}` | Post/image ID |
| `{category}` | Site category |
| `{subcategory}` | Site subcategory |
| `{date}` | Post date |
| `{title}` | Post title |
| `/O` | Use original filename |

Date formatting uses Python's strftime:
- `{date:%Y-%m-%d}` → `2024-01-15`
- `{date:%Y%m%d_%H%M%S}` → `20240115_143022`

See [gallery-dl documentation](https://github.com/mikf/gallery-dl/blob/master/docs/formatting.md) for full details.

## Browser Cookies

The `cookies_browser` option tells gallery-dl to extract cookies from your browser for authenticated downloads.

Supported browsers:
- `chrome`
- `firefox`
- `safari`
- `edge`
- `brave`
- `opera`
- `chromium`

You can also specify a profile:
```toml
cookies_browser = "firefox:profile-name"
```

Or a domain filter:
```toml
cookies_browser = "chrome/instagram.com"
```
