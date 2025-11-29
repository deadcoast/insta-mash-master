"""
insta-mash configuration system

Handles loading, saving, and validating configuration from TOML files.
Supports profiles, XDG paths, and environment variable overrides.
"""

from __future__ import annotations

import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore

import tomli_w

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def get_config_dir() -> Path:
    """Get config directory following XDG spec."""
    if xdg := os.environ.get("XDG_CONFIG_HOME"):
        return Path(xdg) / "insta-mash"

    if sys.platform == "darwin":
        return Path.home() / ".config" / "insta-mash"
    elif sys.platform == "win32":
        return Path(os.environ.get("APPDATA", Path.home())) / "insta-mash"
    else:
        return Path.home() / ".config" / "insta-mash"


def get_data_dir() -> Path:
    """Get data directory for archives and caches."""
    if xdg := os.environ.get("XDG_DATA_HOME"):
        return Path(xdg) / "insta-mash"

    if sys.platform == "darwin":
        return Path.home() / ".local" / "share" / "insta-mash"
    elif sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "insta-mash"
    else:
        return Path.home() / ".local" / "share" / "insta-mash"


def get_config_path() -> Path:
    """Get path to main config file."""
    return get_config_dir() / "config.toml"


def get_default_archive_path() -> Path:
    """Get default path for download archive."""
    return get_data_dir() / "archive.txt"


# ---------------------------------------------------------------------------
# Config Schema
# ---------------------------------------------------------------------------

@dataclass
class DownloadOptions:
    """Options that control download behavior."""

    destination: str = "./downloads"
    filename_format: str = ""
    rate_limit: str = ""
    sleep: str = ""
    sleep_request: str = ""
    retries: int = 4
    timeout: float = 30.0

    cookies_browser: str = ""
    cookies_file: str = ""

    archive_file: str = ""
    range_filter: str = ""
    filesize_min: str = ""
    filesize_max: str = ""

    write_metadata: bool = False
    zip_output: bool = False
    no_skip: bool = False
    no_mtime: bool = False

    user_agent: str = ""
    proxy: str = ""

    # gallery-dl passthrough options (key=value strings)
    extra_options: list[str] = field(default_factory=list)

    def merge(self, other: DownloadOptions) -> DownloadOptions:
        """Merge another options object, non-empty values from other take precedence."""
        result = DownloadOptions()
        for key in self.__dataclass_fields__:
            self_val = getattr(self, key)
            other_val = getattr(other, key)

            # For strings, non-empty other wins
            if isinstance(self_val, str):
                setattr(result, key, other_val if other_val else self_val)
            # For lists, extend
            elif isinstance(self_val, list):
                setattr(result, key, self_val + other_val)
            # For bools, other wins if True
            elif isinstance(self_val, bool):
                setattr(result, key, other_val if other_val else self_val)
            # For numbers, non-default other wins
            else:
                default = self.__dataclass_fields__[key].default
                setattr(result, key, other_val if other_val != default else self_val)

        return result

    def to_gallery_dl_args(self) -> list[str]:
        """Convert to gallery-dl command line arguments."""
        args = []

        if self.destination:
            args.extend(["-D", os.path.expanduser(self.destination)])
        if self.filename_format:
            args.extend(["-f", self.filename_format])
        if self.rate_limit:
            args.extend(["-r", self.rate_limit])
        if self.sleep:
            args.extend(["--sleep", self.sleep])
        if self.sleep_request:
            args.extend(["--sleep-request", self.sleep_request])
        if self.retries != 4:
            args.extend(["-R", str(self.retries)])
        if self.timeout != 30.0:
            args.extend(["--http-timeout", str(self.timeout)])
        if self.cookies_browser:
            args.extend(["--cookies-from-browser", self.cookies_browser])
        if self.cookies_file:
            args.extend(["-C", os.path.expanduser(self.cookies_file)])
        if self.archive_file:
            args.extend(["--download-archive", os.path.expanduser(self.archive_file)])
        if self.range_filter:
            args.extend(["--range", self.range_filter])
        if self.filesize_min:
            args.extend(["--filesize-min", self.filesize_min])
        if self.filesize_max:
            args.extend(["--filesize-max", self.filesize_max])
        if self.write_metadata:
            args.append("--write-metadata")
        if self.zip_output:
            args.append("--zip")
        if self.no_skip:
            args.append("--no-skip")
        if self.no_mtime:
            args.append("--no-mtime")
        if self.user_agent:
            args.extend(["-a", self.user_agent])
        if self.proxy:
            args.extend(["--proxy", self.proxy])
        for opt in self.extra_options:
            args.extend(["-o", opt])

        return args

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        d = asdict(self)
        # Remove default/empty values for cleaner output
        return {k: v for k, v in d.items() if v and v != self.__dataclass_fields__[k].default}


