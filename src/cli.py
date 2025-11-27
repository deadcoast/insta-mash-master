#!/usr/bin/env python3
"""
gdl - Interactive CLI wrapper for gallery-dl
Provides a menu-driven interface for common gallery-dl operations.
"""

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Dependency check and install
def ensure_dependencies():
    required = ["rich", "questionary", "gallery_dl"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            missing.append(pkg.replace("_", "-"))
    
    if missing:
        print(f"Installing: {', '.join(missing)}")
        subprocess.run([
            sys.executable, "-m", "pip", "install", *missing,
            "--break-system-packages", "-q"
        ])

ensure_dependencies()

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# Questionary style matching rich aesthetic
prompt_style = Style([
    ("qmark", "fg:cyan bold"),
    ("question", "fg:white bold"),
    ("answer", "fg:green"),
    ("pointer", "fg:cyan bold"),
    ("highlighted", "fg:cyan bold"),
    ("selected", "fg:green"),
    ("separator", "fg:gray"),
    ("instruction", "fg:gray italic"),
])


@dataclass
class DownloadConfig:
    """Stores current download configuration."""
    url: str = ""
    destination: str = "./downloads"
    filename_format: str = ""
    rate_limit: str = ""
    sleep: str = ""
    retries: int = 4
    cookies_browser: str = ""
    archive_file: str = ""
    range_filter: str = ""
    simulate: bool = False
    write_metadata: bool = False
    zip_output: bool = False
    custom_options: list = field(default_factory=list)
    
    def build_command(self) -> list[str]:
        """Build gallery-dl command from current config."""
        cmd = ["gallery-dl"]
        
        if self.destination:
            cmd.extend(["-D", self.destination])
        if self.filename_format:
            cmd.extend(["-f", self.filename_format])
        if self.rate_limit:
            cmd.extend(["-r", self.rate_limit])
        if self.sleep:
            cmd.extend(["--sleep", self.sleep])
        if self.retries != 4:
            cmd.extend(["-R", str(self.retries)])
        if self.cookies_browser:
            cmd.extend(["--cookies-from-browser", self.cookies_browser])
        if self.archive_file:
            cmd.extend(["--download-archive", self.archive_file])
        if self.range_filter:
            cmd.extend(["--range", self.range_filter])
        if self.simulate:
            cmd.append("-s")
        if self.write_metadata:
            cmd.append("--write-metadata")
        if self.zip_output:
            cmd.append("--zip")
        for opt in self.custom_options:
            cmd.extend(["-o", opt])
        
        if self.url:
            cmd.append(self.url)
        
        return cmd
    
    def display(self) -> None:
        """Display current configuration."""
        table = Table(title="Current Configuration", show_header=False, border_style="cyan")
        table.add_column("Setting", style="bold")
        table.add_column("Value", style="green")
        
        table.add_row("URL", self.url or "[dim]not set[/dim]")
        table.add_row("Destination", self.destination)
        table.add_row("Filename Format", self.filename_format or "[dim]default[/dim]")
        table.add_row("Rate Limit", self.rate_limit or "[dim]unlimited[/dim]")
        table.add_row("Sleep", self.sleep or "[dim]none[/dim]")
        table.add_row("Retries", str(self.retries))
        table.add_row("Cookies From", self.cookies_browser or "[dim]none[/dim]")
        table.add_row("Archive File", self.archive_file or "[dim]none[/dim]")
        table.add_row("Range", self.range_filter or "[dim]all[/dim]")
        table.add_row("Simulate", "Yes" if self.simulate else "No")
        table.add_row("Write Metadata", "Yes" if self.write_metadata else "No")
        table.add_row("Zip Output", "Yes" if self.zip_output else "No")
        if self.custom_options:
            table.add_row("Custom Options", ", ".join(self.custom_options))
        
        console.print(table)
        console.print()
        cmd_text = " ".join(self.build_command())
        console.print(Panel(cmd_text, title="Command Preview", border_style="dim"))


config = DownloadConfig()


def clear_screen():
    console.clear()


def header():
    console.print(Panel(
        Text("gallery-dl interactive", justify="center", style="bold cyan"),
        subtitle="[dim]q to quit | b to go back[/dim]",
        border_style="cyan"
    ))
    console.print()


def main_menu() -> Optional[str]:
    header()
    config.display()
    console.print()
    
    return questionary.select(
        "What do you want to do?",
        choices=[
            questionary.Choice("Set URL", value="url"),
            questionary.Choice("Set Destination", value="dest"),
            questionary.Choice("Configure Options", value="options"),
            questionary.Choice("Quick Presets", value="presets"),
            questionary.Choice("Run Download", value="run"),
            questionary.Choice("Simulate (dry run)", value="simulate"),
            questionary.Choice("View Supported Sites", value="sites"),
            questionary.Choice("Reset Config", value="reset"),
            questionary.Separator(),
            questionary.Choice("Quit", value="quit"),
        ],
        style=prompt_style,
        qmark="→",
    ).ask()


def set_url():
    clear_screen()
    header()
    
    url = questionary.text(
        "Enter URL to download from:",
        default=config.url,
        style=prompt_style,
        qmark="→",
    ).ask()
    
    if url and url.lower() not in ("b", "q"):
        config.url = url
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
                config.destination = suggested


def set_destination():
    clear_screen()
    header()
    
    dest = questionary.path(
        "Download destination:",
        default=config.destination,
        style=prompt_style,
        qmark="→",
    ).ask()
    
    if dest and dest.lower() not in ("b", "q"):
        config.destination = dest


def options_menu():
    while True:
        clear_screen()
        header()
        config.display()
        console.print()
        
        choice = questionary.select(
            "Configure Options:",
            choices=[
                questionary.Choice("Filename Format", value="filename"),
                questionary.Choice("Rate Limit", value="rate"),
                questionary.Choice("Sleep Between Downloads", value="sleep"),
                questionary.Choice("Retries", value="retries"),
                questionary.Choice("Browser Cookies", value="cookies"),
                questionary.Choice("Download Archive (skip duplicates)", value="archive"),
                questionary.Choice("Range Filter", value="range"),
                questionary.Choice("Write Metadata JSON", value="metadata"),
                questionary.Choice("Zip Output", value="zip"),
                questionary.Choice("Add Custom Option", value="custom"),
                questionary.Separator(),
                questionary.Choice("← Back", value="back"),
            ],
            style=prompt_style,
            qmark="→",
        ).ask()
        
        if choice == "back" or choice is None:
            break
        elif choice == "filename":
            set_filename_format()
        elif choice == "rate":
            set_rate_limit()
        elif choice == "sleep":
            set_sleep()
        elif choice == "retries":
            set_retries()
        elif choice == "cookies":
            set_cookies()
        elif choice == "archive":
            set_archive()
        elif choice == "range":
            set_range()
        elif choice == "metadata":
            config.write_metadata = not config.write_metadata
        elif choice == "zip":
            config.zip_output = not config.zip_output
        elif choice == "custom":
            add_custom_option()


def set_filename_format():
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
            config.filename_format = custom
    elif choice is not None:
        config.filename_format = choice


def set_rate_limit():
    clear_screen()
    header()
    
    console.print("[dim]Examples: 500k, 2.5M, 800k-2M (range)[/dim]")
    console.print()
    
    rate = questionary.text(
        "Rate limit (empty for unlimited):",
        default=config.rate_limit,
        style=prompt_style,
        qmark="→",
    ).ask()
    
    if rate is not None:
        config.rate_limit = rate


def set_sleep():
    clear_screen()
    header()
    
    console.print("[dim]Delay between downloads. Examples: 2.0, 1.5-3.0 (range)[/dim]")
    console.print()
    
    sleep = questionary.text(
        "Sleep seconds (empty for none):",
        default=config.sleep,
        style=prompt_style,
        qmark="→",
    ).ask()
    
    if sleep is not None:
        config.sleep = sleep


def set_retries():
    clear_screen()
    header()
    
    retries = questionary.text(
        "Max retries (-1 for infinite):",
        default=str(config.retries),
        style=prompt_style,
        qmark="→",
    ).ask()
    
    if retries:
        try:
            config.retries = int(retries)
        except ValueError:
            pass


def set_cookies():
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
        config.cookies_browser = choice


def set_archive():
    clear_screen()
    header()
    
    console.print("[dim]Archive file tracks downloaded files to skip duplicates across runs[/dim]")
    console.print()
    
    archive = questionary.path(
        "Archive file path (empty to disable):",
        default=config.archive_file or "./gallery-dl-archive.txt",
        style=prompt_style,
        qmark="→",
    ).ask()
    
    if archive is not None:
        config.archive_file = archive if archive.lower() not in ("", "none") else ""


def set_range():
    clear_screen()
    header()
    
    console.print("[dim]Download only specific items. Examples: 1-10, 5, 1:100:2 (every 2nd)[/dim]")
    console.print()
    
    range_val = questionary.text(
        "Range filter (empty for all):",
        default=config.range_filter,
        style=prompt_style,
        qmark="→",
    ).ask()
    
    if range_val is not None:
        config.range_filter = range_val


def add_custom_option():
    clear_screen()
    header()
    
    console.print("[dim]Format: key=value (e.g., browser=firefox, sleep-request=1.0)[/dim]")
    console.print()
    
    if config.custom_options:
        console.print(f"Current custom options: {', '.join(config.custom_options)}")
        console.print()
    
    opt = questionary.text(
        "Add custom option:",
        style=prompt_style,
        qmark="→",
    ).ask()
    
    if opt and "=" in opt:
        config.custom_options.append(opt)


def presets_menu():
    clear_screen()
    header()
    
    choice = questionary.select(
        "Quick Presets:",
        choices=[
            questionary.Choice("Instagram Profile (public)", value="instagram"),
            questionary.Choice("Twitter/X Profile", value="twitter"),
            questionary.Choice("Reddit User/Subreddit", value="reddit"),
            questionary.Choice("Tumblr Blog", value="tumblr"),
            questionary.Choice("Slow & Polite (rate limited)", value="polite"),
            questionary.Choice("Archive Mode (track downloads)", value="archive"),
            questionary.Separator(),
            questionary.Choice("← Back", value="back"),
        ],
        style=prompt_style,
        qmark="→",
    ).ask()
    
    if choice == "instagram":
        console.print()
        username = questionary.text(
            "Instagram username:",
            style=prompt_style,
            qmark="→",
        ).ask()
        if username:
            config.url = f"https://instagram.com/{username.lstrip('@')}"
            config.destination = f"./{username.lstrip('@')}_instagram"
            config.sleep = "1.0-2.0"
            config.filename_format = "{date:%Y-%m-%d}_{filename}"
    
    elif choice == "twitter":
        console.print()
        username = questionary.text(
            "Twitter/X username:",
            style=prompt_style,
            qmark="→",
        ).ask()
        if username:
            config.url = f"https://twitter.com/{username.lstrip('@')}/media"
            config.destination = f"./{username.lstrip('@')}_twitter"
    
    elif choice == "reddit":
        console.print()
        target = questionary.text(
            "Subreddit or user (e.g., r/pics or u/username):",
            style=prompt_style,
            qmark="→",
        ).ask()
        if target:
            config.url = f"https://reddit.com/{target}"
            config.destination = f"./{target.replace('/', '_')}_reddit"
    
    elif choice == "tumblr":
        console.print()
        blog = questionary.text(
            "Tumblr blog name:",
            style=prompt_style,
            qmark="→",
        ).ask()
        if blog:
            config.url = f"https://{blog}.tumblr.com"
            config.destination = f"./{blog}_tumblr"
    
    elif choice == "polite":
        config.sleep = "2.0-4.0"
        config.rate_limit = "500k"
        config.retries = 2
    
    elif choice == "archive":
        config.archive_file = "./gallery-dl-archive.txt"
        config.write_metadata = True


def run_download(simulate: bool = False):
    clear_screen()
    header()
    
    if not config.url:
        console.print("[red]Error: No URL set[/red]")
        questionary.press_any_key_to_continue(style=prompt_style).ask()
        return
    
    config.simulate = simulate
    cmd = config.build_command()
    
    console.print(Panel(" ".join(cmd), title="Executing", border_style="green" if not simulate else "yellow"))
    console.print()
    
    if not simulate:
        # Create destination directory
        Path(config.destination).mkdir(parents=True, exist_ok=True)
    
    try:
        process = subprocess.run(cmd, check=False)
        console.print()
        if process.returncode == 0:
            console.print("[green]✓ Complete[/green]")
        else:
            console.print(f"[yellow]Finished with return code {process.returncode}[/yellow]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    
    config.simulate = False
    console.print()
    questionary.press_any_key_to_continue(style=prompt_style).ask()


def view_sites():
    clear_screen()
    header()
    
    console.print("[dim]Fetching supported extractors...[/dim]")
    result = subprocess.run(
        ["gallery-dl", "--list-extractors"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        lines = result.stdout.strip().split("\n")
        # Group by first letter for easier browsing
        console.print(f"\n[bold]Supported sites ({len(lines)} extractors):[/bold]\n")
        
        # Just show first 50 as a sample
        for line in lines[:50]:
            console.print(f"  {line}")
        
        if len(lines) > 50:
            console.print(f"\n  [dim]... and {len(lines) - 50} more[/dim]")
    
    console.print()
    questionary.press_any_key_to_continue(style=prompt_style).ask()


def reset_config():
    global config
    config = DownloadConfig()


def main():
    while True:
        clear_screen()
        choice = main_menu()
        
        if choice is None or choice == "quit":
            clear_screen()
            console.print("[cyan]Goodbye![/cyan]")
            break
        elif choice == "url":
            set_url()
        elif choice == "dest":
            set_destination()
        elif choice == "options":
            options_menu()
        elif choice == "presets":
            presets_menu()
        elif choice == "run":
            run_download(simulate=False)
        elif choice == "simulate":
            run_download(simulate=True)
        elif choice == "sites":
            view_sites()
        elif choice == "reset":
            reset_config()


if __name__ == "__main__":
    main()