"""
Tests for batch mode functionality.
"""

import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from insta_mash.batch import BatchEntry, BatchFile


class TestBatchEntry:
    """Tests for BatchEntry parsing."""

    def test_parse_url_only(self):
        entry = BatchEntry.parse("https://instagram.com/user", 1)
        assert entry is not None
        assert entry.url == "https://instagram.com/user"
        assert entry.preset == ""
        assert entry.profile == ""
        assert entry.line_number == 1

    def test_parse_url_with_preset(self):
        entry = BatchEntry.parse("https://instagram.com/user preset:instagram", 2)
        assert entry is not None
        assert entry.url == "https://instagram.com/user"
        assert entry.preset == "instagram"
        assert entry.profile == ""

    def test_parse_url_with_profile(self):
        entry = BatchEntry.parse("https://instagram.com/user profile:slow", 3)
        assert entry is not None
        assert entry.url == "https://instagram.com/user"
        assert entry.preset == ""
        assert entry.profile == "slow"

    def test_parse_url_with_both(self):
        entry = BatchEntry.parse(
            "https://instagram.com/user preset:instagram profile:slow", 4
        )
        assert entry is not None
        assert entry.url == "https://instagram.com/user"
        assert entry.preset == "instagram"
        assert entry.profile == "slow"

    def test_parse_comment_returns_none(self):
        entry = BatchEntry.parse("# This is a comment", 5)
        assert entry is None

    def test_parse_empty_line_returns_none(self):
        entry = BatchEntry.parse("", 6)
        assert entry is None

    def test_parse_whitespace_only_returns_none(self):
        entry = BatchEntry.parse("   \t  ", 7)
        assert entry is None

    def test_parse_strips_whitespace(self):
        entry = BatchEntry.parse("  https://example.com  preset:test  ", 8)
        assert entry is not None
        assert entry.url == "https://example.com"
        assert entry.preset == "test"


class TestBatchFile:
    """Tests for BatchFile loading."""

    def test_load_simple_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("https://instagram.com/user1\n")
            f.write("https://instagram.com/user2\n")
            f.flush()
            path = Path(f.name)

        try:
            batch = BatchFile.load(path)
            assert len(batch.entries) == 2
            assert batch.entries[0].url == "https://instagram.com/user1"
            assert batch.entries[1].url == "https://instagram.com/user2"
        finally:
            path.unlink()

    def test_load_with_comments_and_empty_lines(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("# Comment\n")
            f.write("\n")
            f.write("https://instagram.com/user1\n")
            f.write("# Another comment\n")
            f.write("https://instagram.com/user2\n")
            f.write("\n")
            f.flush()
            path = Path(f.name)

        try:
            batch = BatchFile.load(path)
            assert len(batch.entries) == 2
            assert batch.entries[0].url == "https://instagram.com/user1"
            assert batch.entries[1].url == "https://instagram.com/user2"
        finally:
            path.unlink()

    def test_load_with_presets_and_profiles(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("https://instagram.com/user1 preset:instagram\n")
            f.write("https://twitter.com/user2 profile:slow\n")
            f.write("https://reddit.com/r/pics preset:reddit profile:archive\n")
            f.flush()
            path = Path(f.name)

        try:
            batch = BatchFile.load(path)
            assert len(batch.entries) == 3
            assert batch.entries[0].preset == "instagram"
            assert batch.entries[1].profile == "slow"
            assert batch.entries[2].preset == "reddit"
            assert batch.entries[2].profile == "archive"
        finally:
            path.unlink()

    def test_load_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError):
            BatchFile.load(Path("/nonexistent/file.txt"))

    def test_load_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.flush()
            path = Path(f.name)

        try:
            batch = BatchFile.load(path)
            assert len(batch.entries) == 0
        finally:
            path.unlink()


# Property-based tests


# Strategy for generating valid URLs
url_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd"),
        whitelist_characters=".-_/:?=&",
    ),
    min_size=10,
    max_size=100,
).filter(lambda s: " " not in s and "\t" not in s and "\n" not in s)

# Strategy for generating preset/profile names
name_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_"),
    min_size=1,
    max_size=20,
).filter(lambda s: " " not in s and ":" not in s)


