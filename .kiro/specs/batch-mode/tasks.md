# Implementation Plan

- [x] 1. Implement batch file parsing
  - Create `BatchEntry` dataclass with parse method
  - Create `BatchFile` dataclass with load method
  - Handle comments, empty lines, and URL-only entries
  - Parse preset and profile specifications from entries
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 1.1 Write property test for file parsing
  - **Property 1: File reading completeness**
  - **Validates: Requirements 1.1, 1.2**

- [x] 1.2 Write property test for order preservation
  - **Property 2: Order preservation**
  - **Validates: Requirements 1.5**

- [x] 2. Implement configuration resolution for batch entries
  - Extend configuration system to resolve per-entry options
  - Implement merging of global batch settings with entry-specific config
  - Handle default, preset, and profile application
  - _Requirements: 2.1, 2.2, 2.3, 2.5_

- [x] 2.1 Write property test for default configuration
  - **Property 3: Default configuration application**
  - **Validates: Requirements 2.1**

- [x] 2.2 Write property test for preset application
  - **Property 4: Preset application**
  - **Validates: Requirements 2.2**

- [x] 2.3 Write property test for profile application
  - **Property 5: Profile application**
  - **Validates: Requirements 2.3**

- [x] 2.4 Write property test for configuration merging
  - **Property 7: Configuration merging priority**
  - **Validates: Requirements 2.5**

- [x] 3. Implement batch validation
  - Create validation logic for batch files
  - Check for syntax errors with line numbers
  - Verify preset and profile references exist
  - Generate validation report with error details
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 3.1 Write property test for invalid entry skipping
  - **Property 6: Invalid entry skipping**
  - **Validates: Requirements 2.4**

- [x] 3.2 Write property test for validation parsing
  - **Property 20: Validation parsing**
  - **Validates: Requirements 6.1**

- [x] 3.3 Write property test for validation error reporting
  - **Property 21: Validation error reporting**
  - **Validates: Requirements 6.2**

- [x] 3.4 Write property test for validation reference checking
  - **Property 22: Validation reference checking**
  - **Validates: Requirements 6.3**

- [x] 3.5 Write property test for validation count accuracy
  - **Property 23: Validation count accuracy**
  - **Validates: Requirements 6.4**

- [x] 3.6 Write property test for validation exit code
  - **Property 24: Validation exit code**
  - **Validates: Requirements 6.5**

- [x] 4. Implement progress tracking
  - Create `BatchProgress` dataclass
  - Implement progress update logic
  - Add console display formatting with Rich
  - Track success/failure counts
  - Display current URL being processed
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4.1 Write property test for progress tracking
  - **Property 8: Progress tracking accuracy**
  - **Validates: Requirements 3.2**

- [x] 4.2 Write property test for status reporting
  - **Property 9: Status reporting accuracy**
  - **Validates: Requirements 3.3**

- [x] 4.3 Write property test for current URL display
  - **Property 10: Current URL display**
  - **Validates: Requirements 3.4**

- [x] 4.4 Write property test for final report
  - **Property 11: Final report accuracy**
  - **Validates: Requirements 3.5**

- [x] 5. Implement resume state management
  - Create `ResumeState` dataclass
  - Implement save/load methods with JSON serialization
  - Store completed entry indices
  - Handle resume file path resolution
  - _Requirements: 5.2, 5.3_

- [x] 5.1 Write property test for resume state persistence
  - **Property 16: Resume state persistence**
  - **Validates: Requirements 5.2**

- [x] 5.2 Write property test for resume skip behavior
  - **Property 17: Resume skip behavior**
  - **Validates: Requirements 5.3**

- [-] 6. Implement batch executor
  - Create `BatchExecutor` class
  - Implement sequential execution of batch entries
  - Integrate with existing download logic from `grab` command
  - Handle errors gracefully and continue processing
  - Implement delay between downloads
  - Support dry-run mode
  - _Requirements: 4.1, 4.2, 5.4, 5.5_

- [x] 6.1 Write property test for error logging
  - **Property 12: Error logging**
  - **Validates: Requirements 4.1**

- [x] 6.2 Write property test for failure resilience
  - **Property 13: Failure resilience**
  - **Validates: Requirements 4.2**

- [-] 6.3 Write property test for delay timing
  - **Property 18: Delay timing**
  - **Validates: Requirements 5.4**

- [ ] 6.4 Write property test for dry-run mode
  - **Property 19: Dry-run file creation**
  - **Validates: Requirements 5.5**

- [ ] 7. Implement exit code handling
  - Set appropriate exit codes based on batch results
  - Exit with 0 for all successes
  - Exit with non-zero for any failures
  - _Requirements: 4.4, 4.5_

- [ ] 7.1 Write property test for exit codes
  - **Property 14: Exit code on failure**
  - **Property 15: Exit code on success**
  - **Validates: Requirements 4.4, 4.5**

- [ ] 8. Implement CLI commands
  - Add `batch` command group to CLI
  - Implement `mash batch run <file>` command with options
  - Implement `mash batch validate <file>` command
  - Add flags: --delay, --dry-run, --resume
  - Wire up all components
  - _Requirements: All_

- [ ] 8.1 Write integration tests for batch commands
  - Test end-to-end batch execution
  - Test validation command
  - Test resume functionality
  - Test error handling

- [ ] 9. Add batch mode documentation
  - Update README with batch mode examples
  - Add batch file format documentation
  - Document CLI commands and options
  - Add troubleshooting guide

- [ ] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
