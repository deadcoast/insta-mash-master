"""
insta-mash - The simple but comprehensive scraping wrapper.
"""

__version__ = "0.1.0"
__author__ = "Heat"

from insta_mash.config import (PRESETS, Config, DownloadOptions, Preset,
                               Profile, get_config, get_config_dir,
                               get_config_path, get_data_dir, get_preset,
                               list_presets, reload_config, validate_options)

__all__ = [
    "__version__",
    "Config",
    "DownloadOptions",
    "Profile",
    "Preset",
    "PRESETS",
    "get_config",
    "reload_config",
    "get_preset",
    "list_presets",
    "get_config_dir",
    "get_config_path",
    "get_data_dir",
    "validate_options",
]
