# Requirements Document

## Introduction

This document specifies the requirements for smart platform detection functionality in insta-mash. Smart platform detection automatically identifies the source platform from a URL and applies appropriate presets, eliminating the need for users to manually specify presets for common platforms. This feature streamlines the user experience and ensures optimal download settings are applied automatically.

## Glossary

- **Platform Detection**: The process of identifying the source platform from a URL
- **System**: The insta-mash application
- **Source Platform**: The website or service from which media is being downloaded
- **URL Pattern**: A regular expression or string pattern that matches URLs from a specific platform
- **Auto-Preset**: A preset automatically applied based on detected platform
- **Detection Confidence**: A measure of certainty that a URL belongs to a specific platform

## Requirements

### Requirement 1

**User Story:** As a user, I want the system to automatically detect Instagram URLs, so that I don't need to specify the Instagram preset manually.

#### Acceptance Criteria

1. WHEN a user provides a URL containing instagram.com, THE System SHALL detect the platform as Instagram
2. WHEN the System detects Instagram, THE System SHALL apply the Instagram preset automatically
3. WHEN a user provides a URL containing instagr.am, THE System SHALL detect the platform as Instagram
4. WHEN the System applies an Auto-Preset, THE System SHALL display which preset was applied
5. WHEN a user explicitly specifies a preset, THE System SHALL use the user-specified preset instead of the Auto-Preset

### Requirement 2

**User Story:** As a user, I want the system to detect common social media platforms, so that optimal settings are applied automatically.

#### Acceptance Criteria

1. WHEN a user provides a URL containing twitter.com or x.com, THE System SHALL detect the platform as Twitter
2. WHEN a user provides a URL containing reddit.com, THE System SHALL detect the platform as Reddit
3. WHEN a user provides a URL containing tumblr.com, THE System SHALL detect the platform as Tumblr
4. WHEN a user provides a URL containing tiktok.com, THE System SHALL detect the platform as TikTok
5. WHEN the System detects a supported platform, THE System SHALL apply the corresponding preset

### Requirement 3

**User Story:** As a user, I want the system to detect Instagram content types, so that appropriate settings are applied for stories, reels, or posts.

#### Acceptance Criteria

1. WHEN a user provides an Instagram URL containing /stories/, THE System SHALL apply the Instagram Stories preset
2. WHEN a user provides an Instagram URL containing /reels/, THE System SHALL apply the Instagram Reels preset
3. WHEN a user provides an Instagram URL containing /p/, THE System SHALL apply the Instagram post preset
4. WHEN a user provides an Instagram profile URL without content type, THE System SHALL apply the default Instagram preset
5. WHEN the System detects a content-specific URL, THE System SHALL display the detected content type

### Requirement 4

**User Story:** As a user, I want to see what platform was detected, so that I can verify the correct settings will be used.

#### Acceptance Criteria

1. WHEN the System detects a platform, THE System SHALL display the detected platform name
2. WHEN the System applies an Auto-Preset, THE System SHALL display the preset name being applied
3. WHEN the System cannot detect a platform, THE System SHALL display a message indicating no platform was detected
4. WHEN a user specifies the verbose flag, THE System SHALL display the URL patterns that were matched
5. WHEN the System detects a platform with low confidence, THE System SHALL display a warning

### Requirement 5

**User Story:** As a user, I want to disable automatic platform detection, so that I have full control over preset selection.

#### Acceptance Criteria

1. WHEN a user specifies the no-auto-detect flag, THE System SHALL skip platform detection
2. WHEN a user specifies the no-auto-detect flag, THE System SHALL not apply any Auto-Preset
3. WHEN a user disables auto-detection, THE System SHALL use default settings unless a preset is explicitly specified
4. WHEN a user sets a configuration option to disable auto-detection, THE System SHALL respect that setting for all downloads
5. WHEN auto-detection is disabled, THE System SHALL display a message indicating detection was skipped

### Requirement 6

**User Story:** As a user, I want to configure custom platform detection rules, so that I can add support for platforms not built into the system.

#### Acceptance Criteria

1. WHEN a user adds a custom detection rule to configuration, THE System SHALL load the custom rule
2. WHEN the System evaluates custom rules, THE System SHALL check custom rules before built-in rules
3. WHEN a custom rule matches a URL, THE System SHALL apply the associated preset
4. WHEN a custom rule specifies a URL Pattern, THE System SHALL use regular expression matching
5. WHEN a custom rule is invalid, THE System SHALL display a warning and skip the rule