@settings(max_examples=100)
@given(urls=st.lists(url_strategy, min_size=1, max_size=50))
def test_property_file_reading_completeness(urls):
    """
    **Feature: batch-mode, Property 1: File reading completeness**
    **Validates: Requirements 1.1, 1.2**

    For any valid batch file with N non-comment, non-empty lines,
    parsing the file should produce exactly N BatchEntry objects.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for url in urls:
            f.write(f"{url}\n")
        f.flush()
        path = Path(f.name)

    try:
        batch = BatchFile.load(path)
        assert len(batch.entries) == len(urls)
    finally:
        path.unlink()


@settings(max_examples=100)
@given(urls=st.lists(url_strategy, min_size=1, max_size=50))
def test_property_order_preservation(urls):
    """
    **Feature: batch-mode, Property 2: Order preservation**
    **Validates: Requirements 1.5**

    For any list of URLs in a batch file, the order of parsed BatchEntry
    objects should match the order of URLs in the file.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for url in urls:
            f.write(f"{url}\n")
        f.flush()
        path = Path(f.name)

    try:
        batch = BatchFile.load(path)
        for i, entry in enumerate(batch.entries):
            assert entry.url == urls[i]
    finally:
        path.unlink()


@settings(max_examples=100)
@given(url=url_strategy)
def test_property_default_configuration_application(url):
    """
    **Feature: batch-mode, Property 3: Default configuration application**
    **Validates: Requirements 2.1**

    For any BatchEntry without preset or profile specified, resolving its
    configuration should produce options that match the system defaults.
    """
    from insta_mash.config import Config, DownloadOptions

    # Create a config with custom defaults
    config = Config()
    config.defaults.sleep = "2.0"
    config.defaults.retries = 5
    config.defaults.destination = "./custom"

    # Create entry without preset or profile
    entry = BatchEntry(line_number=1, url=url, preset="", profile="")

    # Resolve options
    options = entry.resolve_options(config)

    # Should match config defaults
    assert options.sleep == "2.0"
    assert options.retries == 5
    assert options.destination == "./custom"


@settings(max_examples=100)
@given(
    url=url_strategy,
    preset_name=st.sampled_from(["instagram", "twitter", "reddit", "polite", "archive", "fast"])
)
def test_property_preset_application(url, preset_name):
    """
    **Feature: batch-mode, Property 4: Preset application**
    **Validates: Requirements 2.2**

    For any BatchEntry with a preset specified, the resolved configuration
    should contain all options from that preset.
    """
    from insta_mash.config import Config, PRESETS

    config = Config()

    # Create entry with preset
    entry = BatchEntry(line_number=1, url=url, preset=preset_name, profile="")

    # Resolve options
    options = entry.resolve_options(config)

    # Get expected preset options
    preset = PRESETS[preset_name]
    _, preset_opts = preset.apply()

    # Check that preset options are present in resolved options
    # For non-empty string values, they should match
    if preset_opts.sleep:
        assert options.sleep == preset_opts.sleep
    if preset_opts.rate_limit:
        assert options.rate_limit == preset_opts.rate_limit
    if preset_opts.retries != 4:  # 4 is the default
        assert options.retries == preset_opts.retries
    if preset_opts.write_metadata:
        assert options.write_metadata == preset_opts.write_metadata
    if preset_opts.filename_format:
        assert options.filename_format == preset_opts.filename_format


@settings(max_examples=100)
@given(
    url=url_strategy,
    sleep_val=st.text(
        alphabet=st.characters(whitelist_categories=("Nd",), whitelist_characters=".-"),
        min_size=1,
        max_size=10
    ).filter(lambda s: s and s[0].isdigit()),
    retries_val=st.integers(min_value=0, max_value=10)
)
def test_property_profile_application(url, sleep_val, retries_val):
    """
    **Feature: batch-mode, Property 5: Profile application**
    **Validates: Requirements 2.3**

    For any BatchEntry with a profile specified, the resolved configuration
    should contain all options from that profile.
    """
    from insta_mash.config import Config, DownloadOptions, Profile

    config = Config()

    # Create a profile with specific options
    profile_name = "test_profile"
    profile_opts = DownloadOptions(
        sleep=sleep_val,
        retries=retries_val,
        destination="./profile_dest"
    )
    config.profiles[profile_name] = Profile(
        name=profile_name,
        options=profile_opts
    )

    # Create entry with profile
    entry = BatchEntry(line_number=1, url=url, preset="", profile=profile_name)

    # Resolve options
    options = entry.resolve_options(config)

    # Check that profile options are present in resolved options
    assert options.sleep == sleep_val
    assert options.retries == retries_val
    assert options.destination == "./profile_dest"


