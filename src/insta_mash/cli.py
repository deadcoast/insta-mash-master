"""
insta-mash CLI

Main entry point for the mash command.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from insta_mash import __version__
from insta_mash.config import (PRESETS, Config, DownloadOptions,
                               apply_env_overrides, get_config,
                               get_config_path, get_preset, list_presets,
                               validate_options)

console = Console()


# ---------------------------------------------------------------------------
# CLI Group
# ---------------------------------------------------------------------------


@click.group(invoke_without_command=True)
@click.option("--version", "-V", is_flag=True, help="Show version")
@click.pass_context
def cli(ctx: click.Context, version: bool) -> None:
    """
    insta-mash - The simple but comprehensive scraping wrapper.

    Run without arguments for interactive mode.
    """
    if version:
        console.print(f"insta-mash {__version__}")
        return

    if ctx.invoked_subcommand is None:
        # Launch interactive mode
        from insta_mash.interactive import run_interactive

        run_interactive()


# ---------------------------------------------------------------------------
# grab command
# ---------------------------------------------------------------------------


@cli.command()
@click.argument("url")
@click.option("--destination", "-d", help="Download directory")
@click.option("--filename", "-f", help="Filename format")
@click.option("--rate-limit", "-r", help="Max download rate (e.g., 500k, 2M)")
@click.option("--sleep", "-s", help="Delay between downloads (e.g., 2.0, 1-3)")
@click.option("--retries", "-R", type=int, help="Max retries for failed requests")
@click.option("--cookies", "-c", help="Browser to load cookies from")
@click.option("--archive", "-a", help="Archive file for tracking downloads")
@click.option("--range", "range_filter", help="Download only items in range")
@click.option("--metadata", "-m", is_flag=True, help="Write metadata JSON files")
@click.option("--zip", "-z", "zip_output", is_flag=True, help="Output as ZIP archive")
@click.option("--dry-run", "-n", is_flag=True, help="Simulate without downloading")
@click.option("--profile", "-p", help="Use saved profile")
@click.option("--preset", help="Apply built-in preset")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
def grab(
    url: str,
    destination: Optional[str],
    filename: Optional[str],
    rate_limit: Optional[str],
    sleep: Optional[str],
    retries: Optional[int],
    cookies: Optional[str],
    archive: Optional[str],
    range_filter: Optional[str],
    metadata: bool,
    zip_output: bool,
    dry_run: bool,
    profile: Optional[str],
    preset: Optional[str],
    verbose: bool,
    quiet: bool,
) -> None:
    """Download from URL."""
    config = get_config()

    # Build CLI options
    cli_opts = DownloadOptions()
    if destination:
        cli_opts.destination = destination
    if filename:
        cli_opts.filename_format = filename
    if rate_limit:
        cli_opts.rate_limit = rate_limit
    if sleep:
        cli_opts.sleep = sleep
    if retries is not None:
        cli_opts.retries = retries
    if cookies:
        cli_opts.cookies_browser = cookies
    if archive:
        cli_opts.archive_file = archive
    if range_filter:
        cli_opts.range_filter = range_filter
    if metadata:
        cli_opts.write_metadata = True
    if zip_output:
        cli_opts.zip_output = True

    # Resolve final options
    _, options = config.resolve_options(
        profile_name=profile or "",
        preset_name=preset or "",
        cli_options=cli_opts,
    )

    # Apply env overrides
    options = apply_env_overrides(options)

    # Validate
    errors = validate_options(options)
    if errors:
        for err in errors:
            console.print(f"[red]Config error:[/red] {err.field}: {err.message}")
        sys.exit(1)

    # Build command
    cmd = ["gallery-dl"]
    cmd.extend(options.to_gallery_dl_args())

    if dry_run:
        cmd.append("-s")
    if verbose:
        cmd.append("-v")
    if quiet:
        cmd.append("-q")

    cmd.append(url)

    # Show command
    if not quiet:
        console.print(Panel(" ".join(cmd), title="Command", border_style="dim"))

    # Create destination
    if options.destination and not dry_run:
        Path(os.path.expanduser(options.destination)).mkdir(parents=True, exist_ok=True)

    # Execute
    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        sys.exit(130)


# ---------------------------------------------------------------------------
# preset command
# ---------------------------------------------------------------------------


@cli.command()
@click.argument("name", required=False)
@click.argument("target", required=False)
@click.option("--list", "-l", "list_all", is_flag=True, help="List available presets")
@click.option("--dry-run", "-n", is_flag=True, help="Simulate without downloading")
@click.option("--profile", "-p", help="Also apply a profile")
@click.pass_context
def preset(
    ctx: click.Context,
    name: Optional[str],
    target: Optional[str],
    list_all: bool,
    dry_run: bool,
    profile: Optional[str],
) -> None:
    """Apply a built-in preset and optionally download."""
    if list_all or not name:
        table = Table(title="Available Presets", border_style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("Description")
        table.add_column("URL Template", style="dim")

        for preset_name, preset_obj in PRESETS.items():
            table.add_row(
                preset_name,
                preset_obj.description,
                preset_obj.url_template or "-",
            )

        console.print(table)
        return

    if name not in PRESETS:
        console.print(f"[red]Unknown preset:[/red] {name}")
        console.print(f"Available: {', '.join(list_presets())}")
        sys.exit(1)

    preset_obj = PRESETS[name]

    # If preset requires target and we have one, run download
    if preset_obj.url_template and target:
        url, _ = preset_obj.apply(target)
        ctx.invoke(
            grab,
            url=url,
            preset=name,
            profile=profile,
            dry_run=dry_run,
            destination=None,
            filename=None,
            rate_limit=None,
            sleep=None,
            retries=None,
            cookies=None,
            archive=None,
            range_filter=None,
            metadata=False,
            zip_output=False,
            verbose=False,
            quiet=False,
        )
    elif preset_obj.url_template and not target:
        console.print(f"[yellow]Preset '{name}' requires a target[/yellow]")
        console.print(f"Usage: mash preset {name} <username>")
    else:
        # Modifier preset (polite, archive, etc)
        console.print(f"[green]Preset '{name}' applied[/green]")
        console.print(f"Use with: mash grab --preset {name} <url>")


# ---------------------------------------------------------------------------
# config command
# ---------------------------------------------------------------------------


@cli.group()
def config() -> None:
    """Manage configuration."""
    pass


@config.command("show")
def config_show() -> None:
    """Display current configuration."""
    cfg = get_config()

    console.print(f"[dim]Config file: {cfg._path}[/dim]\n")

    # Defaults
    table = Table(title="Defaults", show_header=False, border_style="cyan")
    table.add_column("Setting", style="bold")
    table.add_column("Value", style="green")

    defaults_dict = cfg.defaults.to_dict()
    if defaults_dict:
        for key, value in defaults_dict.items():
            table.add_row(key, str(value))
    else:
        table.add_row("[dim]No custom defaults set[/dim]", "")

    console.print(table)
    console.print()

    # Profiles
    if cfg.profiles:
        table = Table(title="Profiles", border_style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("Description")
        table.add_column("Extends", style="dim")

        for name, profile in cfg.profiles.items():
            table.add_row(
                name,
                profile.description or "-",
                profile.extends or "-",
            )

        console.print(table)
    else:
        console.print("[dim]No profiles configured[/dim]")


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a default configuration value."""
    cfg = get_config()

    # Type conversion
    field_info = DownloadOptions.__dataclass_fields__.get(key)
    if not field_info:
        console.print(f"[red]Unknown setting:[/red] {key}")
        console.print(f"Valid settings: {', '.join(DownloadOptions.__dataclass_fields__.keys())}")
        sys.exit(1)

    field_type = field_info.type
    if field_type == "int":
        value = int(value)  # type: ignore
    elif field_type == "float":
        value = float(value)  # type: ignore
    elif field_type == "bool":
        value = value.lower() in ("true", "1", "yes")  # type: ignore

    cfg.set_default(key, value)
    cfg.save()

    console.print(f"[green]Set {key} = {value}[/green]")