@dataclass
class Profile:
    """A named configuration profile."""

    name: str
    description: str = ""
    options: DownloadOptions = field(default_factory=DownloadOptions)
    extends: str = ""  # Name of profile to inherit from

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.description:
            d["description"] = self.description
        if self.extends:
            d["extends"] = self.extends
        d.update(self.options.to_dict())
        return d


@dataclass
class Preset:
    """Built-in platform presets."""

    name: str
    description: str
    url_template: str  # e.g., "https://instagram.com/{target}"
    destination_template: str  # e.g., "./{target}_instagram"
    options: DownloadOptions = field(default_factory=DownloadOptions)

    def apply(self, target: str = "") -> tuple[str, DownloadOptions]:
        """Apply preset, returning (url, options) tuple."""
        url = self.url_template.format(target=target) if target else ""
        opts = DownloadOptions(
            destination=self.destination_template.format(target=target) if target else self.options.destination,
            **{k: v for k, v in asdict(self.options).items() if k != "destination"}
        )
        return url, opts


# ---------------------------------------------------------------------------
# Built-in Presets
# ---------------------------------------------------------------------------

PRESETS: dict[str, Preset] = {
    "instagram": Preset(
        name="instagram",
        description="Instagram profile - public posts with polite delays",
        url_template="https://instagram.com/{target}",
        destination_template="./{target}_instagram",
        options=DownloadOptions(
            sleep="1.0-2.0",
            filename_format="{date:%Y-%m-%d}_{filename}",
        ),
    ),
    "instagram-stories": Preset(
        name="instagram-stories",
        description="Instagram stories (requires auth)",
        url_template="https://instagram.com/{target}/stories",
        destination_template="./{target}_instagram_stories",
        options=DownloadOptions(
            sleep="1.0-2.0",
        ),
    ),
    "instagram-reels": Preset(
        name="instagram-reels",
        description="Instagram reels",
        url_template="https://instagram.com/{target}/reels",
        destination_template="./{target}_instagram_reels",
        options=DownloadOptions(
            sleep="1.5-3.0",
        ),
    ),
    "twitter": Preset(
        name="twitter",
        description="Twitter/X media timeline",
        url_template="https://twitter.com/{target}/media",
        destination_template="./{target}_twitter",
        options=DownloadOptions(
            filename_format="/O",
        ),
    ),
    "reddit": Preset(
        name="reddit",
        description="Reddit subreddit or user",
        url_template="https://reddit.com/{target}",
        destination_template="./{target}_reddit",
        options=DownloadOptions(
            sleep="0.5-1.0",
        ),
    ),
    "tumblr": Preset(
        name="tumblr",
        description="Tumblr blog archive",
        url_template="https://{target}.tumblr.com",
        destination_template="./{target}_tumblr",
        options=DownloadOptions(
            write_metadata=True,
        ),
    ),
    "polite": Preset(
        name="polite",
        description="Rate-limited, polite scraping",
        url_template="",
        destination_template="",
        options=DownloadOptions(
            sleep="2.0-4.0",
            sleep_request="1.0",
            rate_limit="500k",
            retries=2,
        ),
    ),
    "archive": Preset(
        name="archive",
        description="Track downloads to skip duplicates",
        url_template="",
        destination_template="",
        options=DownloadOptions(
            archive_file=str(get_default_archive_path()),
            write_metadata=True,
        ),
    ),
    "fast": Preset(
        name="fast",
        description="No delays, parallel where possible",
        url_template="",
        destination_template="",
        options=DownloadOptions(
            sleep="",
            retries=2,
        ),
    ),
}


