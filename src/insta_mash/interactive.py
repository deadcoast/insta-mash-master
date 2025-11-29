"""
insta-mash interactive mode

Menu-driven interface for gallery-dl operations.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from insta_mash import __version__
from insta_mash.config import (PRESETS, Config, DownloadOptions,
                               apply_env_overrides, get_config, list_presets,
                               validate_options)

console = Console()

# Questionary style
prompt_style = Style(
    [
        ("qmark", "fg:cyan bold"),
        ("question", "fg:white bold"),
        ("answer", "fg:green"),
        ("pointer", "fg:cyan bold"),
        ("highlighted", "fg:cyan bold"),
        ("selected", "fg:green"),
        ("separator", "fg:gray"),
        ("instruction", "fg:gray italic"),
    ]
)


class InteractiveSession:
    """Manages interactive session state."""

    def __init__(self) -> None:
        self.config = get_config()
        self.url: str = ""
        self.options = DownloadOptions()
        self.active_profile: str = ""
        self.active_preset: str = ""

        # Initialize from defaults
        self._apply_defaults()

    def _apply_defaults(self) -> None:
        """Apply config defaults to current options."""
        self.options = self.config.defaults.merge(self.options)
        self.options = apply_env_overrides(self.options)

    def apply_preset(self, preset_name: str, target: str = "") -> None:
        """Apply a preset."""
        if preset_name not in PRESETS:
            return

        preset = PRESETS[preset_name]
        url, opts = preset.apply(target)

        if url:
            self.url = url
        self.options = self.options.merge(opts)
        self.active_preset = preset_name

    def apply_profile(self, profile_name: str) -> None:
        """Apply a saved profile."""
        profile = self.config.get_profile(profile_name)
        if profile:
            self.options = self.options.merge(profile.options)
            self.active_profile = profile_name

    def build_command(self) -> list[str]:
        """Build gallery-dl command from current state."""
        cmd = ["gallery-dl"]
        cmd.extend(self.options.to_gallery_dl_args())
        if self.url:
            cmd.append(self.url)
        return cmd

    def reset(self) -> None:
        """Reset to defaults."""
        self.url = ""
        self.options = DownloadOptions()
        self.active_profile = ""
        self.active_preset = ""
        self._apply_defaults()

    def display(self) -> None:
        """Display current configuration."""
        table = Table(show_header=False, border_style="cyan", title="Current Configuration")
        table.add_column("Setting", style="bold", width=20)
        table.add_column("Value", style="green")

        # URL
        table.add_row("URL", self.url or "[dim]not set[/dim]")

        # Active modifiers
        modifiers = []
        if self.active_profile:
            modifiers.append(f"profile:{self.active_profile}")
        if self.active_preset:
            modifiers.append(f"preset:{self.active_preset}")
        table.add_row("Active", ", ".join(modifiers) if modifiers else "[dim]none[/dim]")

        table.add_row("", "")  # Spacer

        # Options
        table.add_row("Destination", self.options.destination)
        table.add_row("Filename Format", self.options.filename_format or "[dim]default[/dim]")
        table.add_row("Rate Limit", self.options.rate_limit or "[dim]unlimited[/dim]")
        table.add_row("Sleep", self.options.sleep or "[dim]none[/dim]")
        table.add_row("Retries", str(self.options.retries))
        table.add_row("Cookies From", self.options.cookies_browser or "[dim]none[/dim]")
        table.add_row("Archive File", self.options.archive_file or "[dim]none[/dim]")
        table.add_row("Range", self.options.range_filter or "[dim]all[/dim]")
        table.add_row("Write Metadata", "Yes" if self.options.write_metadata else "No")
        table.add_row("Zip Output", "Yes" if self.options.zip_output else "No")

        if self.options.extra_options:
            table.add_row("Extra Options", ", ".join(self.options.extra_options))

        console.print(table)
        console.print()

        # Command preview
        cmd_text = " ".join(self.build_command())
        console.print(Panel(cmd_text, title="Command Preview", border_style="dim"))


def clear_screen() -> None:
    console.clear()


def header() -> None:
    console.print(
        Panel(
            Text(f"insta-mash {__version__}", justify="center", style="bold cyan"),
            subtitle="[dim]↑↓ navigate | enter select | q quit[/dim]",
            border_style="cyan",
        )
    )
    console.print()


def run_interactive() -> None:
    """Run the interactive menu."""
    session = InteractiveSession()

    while True:
        clear_screen()
        header()
        session.display()
        console.print()

        choice = questionary.select(
            "What do you want to do?",
            choices=[
                questionary.Choice("Set URL", value="url"),
                questionary.Choice("Set Destination", value="dest"),
                questionary.Choice("Configure Options", value="options"),
                questionary.Choice("Quick Presets", value="presets"),
                questionary.Choice("Load Profile", value="profile"),
                questionary.Choice("Run Download", value="run"),
                questionary.Choice("Simulate (dry run)", value="simulate"),
                questionary.Choice("Save as Profile", value="save_profile"),
                questionary.Choice("View Supported Sites", value="sites"),
                questionary.Choice("Reset", value="reset"),
                questionary.Separator(),
                questionary.Choice("Quit", value="quit"),
            ],
            style=prompt_style,
            qmark="→",
        ).ask()

        if choice is None or choice == "quit":
            clear_screen()
            console.print("[cyan]Goodbye![/cyan]")
            break
        elif choice == "url":
            menu_set_url(session)
        elif choice == "dest":
            menu_set_destination(session)
        elif choice == "options":
            menu_options(session)
        elif choice == "presets":
            menu_presets(session)
        elif choice == "profile":
            menu_load_profile(session)
        elif choice == "run":
            menu_run(session, simulate=False)
        elif choice == "simulate":
            menu_run(session, simulate=True)
        elif choice == "save_profile":
            menu_save_profile(session)
        elif choice == "sites":
            menu_sites()
        elif choice == "reset":
            session.reset()


def menu_set_url(session: InteractiveSession) -> None:
    """Set URL menu."""
    clear_screen()
    header()

    url = questionary.text(
        "Enter URL to download from:",
        default=session.url,
        style=prompt_style,
        qmark="→",
    ).ask()

    if url and url.lower() not in ("b", "q"):
        session.url = url

        # Auto-suggest destination based on URL
        if "instagram.com" in url:
            username = url.rstrip("/").split("/")[-1]
            suggested = f"./{username}_instagram"
            if questionary.confirm(
                f"Set destination to {suggested}?",
                default=True,
                style=prompt_style,
                qmark="→",
            ).ask():
                session.options.destination = suggested


def menu_set_destination(session: InteractiveSession) -> None:
    """Set destination menu."""
    clear_screen()
    header()

    dest = questionary.path(
        "Download destination:",
        default=session.options.destination,
        style=prompt_style,
        qmark="→",
    ).ask()

    if dest and dest.lower() not in ("b", "q"):
        session.options.destination = dest


def menu_options(session: InteractiveSession) -> None:
    """Options submenu."""
    while True:
        clear_screen()
        header()
        session.display()
        console.print()

        choice = questionary.select(
            "Configure Options:",
            choices=[
                questionary.Choice("Filename Format", value="filename"),
                questionary.Choice("Rate Limit", value="rate"),
                questionary.Choice("Sleep Between Downloads", value="sleep"),
                questionary.Choice("Retries", value="retries"),
                questionary.Choice("Browser Cookies", value="cookies"),
                questionary.Choice("Download Archive", value="archive"),
                questionary.Choice("Range Filter", value="range"),
                questionary.Choice("Write Metadata JSON", value="metadata"),
                questionary.Choice("Zip Output", value="zip"),
                questionary.Choice("Add Extra Option", value="extra"),
                questionary.Separator(),
                questionary.Choice("← Back", value="back"),
            ],
            style=prompt_style,
            qmark="→",
        ).ask()

        if choice == "back" or choice is None:
            break
        elif choice == "filename":
            menu_filename(session)
        elif choice == "rate":
            menu_rate_limit(session)
        elif choice == "sleep":
            menu_sleep(session)
        elif choice == "retries":
            menu_retries(session)
        elif choice == "cookies":
            menu_cookies(session)
        elif choice == "archive":
            menu_archive(session)
        elif choice == "range":
            menu_range(session)
        elif choice == "metadata":
            session.options.write_metadata = not session.options.write_metadata
        elif choice == "zip":
            session.options.zip_output = not session.options.zip_output
        elif choice == "extra":
            menu_extra_option(session)


def menu_filename(session: InteractiveSession) -> None:
    """Filename format menu."""
    clear_screen()
    header()

    console.print("[dim]Common placeholders: {category}, {filename}, {id}, {date}, {title}[/dim]")
    console.print("[dim]Use /O for original filenames[/dim]")
    console.print()

    choice = questionary.select(
        "Filename format:",
        choices=[
            questionary.Choice("Original filename", value="/O"),
            questionary.Choice("{category}_{id}_{filename}", value="{category}_{id}_{filename}"),
            questionary.Choice("{date:%Y-%m-%d}_{filename}", value="{date:%Y-%m-%d}_{filename}"),
            questionary.Choice("{date:%Y-%m-%d}_{id}", value="{date:%Y-%m-%d}_{id}"),
            questionary.Choice("Custom...", value="custom"),
            questionary.Choice("Clear (use default)", value=""),
        ],
        style=prompt_style,
        qmark="→",
    ).ask()

    if choice == "custom":
        custom = questionary.text(
            "Enter custom format:",
            style=prompt_style,
            qmark="→",
        ).ask()
        if custom:
            session.options.filename_format = custom
    elif choice is not None:
        session.options.filename_format = choice


def menu_rate_limit(session: InteractiveSession) -> None:
    """Rate limit menu."""
    clear_screen()
    header()

    console.print("[dim]Examples: 500k, 2.5M, 800k-2M (range)[/dim]")
    console.print()

    rate = questionary.text(
        "Rate limit (empty for unlimited):",
        default=session.options.rate_limit,
        style=prompt_style,
        qmark="→",
    ).ask()

    if rate is not None:
        session.options.rate_limit = rate


def menu_sleep(session: InteractiveSession) -> None:
    """Sleep delay menu."""
    clear_screen()
    header()

    console.print("[dim]Delay between downloads. Examples: 2.0, 1.5-3.0 (range)[/dim]")
    console.print()

    sleep = questionary.text(
        "Sleep seconds (empty for none):",
        default=session.options.sleep,
        style=prompt_style,
        qmark="→",
    ).ask()

    if sleep is not None:
        session.options.sleep = sleep


def menu_retries(session: InteractiveSession) -> None:
    """Retries menu."""
    clear_screen()
    header()

    retries = questionary.text(
        "Max retries (-1 for infinite):",
        default=str(session.options.retries),
        style=prompt_style,
        qmark="→",
    ).ask()

    if retries:
        try:
            session.options.retries = int(retries)
        except ValueError:
            pass


def menu_cookies(session: InteractiveSession) -> None:
    """Browser cookies menu."""
    clear_screen()
    header()

    console.print("[dim]Load session cookies from browser for authenticated downloads[/dim]")
    console.print()

    choice = questionary.select(
        "Load cookies from:",
        choices=[
            questionary.Choice("None (public only)", value=""),
            questionary.Choice("Chrome", value="chrome"),
            questionary.Choice("Firefox", value="firefox"),
            questionary.Choice("Safari", value="safari"),
            questionary.Choice("Edge", value="edge"),
            questionary.Choice("Brave", value="brave"),
            questionary.Choice("Opera", value="opera"),
        ],
        style=prompt_style,
        qmark="→",
    ).ask()

    if choice is not None:
        session.options.cookies_browser = choice


def menu_archive(session: InteractiveSession) -> None:
    """Archive file menu."""
    clear_screen()
    header()

    console.print("[dim]Archive file tracks downloaded files to skip duplicates across runs[/dim]")
    console.print()

    archive = questionary.path(
        "Archive file path (empty to disable):",
        default=session.options.archive_file or "./gallery-dl-archive.txt",
        style=prompt_style,
        qmark="→",
    ).ask()

    if archive is not None:
        session.options.archive_file = archive if archive.lower() not in ("", "none") else ""


def menu_range(session: InteractiveSession) -> None:
    """Range filter menu."""
    clear_screen()
    header()

    console.print("[dim]Download only specific items. Examples: 1-10, 5, 1:100:2 (every 2nd)[/dim]")
    console.print()

    range_val = questionary.text(
        "Range filter (empty for all):",
        default=session.options.range_filter,
        style=prompt_style,
        qmark="→",
    ).ask()

    if range_val is not None:
        session.options.range_filter = range_val


def menu_extra_option(session: InteractiveSession) -> None:
    """Add extra gallery-dl option."""
    clear_screen()
    header()

    console.print("[dim]Format: key=value (e.g., browser=firefox, sleep-request=1.0)[/dim]")
    console.print()

    if session.options.extra_options:
        console.print(f"Current: {', '.join(session.options.extra_options)}")
        console.print()

    opt = questionary.text(
        "Add option:",
        style=prompt_style,
        qmark="→",
    ).ask()

    if opt and "=" in opt:
        session.options.extra_options.append(opt)


def menu_presets(session: InteractiveSession) -> None:
    """Presets menu."""
    clear_screen()
    header()

    choices = []
    for name, preset in PRESETS.items():
        label = f"{name} - {preset.description}"
        choices.append(questionary.Choice(label, value=name))

    choices.append(questionary.Separator())
    choices.append(questionary.Choice("← Back", value="back"))

    choice = questionary.select(
        "Select Preset:",
        choices=choices,
        style=prompt_style,
        qmark="→",
    ).ask()

    if choice == "back" or choice is None:
        return

    preset = PRESETS[choice]

    # If preset needs a target
    if preset.url_template and "{target}" in preset.url_template:
        console.print()
        target = questionary.text(
            "Enter username/target:",
            style=prompt_style,
            qmark="→",
        ).ask()

        if target:
            session.apply_preset(choice, target)
    else:
        session.apply_preset(choice)


def menu_load_profile(session: InteractiveSession) -> None:
    """Load profile menu."""
    clear_screen()
    header()

    if not session.config.profiles:
        console.print("[dim]No profiles saved yet[/dim]")
        console.print("Save current config with 'Save as Profile'")
        console.print()
        questionary.press_any_key_to_continue(style=prompt_style).ask()
        return

    choices = []
    for name, profile in session.config.profiles.items():
        label = f"{name}"
        if profile.description:
            label += f" - {profile.description}"
        choices.append(questionary.Choice(label, value=name))

    choices.append(questionary.Separator())
    choices.append(questionary.Choice("← Back", value="back"))

    choice = questionary.select(
        "Select Profile:",
        choices=choices,
        style=prompt_style,
        qmark="→",
    ).ask()

    if choice and choice != "back":
        session.apply_profile(choice)


def menu_save_profile(session: InteractiveSession) -> None:
    """Save current config as profile."""
    clear_screen()
    header()

    name = questionary.text(
        "Profile name:",
        style=prompt_style,
        qmark="→",
    ).ask()

    if not name:
        return

    description = questionary.text(
        "Description (optional):",
        style=prompt_style,
        qmark="→",
    ).ask()

    session.config.add_profile(name, session.options, description or "")
    session.config.save()

    console.print(f"\n[green]Saved profile: {name}[/green]")
    questionary.press_any_key_to_continue(style=prompt_style).ask()


def menu_run(session: InteractiveSession, simulate: bool = False) -> None:
    """Run download."""
    clear_screen()
    header()

    if not session.url:
        console.print("[red]Error: No URL set[/red]")
        questionary.press_any_key_to_continue(style=prompt_style).ask()
        return

    # Validate
    errors = validate_options(session.options)
    if errors:
        for err in errors:
            console.print(f"[red]Config error:[/red] {err.field}: {err.message}")
        console.print()
        questionary.press_any_key_to_continue(style=prompt_style).ask()
        return

    cmd = session.build_command()
    if simulate:
        cmd.append("-s")

    title = "Simulating" if simulate else "Executing"
    style = "yellow" if simulate else "green"
    console.print(Panel(" ".join(cmd), title=title, border_style=style))
    console.print()

    if not simulate:
        # Create destination
        dest = os.path.expanduser(session.options.destination)
        Path(dest).mkdir(parents=True, exist_ok=True)

    try:
        process = subprocess.run(cmd)
        console.print()
        if process.returncode == 0:
            console.print("[green]✓ Complete[/green]")
        else:
            console.print(f"[yellow]Finished with return code {process.returncode}[/yellow]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

    console.print()
    questionary.press_any_key_to_continue(style=prompt_style).ask()


def menu_sites() -> None:
    """View supported sites."""
    clear_screen()
    header()

    console.print("[dim]Fetching supported extractors...[/dim]")

    result = subprocess.run(
        ["gallery-dl", "--list-extractors"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        lines = result.stdout.strip().split("\n")
        console.print(f"\n[bold]Supported sites ({len(lines)} extractors):[/bold]\n")

        for line in lines[:50]:
            console.print(f"  {line}")

        if len(lines) > 50:
            console.print(f"\n  [dim]... and {len(lines) - 50} more[/dim]")

    console.print()
    questionary.press_any_key_to_continue(style=prompt_style).ask()