@config.command("unset")
@click.argument("key")
def config_unset(key: str) -> None:
    """Reset a default to its original value."""
    cfg = get_config()

    if not cfg.unset_default(key):
        console.print(f"[red]Unknown setting:[/red] {key}")
        sys.exit(1)

    cfg.save()
    console.print(f"[green]Reset {key} to default[/green]")


@config.command("edit")
def config_edit() -> None:
    """Open configuration file in editor."""
    path = get_config_path()

    # Create default config if doesn't exist
    if not path.exists():
        cfg = get_config()
        cfg.save()

    editor = os.environ.get("EDITOR", "vim")
    subprocess.run([editor, str(path)])


@config.command("path")
def config_path() -> None:
    """Print configuration file path."""
    console.print(str(get_config_path()))


@config.command("profiles")
def config_profiles() -> None:
    """List saved profiles."""
    cfg = get_config()

    if not cfg.profiles:
        console.print("[dim]No profiles saved[/dim]")
        console.print("Save current config: mash config save-profile <name>")
        return

    table = Table(title="Saved Profiles", border_style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Description")
    table.add_column("Settings")

    for name, profile in cfg.profiles.items():
        settings = ", ".join(f"{k}={v}" for k, v in profile.options.to_dict().items())
        table.add_row(name, profile.description or "-", settings or "-")

    console.print(table)


@config.command("save-profile")
@click.argument("name")
@click.option("--description", "-d", default="", help="Profile description")
def config_save_profile(name: str, description: str) -> None:
    """Save current configuration as a profile."""
    cfg = get_config()
    cfg.add_profile(name, cfg.defaults, description)
    cfg.save()
    console.print(f"[green]Saved profile: {name}[/green]")


@config.command("load-profile")
@click.argument("name")
def config_load_profile(name: str) -> None:
    """Load a profile as current defaults."""
    cfg = get_config()

    profile = cfg.get_profile(name)
    if not profile:
        console.print(f"[red]Profile not found:[/red] {name}")
        sys.exit(1)

    cfg.defaults = profile.options
    cfg.save()
    console.print(f"[green]Loaded profile: {name}[/green]")


@config.command("delete-profile")
@click.argument("name")
def config_delete_profile(name: str) -> None:
    """Delete a saved profile."""
    cfg = get_config()

    if not cfg.delete_profile(name):
        console.print(f"[red]Profile not found:[/red] {name}")
        sys.exit(1)

    cfg.save()
    console.print(f"[green]Deleted profile: {name}[/green]")


# ---------------------------------------------------------------------------
# sites command
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--filter", "-f", "filter_str", help="Filter by name")
def sites(filter_str: Optional[str]) -> None:
    """List supported sites."""
    result = subprocess.run(
        ["gallery-dl", "--list-extractors"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        console.print("[red]Failed to get extractor list[/red]")
        sys.exit(1)

    lines = result.stdout.strip().split("\n")

    if filter_str:
        lines = [l for l in lines if filter_str.lower() in l.lower()]

    console.print(f"[bold]Supported sites ({len(lines)}):[/bold]\n")

    for line in lines[:100]:
        console.print(f"  {line}")

    if len(lines) > 100:
        console.print(f"\n  [dim]... and {len(lines) - 100} more[/dim]")
        console.print("  [dim]Use --filter to narrow results[/dim]")


# ---------------------------------------------------------------------------
# version command
# ---------------------------------------------------------------------------


@cli.command()
def version() -> None:
    """Show version information."""
    console.print(f"insta-mash {__version__}")

    # Get gallery-dl version
    result = subprocess.run(
        ["gallery-dl", "--version"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        console.print(f"gallery-dl {result.stdout.strip()}")

    console.print(f"Python {sys.version.split()[0]}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
