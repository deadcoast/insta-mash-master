# Implementation Plan

- [ ] 1. Set up progress display module structure and core data models
  - Create `src/insta_mash/progress.py` module
  - Implement `ProgressState` dataclass with completion percentage and elapsed time calculations
  - Implement `DownloadSummary` dataclass with formatting method
  - Implement `ProgressEvent` dataclass for event representation
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 1.1 Write property test for progress percentage calculation
  - **Property 1: Progress percentage accuracy**
  - **Validates: Requirements 1.2**

- [ ] 1.2 Write property test for summary calculations
  - **Property 15: Summary file count accuracy**
  - **Property 16: Summary byte count accuracy**
  - **Property 17: Summary elapsed time accuracy**
  - **Property 18: Summary average speed accuracy**
  - **Property 19: Summary failure count accuracy**
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

- [ ] 2. Implement metrics calculator for speed and ETA
  - Create `MetricsCalculator` class with sliding window for samples
  - Implement `add_sample()` method to track data points
  - Implement `current_speed()` method with moving average calculation
  - Implement `estimate_eta()` method based on current speed
  - Implement `format_speed()` method with unit selection (B/s, KB/s, MB/s)
  - Implement `format_eta()` method for human-readable time
  - _Requirements: 2.1, 2.2, 2.5_

- [ ] 2.1 Write property test for speed calculation
  - **Property 3: Speed calculation accuracy**
  - **Validates: Requirements 2.1**

- [ ] 2.2 Write property test for ETA calculation
  - **Property 4: ETA calculation reasonableness**
  - **Validates: Requirements 2.2**

- [ ] 2.3 Write property test for speed formatting
  - **Property 5: Speed formatting for low speeds**
  - **Validates: Requirements 2.5**

- [ ] 3. Implement terminal adapter for capability detection
  - Create `TerminalAdapter` class
  - Implement TTY detection using `sys.stdout.isatty()`
  - Implement ANSI support detection (check TERM environment variable)
  - Implement terminal width detection using `shutil.get_terminal_size()`
  - Implement `get_display_mode()` method returning 'full', 'compact', or 'simple'
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 6.3, 6.4_

- [ ] 3.1 Write property test for terminal width adaptation
  - **Property 11: Terminal width adaptation**
  - **Validates: Requirements 4.1, 4.2**

- [ ] 3.2 Write property test for non-ANSI fallback
  - **Property 13: Non-ANSI fallback**
  - **Property 22: Non-TTY output mode**
  - **Validates: Requirements 4.4, 6.3, 6.4**

- [ ] 4. Implement progress renderer with Rich library integration
  - Create `ProgressRenderer` class with Rich Progress instance
  - Implement `start()` method to initialize progress display
  - Implement `_render_full()` method for full display mode (width >= 80)
  - Implement `_render_compact()` method for compact display mode (width < 80)
  - Implement `_render_simple()` method for simple text mode (no ANSI)
  - Implement `_truncate_filename()` method with ellipsis handling
  - Implement `update()` method to refresh display based on mode
  - Implement `finish()` method to display summary and cleanup
  - _Requirements: 1.5, 3.1, 3.2, 3.4, 3.5, 4.1, 4.2, 4.4, 4.5_

- [ ] 4.1 Write property test for filename display
  - **Property 6: Filename display presence**
  - **Validates: Requirements 3.1**

- [ ] 4.2 Write property test for file size display
  - **Property 7: File size display when known**
  - **Validates: Requirements 3.2**

- [ ] 4.3 Write property test for file counter display
  - **Property 9: File counter display**
  - **Validates: Requirements 3.4**

- [ ] 4.4 Write property test for filename truncation
  - **Property 10: Filename truncation**
  - **Validates: Requirements 3.5**

- [ ] 4.5 Write property test for no newline accumulation
  - **Property 14: No newline accumulation**
  - **Validates: Requirements 4.5**

- [ ] 5. Implement progress tracker orchestration
  - Create `ProgressTracker` class coordinating renderer and calculator
  - Implement `start_session()` method to initialize tracking
  - Implement `start_file()` method to begin tracking a new file
  - Implement `update_progress()` method to process byte updates
  - Implement `complete_file()` method to mark file completion
  - Implement `finish_session()` method to generate summary
  - Add logic to update metrics calculator with each progress update
  - Add logic to trigger renderer updates
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.3_

- [ ] 5.1 Write property test for file completion updates
  - **Property 2: Progress bar updates on file completion**
  - **Validates: Requirements 1.3**

- [ ] 5.2 Write property test for file transition updates
  - **Property 8: File transition updates**
  - **Validates: Requirements 3.3**

- [ ] 6. Implement quiet and verbose mode support
  - Add quiet mode logic to `ProgressRenderer` to suppress output
  - Ensure error messages still go to stderr in quiet mode
  - Add verbose mode logic to include debug information
  - Add conditional logging based on verbose flag
  - _Requirements: 6.1, 6.2, 6.5_

- [ ] 6.1 Write property test for quiet mode suppression
  - **Property 20: Quiet mode suppression**
  - **Validates: Requirements 6.1**

- [ ] 6.2 Write property test for quiet mode error preservation
  - **Property 21: Quiet mode error preservation**
  - **Validates: Requirements 6.2**

- [ ] 6.3 Write property test for verbose mode information
  - **Property 23: Verbose mode information**
  - **Validates: Requirements 6.5**

- [ ] 7. Integrate progress display with CLI and download execution
  - Update `cli.py` to create `ProgressTracker` instance for download commands
  - Pass quiet and verbose flags from CLI to `ProgressRenderer`
  - Hook progress tracker into download execution flow
  - Capture and parse gallery-dl output for progress events
  - Map gallery-dl events to progress tracker method calls
  - Display summary after download completion
  - _Requirements: All requirements (integration)_

- [ ] 7.1 Write integration tests for end-to-end progress display
  - Test progress display with simulated downloads
  - Test terminal adaptation with various widths
  - Test mode switching (quiet, verbose)
  - Test summary generation accuracy

- [ ] 8. Add dynamic terminal width adaptation
  - Implement signal handler for SIGWINCH (terminal resize)
  - Update `TerminalAdapter` to refresh width on resize
  - Trigger display mode recalculation on width change
  - Ensure renderer adapts format on next update
  - _Requirements: 4.3_

- [ ] 8.1 Write property test for dynamic width adaptation
  - **Property 12: Dynamic width adaptation**
  - **Validates: Requirements 4.3**

- [ ] 9. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

