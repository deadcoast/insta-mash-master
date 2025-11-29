# Implementation Plan

- [ ] 1. Set up core detection data structures
  - Create PlatformPattern dataclass with regex compilation
  - Create DetectionResult dataclass with confidence checking and display methods
  - Create DetectionConfig dataclass with configuration loading
  - Set up testing framework with Hypothesis for property-based testing
  - _Requirements: 1.1, 2.1, 6.1, 6.4_

- [ ] 2. Implement pattern matching engine
- [ ] 2.1 Create PlatformDetector class with pattern loading
  - Implement `__init__` with custom patterns and enabled flag
  - Implement `_load_built_in_patterns()` with all platform patterns
  - Define built-in patterns for Instagram (including content types), Twitter/X, Reddit, Tumblr, TikTok
  - _Requirements: 1.1, 1.3, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4_

- [ ] 2.2 Implement URL pattern matching logic
  - Implement `_match_patterns()` to check URL against pattern list
  - Implement pattern priority ordering (custom rules first, then content-specific, then general)
  - Implement `matches()` method in PlatformPattern
  - _Requirements: 1.1, 3.1, 6.2_

- [ ] 2.3 Implement confidence scoring
  - Implement `_calculate_confidence()` with scoring rules
  - Content-specific patterns score 1.0, domain-only 0.9, partial 0.6-0.8
  - _Requirements: 4.5_

- [ ] 2.4 Implement main detection method
  - Implement `detect()` method that orchestrates pattern matching
  - Check custom patterns before built-in patterns
  - Return DetectionResult or None
  - _Requirements: 1.1, 6.2_

- [ ] 2.5 Write property test for platform domain detection
  - **Property 1: Platform domain detection**
  - **Validates: Requirements 1.1, 1.3, 2.1, 2.2, 2.3, 2.4**

- [ ] 2.6 Write property test for Instagram content-type detection
  - **Property 5: Instagram content-type detection**
  - **Validates: Requirements 3.1, 3.2, 3.3**

- [ ] 2.7 Write property test for Instagram default fallback
  - **Property 6: Instagram default fallback**
  - **Validates: Requirements 3.4**

