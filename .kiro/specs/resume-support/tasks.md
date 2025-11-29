# Implementation Plan: Resume Support

## Overview

This implementation plan guides the development of resume support functionality for insta-mash. The plan follows an incremental approach, building core state management first, then adding signal handling, file tracking, archive integration, and finally CLI commands. Each step includes corresponding property-based tests to validate correctness.

## Tasks

- [ ] 1. Set up resume support infrastructure
  - Create directory structure for resume state management
  - Define data models for ResumeState
  - Set up state directory in user config location (~/.config/insta-mash/resume/)
  - Configure JSON serialization for state persistence
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 2. Implement ResumeState data model
  - Create ResumeState dataclass with url, timestamp, completed_files, total_files, version fields
  - Implement to_dict() serialization method
  - Implement from_dict() deserialization method
  - Implement matches_url() method for URL comparison
  - _Requirements: 1.3, 2.5, 4.3_

- [ ] 2.1 Write property test for state serialization
  - **Property 14: Atomic state persistence (partial - serialization round-trip)**
  - Test that for any ResumeState, serializing then deserializing produces equivalent state
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 3. Implement ResumeStateManager
  - Create ResumeStateManager class with state_dir initialization
  - Implement _get_state_path() to generate filename from URL hash (SHA256, first 16 chars)
  - Implement _atomic_write() using temp file and atomic rename
  - Implement save_state() with atomic write and timestamp
  - Implement load_state() with validation
  - Implement _validate_state() for format checking
  - Implement delete_state() for single state removal
  - Implement list_states() to enumerate all state files
  - Implement clear_all_states() to delete all states
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 5.1, 5.2_

- [ ] 3.1 Write property test for atomic state persistence
  - **Property 14: Atomic state persistence**
  - Test that for any ResumeState, saving creates a file with correct content and timestamp
  - Verify temp file is used during write
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 3.2 Write property test for state validation
  - **Property 15: State format validation**
  - Test that for any state load operation, invalid formats are rejected
  - Generate various invalid state formats and verify validation catches them
  - _Requirements: 4.4_

- [ ] 3.3 Write property test for corrupted state handling
  - **Property 16: Corrupted state handling**
  - Test that for any corrupted state file, system displays warning and continues
  - _Requirements: 4.5_

- [ ] 4. Implement SignalHandler
  - Create SignalHandler class with interrupt callback
  - Implement setup() to register SIGINT and SIGTERM handlers
  - Implement handle_signal() to track interrupt count
  - Implement is_interrupted() to check interrupt flag
  - Implement should_force_exit() to check for double interrupt
  - Track interrupt_count to distinguish first vs second interrupt
  - _Requirements: 1.1, 1.5_

- [ ] 4.1 Write property test for signal handling
  - **Property 1: Current file completion before interrupt**
  - **Property 4: Interrupt exit code**
  - Test that interrupt flag is set correctly
  - Test that double interrupt is detected
  - _Requirements: 1.1, 1.4, 1.5_

- [ ] 5. Implement FileTracker
  - Create FileTracker class with completed_files set
  - Implement constructor that loads from optional ResumeState
  - Implement start_file() to mark file as current and check if should download
  - Implement should_skip() to check if file is in completed set
  - Implement complete_file() with optional size verification
  - Implement verify_file_size() to check actual vs expected size
  - Implement mark_partial() to track partial downloads
  - Implement cleanup_partial() to delete partial files
  - Implement get_completed_count() to return count
  - _Requirements: 2.2, 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 5.1 Write property test for file skipping
  - **Property 6: Completed file skipping**
  - Test that for any file in completed set, should_skip returns True
  - _Requirements: 2.2_

- [ ] 5.2 Write property test for file size verification
  - **Property 12: File size verification**
  - Test that for any file with known expected size, verification is performed
  - _Requirements: 3.3_

- [ ] 5.3 Write property test for verification failure handling
  - **Property 13: Failed verification state update**
  - Test that files failing verification are marked incomplete
  - _Requirements: 3.4_

- [ ] 5.4 Write property test for partial download cleanup
  - **Property 10: Partial download cleanup**
  - Test that partial files are deleted on interrupt and resume
  - _Requirements: 3.1, 3.5_

- [ ] 6. Implement ArchiveCoordinator
  - Create ArchiveCoordinator class with archive_path and state_manager
  - Implement _load_archive() to read existing archive entries
  - Implement should_skip_file() combining archive and resume state logic
  - Implement update_archive() to add completed files
  - Implement ensure_consistency() to sync archive with resume state
  - Implement resolve_conflict() with resume state as authoritative
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 6.1 Write property test for archive-state skip logic
  - **Property 23: Archive and state skip logic**
  - Test that files in both archive and state are skipped
  - _Requirements: 6.2_

- [ ] 6.2 Write property test for archive consistency
  - **Property 25: Archive-state consistency**
  - Test that archive remains consistent with resume state
  - Test that resume state is authoritative in conflicts
  - _Requirements: 6.4, 6.5_

