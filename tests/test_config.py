"""
Tests for insta-mash configuration system.
"""

import tempfile
from pathlib import Path

import pytest

from insta_mash.config import (PRESETS, Config, DownloadOptions, Profile,
                               validate_options)


class TestDownloadOptions:
    """Tests for DownloadOptions dataclass."""

    def test_default_values(self):
        opts = DownloadOptions()
        assert opts.destination == "./downloads"
        assert opts.retries == 4
        assert opts.sleep == ""
        assert opts.write_metadata is False

    def test_merge_prefers_non_empty(self):
        base = DownloadOptions(destination="./base", sleep="1.0")
        override = DownloadOptions(sleep="2.0")

        merged = base.merge(override)

        assert merged.destination == "./base"  # from base
        assert merged.sleep == "2.0"  # from override

    def test_merge_extends_lists(self):
        base = DownloadOptions(extra_options=["a=1"])
        override = DownloadOptions(extra_options=["b=2"])

        merged = base.merge(override)

        assert merged.extra_options == ["a=1", "b=2"]

    def test_to_gallery_dl_args(self):
        opts = DownloadOptions(
            destination="./test",
            sleep="1.0-2.0",
            retries=3,
            write_metadata=True,
        )

        args = opts.to_gallery_dl_args()

        assert "-D" in args
        assert "./test" in args
        assert "--sleep" in args
        assert "1.0-2.0" in args
        assert "-R" in args
        assert "3" in args
        assert "--write-metadata" in args

    def test_to_dict_excludes_defaults(self):
        opts = DownloadOptions(sleep="2.0")
        d = opts.to_dict()

        assert "sleep" in d
        assert "retries" not in d  # default value excluded


class TestConfig:
    """Tests for Config class."""

    def test_load_nonexistent_returns_defaults(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nonexistent.toml"
            config = Config.load(path)

            assert config.defaults.destination == "./downloads"
            assert len(config.profiles) == 0

    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.toml"

            # Create and save
            config = Config()
            config.defaults.sleep = "2.0"
            config.add_profile("test", DownloadOptions(rate_limit="500k"), "Test profile")
            config.save(path)

            # Load and verify
            loaded = Config.load(path)
            assert loaded.defaults.sleep == "2.0"
            assert "test" in loaded.profiles
            assert loaded.profiles["test"].options.rate_limit == "500k"

    def test_profile_inheritance(self):
        config = Config()
        config.add_profile("base", DownloadOptions(sleep="1.0", retries=3))
        config.profiles["child"] = Profile(
            name="child",
            extends="base",
            options=DownloadOptions(sleep="2.0"),
        )

        resolved = config.get_profile("child")

        assert resolved is not None
        assert resolved.options.sleep == "2.0"  # overridden
        assert resolved.options.retries == 3  # inherited

    def test_resolve_options_priority(self):
        config = Config()
        config.defaults.sleep = "1.0"
        config.add_profile("slow", DownloadOptions(sleep="3.0"))

        cli_opts = DownloadOptions(sleep="5.0")

        _, options = config.resolve_options(
            profile_name="slow",
            cli_options=cli_opts,
        )

        # CLI should win
        assert options.sleep == "5.0"


class TestPresets:
    """Tests for built-in presets."""

    def test_instagram_preset_exists(self):
        assert "instagram" in PRESETS

    def test_instagram_preset_apply(self):
        preset = PRESETS["instagram"]
        url, opts = preset.apply("testuser")

        assert url == "https://instagram.com/testuser"
        assert opts.destination == "./testuser_instagram"
        assert opts.sleep == "1.0-2.0"

    def test_polite_preset_has_no_url(self):
        preset = PRESETS["polite"]
        url, opts = preset.apply()

        assert url == ""
        assert opts.sleep == "2.0-4.0"


class TestValidation:
    """Tests for option validation."""

    def test_valid_options_no_errors(self):
        opts = DownloadOptions(
            sleep="1.0-2.0",
            rate_limit="500k",
            retries=3,
        )
        errors = validate_options(opts)
        assert len(errors) == 0

    def test_invalid_sleep_format(self):
        opts = DownloadOptions(sleep="invalid")
        errors = validate_options(opts)

        assert len(errors) == 1
        assert errors[0].field == "sleep"

    def test_invalid_rate_limit_format(self):
        opts = DownloadOptions(rate_limit="fast")
        errors = validate_options(opts)

        assert len(errors) == 1
        assert errors[0].field == "rate_limit"

    def test_invalid_retries(self):
        opts = DownloadOptions(retries=-5)
        errors = validate_options(opts)

        assert len(errors) == 1
        assert errors[0].field == "retries"

    def test_invalid_browser(self):
        opts = DownloadOptions(cookies_browser="netscape")
        errors = validate_options(opts)

        assert len(errors) == 1
        assert errors[0].field == "cookies_browser"