# ---------------------------------------------------------------------------
# Config Class
# ---------------------------------------------------------------------------

@dataclass
class Config:
    """Main configuration container."""

    defaults: DownloadOptions = field(default_factory=DownloadOptions)
    profiles: dict[str, Profile] = field(default_factory=dict)

    # Runtime state (not persisted)
    _path: Path = field(default_factory=get_config_path, repr=False)
    _dirty: bool = field(default=False, repr=False)

    @classmethod
    def load(cls, path: Optional[Path] = None) -> Config:
        """Load config from TOML file."""
        path = path or get_config_path()

        if not path.exists():
            config = cls()
            config._path = path
            return config

        with open(path, "rb") as f:
            data = tomllib.load(f)

        config = cls._from_dict(data)
        config._path = path
        return config

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> Config:
        """Create config from dictionary."""
        defaults_data = data.get("defaults", {})
        defaults = DownloadOptions(**{
            k: v for k, v in defaults_data.items()
            if k in DownloadOptions.__dataclass_fields__
        })

        profiles = {}
        for name, profile_data in data.get("profiles", {}).items():
            opts_data = {k: v for k, v in profile_data.items()
                        if k in DownloadOptions.__dataclass_fields__}
            profiles[name] = Profile(
                name=name,
                description=profile_data.get("description", ""),
                extends=profile_data.get("extends", ""),
                options=DownloadOptions(**opts_data),
            )

        return cls(defaults=defaults, profiles=profiles)

    def save(self, path: Optional[Path] = None) -> None:
        """Save config to TOML file."""
        path = path or self._path
        path.parent.mkdir(parents=True, exist_ok=True)

        data = self._to_dict()

        with open(path, "wb") as f:
            tomli_w.dump(data, f)

        self._dirty = False

    def _to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        data: dict[str, Any] = {}

        defaults_dict = self.defaults.to_dict()
        if defaults_dict:
            data["defaults"] = defaults_dict

        if self.profiles:
            data["profiles"] = {
                name: profile.to_dict()
                for name, profile in self.profiles.items()
            }

        return data

    def get_profile(self, name: str) -> Optional[Profile]:
        """Get a profile by name, resolving inheritance."""
        if name not in self.profiles:
            return None

        profile = self.profiles[name]

        # Resolve inheritance
        if profile.extends:
            parent = self.get_profile(profile.extends)
            if parent:
                merged_opts = parent.options.merge(profile.options)
                return Profile(
                    name=profile.name,
                    description=profile.description,
                    options=merged_opts,
                )

        return profile

    def resolve_options(
        self,
        profile_name: str = "",
        preset_name: str = "",
        cli_options: Optional[DownloadOptions] = None,
        target: str = "",
    ) -> tuple[str, DownloadOptions]:
        """
        Resolve final options from defaults, profile, preset, and CLI overrides.

        Priority (lowest to highest):
        1. Built-in defaults
        2. Config file defaults
        3. Profile options
        4. Preset options
        5. CLI options

        Returns (url, options) tuple.
        """
        url = ""
        options = DownloadOptions()

        # Apply config defaults
        options = options.merge(self.defaults)

        # Apply profile
        if profile_name:
            profile = self.get_profile(profile_name)
            if profile:
                options = options.merge(profile.options)

        # Apply preset
        if preset_name and preset_name in PRESETS:
            preset = PRESETS[preset_name]
            url, preset_opts = preset.apply(target)
            options = options.merge(preset_opts)

        # Apply CLI overrides
        if cli_options:
            options = options.merge(cli_options)

        return url, options

    def add_profile(self, name: str, options: DownloadOptions, description: str = "") -> None:
        """Add or update a profile."""
        self.profiles[name] = Profile(name=name, description=description, options=options)
        self._dirty = True

    def delete_profile(self, name: str) -> bool:
        """Delete a profile. Returns True if deleted."""
        if name in self.profiles:
            del self.profiles[name]
            self._dirty = True
            return True
        return False

    def set_default(self, key: str, value: Any) -> bool:
        """Set a default option. Returns True if valid key."""
        if key not in DownloadOptions.__dataclass_fields__:
            return False

        setattr(self.defaults, key, value)
        self._dirty = True
        return True

    def unset_default(self, key: str) -> bool:
        """Reset a default to its original value."""
        if key not in DownloadOptions.__dataclass_fields__:
            return False

        default_val = DownloadOptions.__dataclass_fields__[key].default
        if default_val is not None:
            setattr(self.defaults, key, default_val)
        else:
            # Handle fields with default_factory
            factory = DownloadOptions.__dataclass_fields__[key].default_factory
            if factory is not None:
                setattr(self.defaults, key, factory())

        self._dirty = True
        return True