- [ ] 7. Implement ResumeDownloadSession orchestrator
  - Create ResumeDownloadSession class with url, state_manager, archive_coordinator, no_resume flag
  - Implement start() to initialize session, load resume state, return tracker and skip count
  - Implement _load_resume_state() to load and validate state for URL
  - Implement on_file_start() to handle file start events
  - Implement on_file_complete() to handle file completion and update state
  - Implement _save_checkpoint() to periodically save progress
  - Implement on_interrupt() to handle interrupt signal
  - Implement finish() to cleanup state on successful completion
  - Integrate SignalHandler for interrupt handling
  - _Requirements: 1.1, 1.2, 2.1, 2.3, 2.4, 2.5_

- [ ] 7.1 Write property test for state persistence on interrupt
  - **Property 2: State persistence on interrupt**
  - Test that interrupt triggers state save
  - _Requirements: 1.2_

- [ ] 7.2 Write property test for completed files in state
  - **Property 3: Completed files in saved state**
  - Test that all completed files appear in saved state
  - _Requirements: 1.3_

- [ ] 7.3 Write property test for resume state loading
  - **Property 5: Resume state loading**
  - Test that valid resume state is loaded on session start
  - _Requirements: 2.1_

- [ ] 7.4 Write property test for skip count display
  - **Property 7: Skip count display**
  - Test that resumed session displays correct skip count
  - _Requirements: 2.3_

- [ ] 7.5 Write property test for state cleanup
  - **Property 8: State cleanup on completion**
  - Test that state file is deleted on successful completion
  - _Requirements: 2.4_

- [ ] 7.6 Write property test for URL mismatch
  - **Property 9: URL mismatch handling**
  - Test that mismatched URLs cause state to be ignored
  - _Requirements: 2.5_

- [ ] 7.7 Write property test for incomplete file re-download
  - **Property 11: Incomplete file re-download**
  - Test that incomplete files are re-downloaded
  - _Requirements: 3.2_

- [ ] 8. Integrate resume support with CLI
  - Modify cli.py to create ResumeDownloadSession for download commands
  - Add --no-resume flag to download command
  - Pass archive file path to ArchiveCoordinator if archive is enabled
  - Handle exit code 130 for interrupted downloads
  - Display skip count when resuming
  - _Requirements: 2.3, 5.4, 5.5_

- [ ] 8.1 Write property test for no-resume flag
  - **Property 20: No-resume flag state ignore**
  - **Property 21: No-resume flag state creation**
  - Test that no-resume flag disables resume functionality
  - _Requirements: 5.4, 5.5_

- [ ] 9. Implement resume management CLI commands
  - Add 'resume list' subcommand to list all resume states with timestamps
  - Add 'resume show <url>' subcommand to display specific resume state contents
  - Add 'resume clear' subcommand to delete all resume states
  - Format output for human readability
  - Handle cases where no resume states exist
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 9.1 Write property test for clear command
  - **Property 17: Clear command deletion**
  - Test that clear command deletes all state files
  - _Requirements: 5.1_

- [ ] 9.2 Write property test for list command
  - **Property 18: List command output**
  - Test that list command shows all states with timestamps
  - _Requirements: 5.2_

- [ ] 9.3 Write property test for show command
  - **Property 19: Show command output**
  - Test that show command displays state contents
  - _Requirements: 5.3_

- [ ] 10. Implement archive integration
  - Ensure ArchiveCoordinator updates archive on each file completion
  - Verify archive contains all files on successful completion
  - Test archive-resume state consistency during interrupts
  - _Requirements: 6.1, 6.3, 6.4_

- [ ] 10.1 Write property test for archive updates
  - **Property 22: Archive update on completion**
  - Test that archive is updated when files complete
  - _Requirements: 6.1_

- [ ] 10.2 Write property test for archive completeness
  - **Property 24: Archive completeness on finish**
  - Test that archive contains all files on completion
  - _Requirements: 6.3_

- [ ] 11. Add error handling and edge cases
  - Handle file system errors during state save/load
  - Handle permission errors on state directory
  - Handle disk full scenarios
  - Add logging for debugging resume operations
  - Test with very large file lists
  - _Requirements: 4.4, 4.5_

- [ ] 12. Add documentation
  - Document resume support in README
  - Add examples of interrupt and resume workflow
  - Document resume management commands
  - Document --no-resume flag usage
  - Document state file location and format
  - _Requirements: All_

- [ ] 13. Final checkpoint - Ensure all tests pass
  - Run all unit tests and verify they pass
  - Run all property-based tests and verify they pass
  - Ensure all 25 correctness properties are validated
  - Ask the user if questions arise

## Notes

- Resume state files are stored in `~/.config/insta-mash/resume/`
- State filenames are based on SHA256 hash of URL (first 16 characters)
- Exit code 130 indicates interrupted download with saved state
- Resume state is authoritative over archive file in case of conflicts
- Property-based tests use Hypothesis library with minimum 100 iterations
- Each property test must reference its correctness property number