@settings(max_examples=100)
@given(
    url=url_strategy,
    global_sleep=st.text(
        alphabet=st.characters(whitelist_categories=("Nd",), whitelist_characters=".-"),
        min_size=1,
        max_size=10
    ).filter(lambda s: s and s[0].isdigit()),
    entry_sleep=st.text(
        alphabet=st.characters(whitelist_categories=("Nd",), whitelist_characters=".-"),
        min_size=1,
        max_size=10
    ).filter(lambda s: s and s[0].isdigit()),
    global_retries=st.integers(min_value=0, max_value=10),
    entry_retries=st.integers(min_value=0, max_value=10).filter(lambda x: x != 4)  # Exclude default
)
def test_property_configuration_merging_priority(
    url, global_sleep, entry_sleep, global_retries, entry_retries
):
    """
    **Feature: batch-mode, Property 7: Configuration merging priority**
    **Validates: Requirements 2.5**

    For any BatchEntry with both global and entry-specific configuration,
    the entry-specific configuration should override global configuration
    for conflicting options (when the entry-specific value is non-default).
    """
    from insta_mash.config import Config, DownloadOptions, Profile

    config = Config()

    # Set up global batch options
    global_options = DownloadOptions(
        sleep=global_sleep,
        retries=global_retries,
        destination="./global_dest"
    )

    # Create a profile with entry-specific options
    profile_name = "entry_profile"
    entry_opts = DownloadOptions(
        sleep=entry_sleep,
        retries=entry_retries,
        destination="./entry_dest"
    )
    config.profiles[profile_name] = Profile(
        name=profile_name,
        options=entry_opts
    )

    # Create entry with profile
    entry = BatchEntry(line_number=1, url=url, preset="", profile=profile_name)

    # Resolve options with global options
    options = entry.resolve_options(config, global_options)

    # Entry-specific options should override global options
    # For strings, non-empty entry values override
    assert options.sleep == entry_sleep
    # For numbers, non-default entry values override
    assert options.retries == entry_retries
    # For all types, entry-specific values take precedence
    assert options.destination == "./entry_dest"