# ---------------------------------------------------------------------------
# Environment Variable Overrides
# ---------------------------------------------------------------------------

ENV_PREFIX = "MASH_"

ENV_MAPPINGS = {
    "DESTINATION": "destination",
    "SLEEP": "sleep",
    "RATE_LIMIT": "rate_limit",
    "RETRIES": "retries",
    "COOKIES_BROWSER": "cookies_browser",
    "ARCHIVE": "archive_file",
    "PROXY": "proxy",
}


def apply_env_overrides(options: DownloadOptions) -> DownloadOptions:
    """Apply environment variable overrides to options."""
    for env_key, opt_key in ENV_MAPPINGS.items():
        env_var = f"{ENV_PREFIX}{env_key}"
        if value := os.environ.get(env_var):
            if opt_key == "retries":
                setattr(options, opt_key, int(value))
            else:
                setattr(options, opt_key, value)

    return options


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

@dataclass
class ValidationError:
    """A configuration validation error."""
    field: str
    message: str
    value: Any = None


def validate_options(options: DownloadOptions) -> list[ValidationError]:
    """Validate download options, returning list of errors."""
    errors = []

    # Validate rate limit format
    if options.rate_limit:
        import re
        if not re.match(r"^\d+(\.\d+)?[kmg]?(-\d+(\.\d+)?[kmg]?)?$", options.rate_limit, re.I):
            errors.append(ValidationError(
                field="rate_limit",
                message="Invalid format. Use: 500k, 2.5M, or 800k-2M",
                value=options.rate_limit,
            ))

    # Validate sleep format
    if options.sleep:
        import re
        if not re.match(r"^\d+(\.\d+)?(-\d+(\.\d+)?)?$", options.sleep):
            errors.append(ValidationError(
                field="sleep",
                message="Invalid format. Use: 2.0 or 1.5-3.0",
                value=options.sleep,
            ))

    # Validate retries
    if options.retries < -1:
        errors.append(ValidationError(
            field="retries",
            message="Must be -1 (infinite) or >= 0",
            value=options.retries,
        ))

    # Validate timeout
    if options.timeout <= 0:
        errors.append(ValidationError(
            field="timeout",
            message="Must be positive",
            value=options.timeout,
        ))

    # Validate range filter
    if options.range_filter:
        import re
        if not re.match(r"^(\d+(-\d+)?|\d+:\d*(:\d+)?)$", options.range_filter):
            errors.append(ValidationError(
                field="range_filter",
                message="Invalid format. Use: 5, 8-20, or 1:24:3",
                value=options.range_filter,
            ))

    # Validate browser name
    valid_browsers = {"chrome", "firefox", "safari", "edge", "brave", "opera", "chromium", ""}
    if options.cookies_browser and options.cookies_browser.split("/")[0].lower() not in valid_browsers:
        errors.append(ValidationError(
            field="cookies_browser",
            message=f"Unknown browser. Valid: {', '.join(sorted(valid_browsers - {''}))}",
            value=options.cookies_browser,
        ))

    return errors


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------

_config: Optional[Config] = None


def get_config() -> Config:
    """Get or load the global config instance."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config() -> Config:
    """Force reload config from disk."""
    global _config
    _config = Config.load()
    return _config


def get_preset(name: str) -> Optional[Preset]:
    """Get a built-in preset by name."""
    return PRESETS.get(name)


def list_presets() -> list[str]:
    """List available preset names."""
    return list(PRESETS.keys())
