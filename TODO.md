# insta-mash TODO

## Active

- [ ] Implement CLI argument parser (click or typer)
- [ ] Implement `mash grab` command
- [ ] Implement `mash preset` command
- [ ] Wire up config system to CLI
- [ ] Add --dry-run flag implementation
- [ ] Test on macOS terminal

## Config System

- [x] Design config schema
- [x] Implement config loader with TOML
- [x] Implement profile system
- [ ] Add config validation
- [ ] Add config migration for version changes
- [ ] Implement `mash config` subcommands
- [ ] Add XDG fallback for non-standard systems

## Interactive Mode

- [x] Basic menu structure (from gdl.py)
- [ ] Refactor menu to use new config system
- [ ] Add profile selection to menu
- [ ] Add "save current as profile" option
- [ ] Improve command preview formatting

## Presets

- [x] Instagram preset
- [x] Twitter preset  
- [x] Reddit preset
- [x] Tumblr preset
- [x] Polite preset
- [x] Archive preset
- [ ] Add preset for Pixiv
- [ ] Add preset for DeviantArt
- [ ] Smart platform detection from URL

## Testing

- [ ] Unit tests for config system
- [ ] Unit tests for command builder
- [ ] Integration tests with gallery-dl
- [ ] Test on Windows
- [ ] Test on Linux

## Documentation

- [x] README with quickstart
- [ ] CONFIG.md reference
- [ ] CONTRIBUTING.md
- [ ] man page

## Packaging

- [ ] pyproject.toml setup
- [ ] Entry points for `mash` command
- [ ] PyPI publish workflow
- [ ] Homebrew formula

## Future

- [ ] Batch mode with input files
- [ ] Progress bars
- [ ] Shell completions
- [ ] Post-download hooks
- [ ] Content-hash deduplication