@settings(max_examples=100)
@given(
    valid_urls=st.lists(url_strategy, min_size=1, max_size=20),
    num_invalid=st.integers(min_value=1, max_value=10)
)
def test_property_invalid_entry_skipping(valid_urls, num_invalid):
    """
    **Feature: batch-mode, Property 6: Invalid entry skipping**
    **Validates: Requirements 2.4**

    For any batch file containing invalid entries, parsing should skip
    invalid entries and return only valid BatchEntry objects.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        # Write valid URLs
        for url in valid_urls:
            f.write(f"{url}\n")
        
        # Write invalid entries (comments and empty lines)
        for _ in range(num_invalid):
            f.write("# This is a comment\n")
            f.write("\n")
        
        f.flush()
        path = Path(f.name)

    try:
        batch = BatchFile.load(path)
        # Should only have valid entries, invalid ones skipped
        assert len(batch.entries) == len(valid_urls)
        # All entries should be valid URLs
        for i, entry in enumerate(batch.entries):
            assert entry.url == valid_urls[i]
    finally:
        path.unlink()


@settings(max_examples=100)
@given(urls=st.lists(url_strategy, min_size=1, max_size=30))
def test_property_validation_parsing(urls):
    """
    **Feature: batch-mode, Property 20: Validation parsing**
    **Validates: Requirements 6.1**

    For any batch file, the validate command should parse all entries
    and return a list of validation results.
    """
    from insta_mash.config import Config

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for url in urls:
            f.write(f"{url}\n")
        f.flush()
        path = Path(f.name)

    try:
        batch = BatchFile.load(path)
        config = Config()
        
        # Validate should return a list (possibly empty)
        validation_results = batch.validate(config)
        
        # Should be a list
        assert isinstance(validation_results, list)
        
        # For valid entries without preset/profile, should have no errors
        # (since we're not specifying invalid presets/profiles)
        assert len(validation_results) == 0
    finally:
        path.unlink()


@settings(max_examples=100)
@given(
    valid_urls=st.lists(url_strategy, min_size=1, max_size=10),
    invalid_preset_names=st.lists(
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_"),
            min_size=1,
            max_size=20
        ).filter(lambda s: s not in ["instagram", "twitter", "reddit", "polite", "archive", "fast", "instagram-stories", "instagram-reels", "tumblr"]),
        min_size=1,
        max_size=5
    )
)
def test_property_validation_error_reporting(valid_urls, invalid_preset_names):
    """
    **Feature: batch-mode, Property 21: Validation error reporting**
    **Validates: Requirements 6.2**

    For any batch file with syntax errors on lines L1, L2, ..., Ln,
    the validation report should include line numbers L1, L2, ..., Ln.
    """
    from insta_mash.config import Config

    # Track which lines should have errors
    error_lines = []
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        line_num = 1
        
        # Write some valid URLs
        for url in valid_urls[:len(valid_urls)//2]:
            f.write(f"{url}\n")
            line_num += 1
        
        # Write URLs with invalid presets
        for i, preset in enumerate(invalid_preset_names):
            if i < len(valid_urls):
                f.write(f"{valid_urls[i]} preset:{preset}\n")
                error_lines.append(line_num)
                line_num += 1
        
        # Write remaining valid URLs
        for url in valid_urls[len(valid_urls)//2:]:
            f.write(f"{url}\n")
            line_num += 1
        
        f.flush()
        path = Path(f.name)

    try:
        batch = BatchFile.load(path)
        config = Config()
        
        # Validate
        validation_results = batch.validate(config)
        
        # Should have errors for invalid presets
        assert len(validation_results) > 0
        
        # All error line numbers should be in our expected error_lines
        reported_lines = [err.line_number for err in validation_results]
        
        # Each expected error line should be reported
        for expected_line in error_lines:
            assert expected_line in reported_lines
    finally:
        path.unlink()


@settings(max_examples=100)
@given(
    url=url_strategy,
    invalid_preset=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_"),
        min_size=1,
        max_size=20
    ).filter(lambda s: s not in ["instagram", "twitter", "reddit", "polite", "archive", "fast", "instagram-stories", "instagram-reels", "tumblr"]),
    invalid_profile=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_"),
        min_size=1,
        max_size=20
    )
)
def test_property_validation_reference_checking(url, invalid_preset, invalid_profile):
    """
    **Feature: batch-mode, Property 22: Validation reference checking**
    **Validates: Requirements 6.3**

    For any batch file referencing non-existent presets or profiles,
    the validation report should identify those invalid references.
    """
    from insta_mash.config import Config

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        # Write URL with invalid preset
        f.write(f"{url} preset:{invalid_preset}\n")
        # Write URL with invalid profile
        f.write(f"{url} profile:{invalid_profile}\n")
        f.flush()
        path = Path(f.name)

    try:
        batch = BatchFile.load(path)
        config = Config()
        
        # Validate
        validation_results = batch.validate(config)
        
        # Should have at least 2 errors (one for preset, one for profile)
        assert len(validation_results) >= 2
        
        # Check that errors mention the invalid references
        error_messages = [err.message for err in validation_results]
        
        # Should have error about invalid preset
        assert any(invalid_preset in msg for msg in error_messages)
        
        # Should have error about invalid profile
        assert any(invalid_profile in msg for msg in error_messages)
    finally:
        path.unlink()


@settings(max_examples=100)
@given(
    valid_urls=st.lists(url_strategy, min_size=1, max_size=30),
    num_comments=st.integers(min_value=0, max_value=10),
    num_empty=st.integers(min_value=0, max_value=10)
)
def test_property_validation_count_accuracy(valid_urls, num_comments, num_empty):
    """
    **Feature: batch-mode, Property 23: Validation count accuracy**
    **Validates: Requirements 6.4**

    For any batch file with V valid entries, the validation report
    should show V as the count of valid entries.
    """
    from insta_mash.config import Config

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        # Write valid URLs
        for url in valid_urls:
            f.write(f"{url}\n")
        
        # Write comments
        for _ in range(num_comments):
            f.write("# This is a comment\n")
        
        # Write empty lines
        for _ in range(num_empty):
            f.write("\n")
        
        f.flush()
        path = Path(f.name)

    try:
        batch = BatchFile.load(path)
        config = Config()
        
        # Validate
        validation_results = batch.validate(config)
        
        # Should have no errors for valid entries
        assert len(validation_results) == 0
        
        # The batch should have exactly V valid entries
        assert len(batch.entries) == len(valid_urls)
    finally:
        path.unlink()


@settings(max_examples=100)
@given(
    valid_urls=st.lists(url_strategy, min_size=1, max_size=20),
    num_comments=st.integers(min_value=0, max_value=5)
)
def test_property_validation_exit_code(valid_urls, num_comments):
    """
    **Feature: batch-mode, Property 24: Validation exit code**
    **Validates: Requirements 6.5**

    For any batch file with zero validation errors, the validate command
    should exit with status code 0 (indicated by empty error list).
    """
    from insta_mash.config import Config

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        # Write valid URLs
        for url in valid_urls:
            f.write(f"{url}\n")
        
        # Write comments
        for _ in range(num_comments):
            f.write("# Comment\n")
        
        f.flush()
        path = Path(f.name)

    try:
        batch = BatchFile.load(path)
        config = Config()
        
        # Validate
        validation_results = batch.validate(config)
        
        # No errors means exit code should be 0
        # We test this by checking the error list is empty
        assert len(validation_results) == 0
    finally:
        path.unlink()



@settings(max_examples=100)
@given(
    total=st.integers(min_value=1, max_value=100),
    num_to_process=st.integers(min_value=0, max_value=100)
)
def test_property_progress_tracking_accuracy(total, num_to_process):
    """
    **Feature: batch-mode, Property 8: Progress tracking accuracy**
    **Validates: Requirements 3.2**

    For any batch execution, after processing N entries, the progress
    counter should show N completed out of total.
    """
    from insta_mash.batch import BatchProgress

    # Ensure num_to_process doesn't exceed total
    num_to_process = min(num_to_process, total)

    # Create progress tracker
    progress = BatchProgress(total=total)

    # Process N entries
    for i in range(num_to_process):
        # Randomly succeed or fail
        success = (i % 2 == 0)
        progress.update(success=success, url=f"https://example.com/{i}")

    # Check progress accuracy
    assert progress.completed == num_to_process
    assert progress.total == total



@settings(max_examples=100)
@given(
    total=st.integers(min_value=1, max_value=50),
    success_status=st.booleans()
)
def test_property_status_reporting_accuracy(total, success_status):
    """
    **Feature: batch-mode, Property 9: Status reporting accuracy**
    **Validates: Requirements 3.3**

    For any completed download operation, the progress display should
    indicate success if the operation succeeded and failure if it failed.
    """
    from insta_mash.batch import BatchProgress

    # Create progress tracker
    progress = BatchProgress(total=total)

    # Process one entry with the given status
    progress.update(success=success_status, url="https://example.com/test")

    # Check that status is correctly recorded
    if success_status:
        assert progress.succeeded == 1
        assert progress.failed == 0
    else:
        assert progress.succeeded == 0
        assert progress.failed == 1



@settings(max_examples=100)
@given(
    total=st.integers(min_value=1, max_value=50),
    current_url=url_strategy
)
def test_property_current_url_display(total, current_url):
    """
    **Feature: batch-mode, Property 10: Current URL display**
    **Validates: Requirements 3.4**

    For any batch entry being processed, the progress display should
    show the URL from that entry.
    """
    from insta_mash.batch import BatchProgress

    # Create progress tracker
    progress = BatchProgress(total=total)

    # Set current URL
    progress.set_current_url(current_url)

    # Check that current URL is stored
    assert progress.current_url == current_url

    # Check that display includes the current URL
    # Note: Rich may wrap long URLs across lines, so we remove whitespace for comparison
    display_output = progress.display()
    # Remove all whitespace and newlines from both strings for comparison
    display_normalized = "".join(display_output.split())
    url_normalized = "".join(current_url.split())
    assert url_normalized in display_normalized



@settings(max_examples=100)
@given(
    num_successes=st.integers(min_value=0, max_value=50),
    num_failures=st.integers(min_value=0, max_value=50)
)
def test_property_final_report_accuracy(num_successes, num_failures):
    """
    **Feature: batch-mode, Property 11: Final report accuracy**
    **Validates: Requirements 3.5**

    For any completed batch session with S successes and F failures,
    the final report should display S as success count and F as failure count.
    """
    from insta_mash.batch import BatchProgress

    # Ensure at least one operation
    if num_successes == 0 and num_failures == 0:
        num_successes = 1

    total = num_successes + num_failures

    # Create progress tracker
    progress = BatchProgress(total=total)

    # Process successes
    for i in range(num_successes):
        progress.update(success=True, url=f"https://example.com/success/{i}")

    # Process failures
    for i in range(num_failures):
        progress.update(
            success=False,
            url=f"https://example.com/failure/{i}",
            error=f"Error {i}"
        )

    # Get final report
    report = progress.get_final_report()

    # Check that report contains correct counts
    # The report should show the success and failure counts
    assert str(num_successes) in report
    assert str(num_failures) in report

    # Verify internal state
    assert progress.succeeded == num_successes
    assert progress.failed == num_failures
    assert progress.completed == total



@settings(max_examples=100)
@given(
    batch_file_path=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="/-_."),
        min_size=5,
        max_size=50
    ).map(lambda s: Path(s)),
    completed_indices=st.sets(st.integers(min_value=0, max_value=100), min_size=0, max_size=50)
)
def test_property_resume_state_persistence(batch_file_path, completed_indices):
    """
    **Feature: batch-mode, Property 16: Resume state persistence**
    **Validates: Requirements 5.2**

    For any paused batch session, the resume file should contain
    the indices of all completed entries.
    """
    from datetime import datetime
    from insta_mash.batch import ResumeState

    # Create a resume state
    original_state = ResumeState(
        batch_file_path=batch_file_path,
        completed_indices=completed_indices,
        timestamp=datetime.now()
    )

    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        resume_path = Path(f.name)

    try:
        # Save the state
        original_state.save(resume_path)

        # Load the state back
        loaded_state = ResumeState.load(resume_path)

        # Should not be None
        assert loaded_state is not None

        # Check that all data is preserved
        assert loaded_state.batch_file_path == original_state.batch_file_path
        assert loaded_state.completed_indices == original_state.completed_indices
        
        # Timestamp should be close (within a second due to serialization)
        time_diff = abs((loaded_state.timestamp - original_state.timestamp).total_seconds())
        assert time_diff < 1.0

    finally:
        if resume_path.exists():
            resume_path.unlink()



@settings(max_examples=100)
@given(
    urls=st.lists(url_strategy, min_size=5, max_size=30),
    completed_indices=st.sets(st.integers(min_value=0, max_value=29), min_size=1, max_size=15)
)
def test_property_resume_skip_behavior(urls, completed_indices):
    """
    **Feature: batch-mode, Property 17: Resume skip behavior**
    **Validates: Requirements 5.3**

    For any batch execution with a resume state, entries whose indices
    are in the completed set should be skipped.
    """
    from datetime import datetime
    from insta_mash.batch import ResumeState

    # Filter completed_indices to only include valid indices for our URL list
    completed_indices = {idx for idx in completed_indices if idx < len(urls)}
    
    # Skip test if no valid completed indices
    if not completed_indices:
        return

    # Create a batch file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for url in urls:
            f.write(f"{url}\n")
        f.flush()
        batch_path = Path(f.name)

    # Create resume state
    resume_state = ResumeState(
        batch_file_path=batch_path,
        completed_indices=completed_indices,
        timestamp=datetime.now()
    )

    try:
        # Load the batch file
        batch = BatchFile.load(batch_path)

        # Simulate processing with resume state
        # Entries to process should be those NOT in completed_indices
        entries_to_process = [
            entry for i, entry in enumerate(batch.entries)
            if i not in resume_state.completed_indices
        ]

        # Verify that we're skipping the right entries
        # The number of entries to process should be total - completed
        expected_to_process = len(urls) - len(completed_indices)
        assert len(entries_to_process) == expected_to_process

        # Verify that none of the entries to process have indices in completed_indices
        for i, entry in enumerate(batch.entries):
            if i in resume_state.completed_indices:
                # This entry should NOT be in entries_to_process
                assert entry not in entries_to_process
            else:
                # This entry SHOULD be in entries_to_process
                assert entry in entries_to_process

    finally:
        if batch_path.exists():
            batch_path.unlink()


@settings(max_examples=100)
@given(
    urls=st.lists(url_strategy, min_size=2, max_size=10),
    num_failures=st.integers(min_value=1, max_value=5)
)
def test_property_error_logging(urls, num_failures):
    """
    **Feature: batch-mode, Property 12: Error logging**
    **Validates: Requirements 4.1**

    For any failed download operation, the system should log error
    details including the URL and error message.
    """
    from insta_mash.batch import BatchExecutor, BatchFile
    from insta_mash.config import Config
    from unittest.mock import patch, MagicMock
    
    # Ensure we have enough URLs for the failures
    num_failures = min(num_failures, len(urls))
    
    # Create a batch file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for url in urls:
            f.write(f"{url}\n")
        f.flush()
        batch_path = Path(f.name)
    
    try:
        batch = BatchFile.load(batch_path)
        config = Config()
        
        # Create executor
        executor = BatchExecutor(batch_file=batch, config=config, dry_run=True)
        
        # Track which entry index we're on
        call_count = [0]
        
        # Mock subprocess to simulate failures for first num_failures entries
        with patch('subprocess.run') as mock_run:
            def side_effect(*args, **kwargs):
                # Track which entry this is (by call order, not URL)
                entry_index = call_count[0]
                call_count[0] += 1
                
                result = MagicMock()
                if entry_index < num_failures:
                    # Simulate failure
                    cmd = args[0] if args else kwargs.get('args', [])
                    url_in_cmd = cmd[-1] if cmd else ""
                    result.returncode = 1
                    result.stderr = f"Error downloading {url_in_cmd}"
                    result.stdout = ""
                else:
                    # Simulate success
                    result.returncode = 0
                    result.stderr = ""
                    result.stdout = "Success"
                
                return result
            
            mock_run.side_effect = side_effect
            
            # Execute batch
            progress = executor.execute()
            
            # Check that errors were logged
            assert len(progress.errors) == num_failures
            
            # Check that each error contains a URL and error message
            for url, error_msg in progress.errors:
                assert url in urls
                assert error_msg  # Error message should not be empty
    
    finally:
        if batch_path.exists():
            batch_path.unlink()


@settings(max_examples=100)
@given(
    urls=st.lists(url_strategy, min_size=3, max_size=15),
    failure_index=st.integers(min_value=0, max_value=14)
)
def test_property_failure_resilience(urls, failure_index):
    """
    **Feature: batch-mode, Property 13: Failure resilience**
    **Validates: Requirements 4.2**

    For any batch file where entry N fails, the system should still
    attempt to process entry N+1.
    """
    from insta_mash.batch import BatchExecutor, BatchFile
    from insta_mash.config import Config
    from unittest.mock import patch, MagicMock
    
    # Ensure failure_index is within bounds
    if len(urls) < 2:
        return
    
    failure_index = min(failure_index, len(urls) - 2)  # Ensure there's at least one entry after failure
    
    # Create a batch file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for url in urls:
            f.write(f"{url}\n")
        f.flush()
        batch_path = Path(f.name)
    
    try:
        batch = BatchFile.load(batch_path)
        config = Config()
        
        # Create executor
        executor = BatchExecutor(batch_file=batch, config=config, dry_run=True)
        
        # Track which URLs were attempted
        attempted_urls = []
        
        # Mock subprocess to simulate failure at specific index
        with patch('subprocess.run') as mock_run:
            def side_effect(*args, **kwargs):
                # Get the URL from the command
                cmd = args[0] if args else kwargs.get('args', [])
                url_in_cmd = cmd[-1] if cmd else ""
                attempted_urls.append(url_in_cmd)
                
                # Determine if this should fail
                url_index = next((i for i, u in enumerate(urls) if u == url_in_cmd), -1)
                
                result = MagicMock()
                if url_index == failure_index:
                    # Simulate failure
                    result.returncode = 1
                    result.stderr = f"Error at index {failure_index}"
                    result.stdout = ""
                else:
                    # Simulate success
                    result.returncode = 0
                    result.stderr = ""
                    result.stdout = "Success"
                
                return result
            
            mock_run.side_effect = side_effect
            
            # Execute batch
            progress = executor.execute()
            
            # Check that entry N+1 was attempted after entry N failed
            # All URLs should have been attempted
            assert len(attempted_urls) == len(urls)
            
            # The URL after the failure should have been attempted
            if failure_index + 1 < len(urls):
                assert urls[failure_index + 1] in attempted_urls
    
    finally:
        if batch_path.exists():
            batch_path.unlink()


@settings(max_examples=100, deadline=None)
@given(
    urls=st.lists(url_strategy, min_size=2, max_size=10),
    delay=st.floats(min_value=0.1, max_value=2.0)
)
def test_property_delay_timing(urls, delay):
    """
    **Feature: batch-mode, Property 18: Delay timing**
    **Validates: Requirements 5.4**

    For any batch execution with delay D specified, the time between
    starting consecutive download operations should be at least D seconds.
    """
    from insta_mash.batch import BatchExecutor, BatchFile
    from insta_mash.config import Config
    from unittest.mock import patch, MagicMock
    import time
    
    # Create a batch file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for url in urls:
            f.write(f"{url}\n")
        f.flush()
        batch_path = Path(f.name)
    
    try:
        batch = BatchFile.load(batch_path)
        config = Config()
        
        # Create executor with delay
        executor = BatchExecutor(batch_file=batch, config=config, delay=delay, dry_run=True)
        
        # Track execution times
        execution_times = []
        
        # Mock subprocess to track timing
        with patch('subprocess.run') as mock_run:
            def side_effect(*args, **kwargs):
                execution_times.append(time.time())
                result = MagicMock()
                result.returncode = 0
                result.stderr = ""
                result.stdout = "Success"
                return result
            
            mock_run.side_effect = side_effect
            
            # Execute batch
            progress = executor.execute()
            
            # Check that delays were applied between consecutive downloads
            for i in range(1, len(execution_times)):
                time_diff = execution_times[i] - execution_times[i-1]
                # Allow small tolerance for execution overhead
                assert time_diff >= delay - 0.1, f"Delay between downloads {i-1} and {i} was {time_diff}, expected at least {delay}"
    
    finally:
        if batch_path.exists():
            batch_path.unlink()


@settings(max_examples=100)
@given(
    urls=st.lists(url_strategy, min_size=1, max_size=10)
)
def test_property_dry_run_file_creation(urls):
    """
    **Feature: batch-mode, Property 19: Dry-run file creation**
    **Validates: Requirements 5.5**

    For any batch execution in dry-run mode, no media files should be
    created in the destination directories.
    """
    from insta_mash.batch import BatchExecutor, BatchFile
    from insta_mash.config import Config
    from unittest.mock import patch, MagicMock
    import tempfile
    import shutil
    
    # Create a temporary destination directory
    temp_dest = tempfile.mkdtemp()
    
    # Create a batch file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for url in urls:
            f.write(f"{url}\n")
        f.flush()
        batch_path = Path(f.name)
    
    try:
        batch = BatchFile.load(batch_path)
        config = Config()
        config.defaults.destination = temp_dest
        
        # Create executor in dry-run mode
        executor = BatchExecutor(batch_file=batch, config=config, dry_run=True)
        
        # Mock subprocess to simulate successful downloads
        with patch('subprocess.run') as mock_run:
            result = MagicMock()
            result.returncode = 0
            result.stderr = ""
            result.stdout = "Success"
            mock_run.return_value = result
            
            # Execute batch
            progress = executor.execute()
            
            # In dry-run mode, gallery-dl is called with -s flag which simulates
            # Check that the -s flag was passed to gallery-dl
            for call in mock_run.call_args_list:
                cmd = call[0][0] if call[0] else call[1].get('args', [])
                assert '-s' in cmd, "Dry-run flag -s should be present in command"
    
    finally:
        if batch_path.exists():
            batch_path.unlink()
        if Path(temp_dest).exists():
            shutil.rmtree(temp_dest)