- [ ] 2.8 Write unit tests for pattern matching
  - Test exact domain matches for all platforms
  - Test subdomain handling (www., mobile., etc.)
  - Test protocol variations (http://, https://, no protocol)
  - Test query parameters and fragments don't affect detection
  - Test edge cases (empty URL, malformed URL, multiple domains)
  - _Requirements: 1.1, 1.3, 2.1, 2.2, 2.3, 2.4_

- [ ] 3. Implement preset resolution
- [ ] 3.1 Create PresetResolver class
  - Implement `resolve()` method with precedence logic
  - User preset > auto-detected preset > default
  - Return tuple of (preset_name, source)
  - _Requirements: 1.2, 1.5, 2.5, 5.3_

- [ ] 3.2 Write property test for detected platform applies preset
  - **Property 2: Detected platform applies corresponding preset**
  - **Validates: Requirements 1.2, 2.5**

- [ ] 3.3 Write property test for user preset precedence
  - **Property 4: User preset precedence**
  - **Validates: Requirements 1.5**

- [ ] 3.4 Write property test for default settings with disabled detection
  - **Property 12: Default settings with disabled detection**
  - **Validates: Requirements 5.3**

- [ ] 3.5 Write unit tests for preset resolution
  - Test user preset overrides auto-detection
  - Test auto-detection with no user preset
  - Test disabled detection returns default
  - Test fallback behavior
  - _Requirements: 1.2, 1.5, 5.3_

- [ ] 4. Implement detection display and reporting
- [ ] 4.1 Implement display message generation
  - Implement `display_message()` in DetectionResult
  - Include platform name, preset name, content type
  - Add verbose mode with matched pattern details
  - Add low confidence warnings
  - _Requirements: 1.4, 3.5, 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 4.2 Write property test for auto-preset display
  - **Property 3: Auto-preset display**
  - **Validates: Requirements 1.4, 4.2**

- [ ] 4.3 Write property test for content-type display
  - **Property 7: Content-type display**
  - **Validates: Requirements 3.5**

- [ ] 4.4 Write property test for platform name display
  - **Property 8: Platform name display**
  - **Validates: Requirements 4.1**

- [ ] 4.5 Write property test for verbose pattern display
  - **Property 9: Verbose pattern display**
  - **Validates: Requirements 4.4**

- [ ] 4.6 Write property test for low confidence warning
  - **Property 10: Low confidence warning**
  - **Validates: Requirements 4.5**

- [ ] 4.7 Write unit tests for display messages
  - Test detection success message format
  - Test no detection message
  - Test low confidence warning format
  - Test verbose output includes pattern
  - Test content-type in message
  - _Requirements: 1.4, 3.5, 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 5. Implement custom detection rules
- [ ] 5.1 Implement custom rule loading
  - Implement `load_custom_patterns()` in DetectionConfig
  - Parse custom rules from configuration dictionary
  - Validate rule structure (platform, pattern, preset required)
  - Handle invalid rules with warnings
  - _Requirements: 6.1, 6.4, 6.5_

- [ ] 5.2 Implement custom rule validation
  - Validate regex patterns compile correctly
  - Validate required fields present
  - Generate warnings for invalid rules
  - Skip invalid rules and continue
  - _Requirements: 6.5_

- [ ] 5.3 Write property test for custom rule loading
  - **Property 15: Custom rule loading**
  - **Validates: Requirements 6.1**

- [ ] 5.4 Write property test for custom rule precedence
  - **Property 16: Custom rule precedence**
  - **Validates: Requirements 6.2**

- [ ] 5.5 Write property test for custom rule preset application
  - **Property 17: Custom rule preset application**
  - **Validates: Requirements 6.3**

- [ ] 5.6 Write property test for regex pattern matching
  - **Property 18: Regex pattern matching**
  - **Validates: Requirements 6.4**

- [ ] 5.7 Write property test for invalid rule handling
  - **Property 19: Invalid rule handling**
  - **Validates: Requirements 6.5**

- [ ] 5.8 Write unit tests for custom rules
  - Test valid custom rule loading
  - Test invalid regex handling
  - Test missing field handling
  - Test priority ordering
  - Test custom rules checked before built-in
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 6. Implement detection control flags
- [ ] 6.1 Add no-auto-detect flag support
  - Add flag to CLI interface
  - Implement detection skip logic when flag is set
  - Ensure no preset applied when disabled
  - _Requirements: 5.1, 5.2_

- [ ] 6.2 Implement configuration-level detection control
  - Add enabled flag to DetectionConfig
  - Respect configuration setting across all operations
  - _Requirements: 5.4_

- [ ] 6.3 Implement detection skipped messaging
  - Display message when detection is skipped
  - Include reason (flag or configuration)
  - _Requirements: 5.5_

- [ ] 6.4 Write property test for no-auto-detect disables preset
  - **Property 11: No-auto-detect disables preset application**
  - **Validates: Requirements 5.1, 5.2**

- [ ] 6.5 Write property test for configuration-level disable
  - **Property 13: Configuration-level detection disable**
  - **Validates: Requirements 5.4**

- [ ] 6.6 Write property test for detection skipped message
  - **Property 14: Detection skipped message**
  - **Validates: Requirements 5.5**

- [ ] 6.7 Write unit tests for detection control
  - Test --no-auto-detect flag disables detection
  - Test configuration enabled=false disables detection
  - Test skipped message displayed
  - Test defaults used when disabled
  - _Requirements: 5.1, 5.2, 5.4, 5.5_

- [ ] 7. Integrate with CLI and configuration system
- [ ] 7.1 Integrate PlatformDetector into grab command
  - Create detector instance with configuration
  - Run detection before download execution
  - Pass detection result to preset resolver
  - Display detection messages
  - _Requirements: 1.1, 1.2, 4.1_

- [ ] 7.2 Add detection configuration to config file schema
  - Add platform_detection section to configuration
  - Support enabled, confidence_threshold, custom_rules fields
  - Load detection config in Config class
  - _Requirements: 5.4, 6.1_

- [ ] 7.3 Integrate PresetResolver with config merging
  - Call resolver with detection result and user preset
  - Merge resolved preset with other configuration sources
  - Respect precedence: user > auto > default
  - _Requirements: 1.5, 2.5_

- [ ] 7.4 Add CLI flags for detection control
  - Add --no-auto-detect flag to grab command
  - Add --verbose flag support for pattern display
  - Wire flags to detector and display logic
  - _Requirements: 4.4, 5.1_

- [ ] 7.5 Write integration tests
  - Test end-to-end detection flow with real URLs
  - Test CLI flag integration (--no-auto-detect, --verbose)
  - Test configuration file integration
  - Test preset system integration
  - Test error resilience when detection fails
  - _Requirements: All_

- [ ] 8. Final checkpoint - Ensure all tests pass
  - Run all unit tests and verify they pass
  - Run all property-based tests and verify they pass
  - Run integration tests and verify they pass
  - Ask the user if questions arise

