# Requirements Document

## Introduction

This document specifies the requirements for batch mode functionality in insta-mash. Batch mode enables users to download media from multiple URLs in a single operation by reading URLs from an input file. This feature streamlines bulk downloading operations and reduces manual intervention for users who need to process multiple sources.

## Glossary

- **Batch Mode**: An operational mode where the System processes multiple URLs sequentially from an input file
- **Input File**: A text file containing one or more URLs to be processed
- **Batch Session**: A single execution of batch mode from start to completion
- **URL Entry**: A single line in the Input File containing a URL and optional configuration
- **System**: The insta-mash application
- **Download Operation**: The process of fetching media from a single URL using gallery-dl
- **Batch Report**: A summary of results from processing all URLs in a Batch Session

## Requirements

### Requirement 1

**User Story:** As a user, I want to provide a file containing multiple URLs, so that I can download from all of them without manual intervention.

#### Acceptance Criteria

1. WHEN a user invokes the batch command with an Input File path, THE System SHALL read all URLs from the Input File
2. WHEN the System reads the Input File, THE System SHALL process one URL per line
3. WHEN the System encounters an empty line in the Input File, THE System SHALL skip the empty line and continue processing
4. WHEN the System encounters a line starting with a hash character in the Input File, THE System SHALL treat the line as a comment and skip it
5. WHEN the System completes reading the Input File, THE System SHALL process each URL Entry sequentially in the order they appear

### Requirement 2

**User Story:** As a user, I want to apply different configurations to different URLs in my batch file, so that I can customize download behavior per source.

#### Acceptance Criteria

1. WHEN a URL Entry contains only a URL, THE System SHALL apply the default configuration to that Download Operation
2. WHEN a URL Entry contains a URL followed by a preset name, THE System SHALL apply the specified preset to that Download Operation
3. WHEN a URL Entry contains a URL followed by a profile name, THE System SHALL apply the specified profile to that Download Operation
4. WHEN a URL Entry contains invalid configuration syntax, THE System SHALL log a warning and skip that URL Entry
5. WHEN the System applies configuration to a URL Entry, THE System SHALL merge the entry-specific configuration with global batch settings

### Requirement 3

**User Story:** As a user, I want to see progress as my batch downloads, so that I can monitor the operation and estimate completion time.

#### Acceptance Criteria

1. WHEN the System starts a Batch Session, THE System SHALL display the total number of URL Entries to be processed
2. WHEN the System completes a Download Operation, THE System SHALL display the current progress as a ratio of completed to total URLs
3. WHEN the System completes a Download Operation, THE System SHALL display whether the operation succeeded or failed
4. WHEN the System processes each URL Entry, THE System SHALL display the current URL being processed
5. WHEN the System completes the Batch Session, THE System SHALL display a Batch Report with success and failure counts

### Requirement 4

**User Story:** As a user, I want batch mode to handle errors gracefully, so that one failed download does not stop the entire batch.

#### Acceptance Criteria

1. WHEN a Download Operation fails, THE System SHALL log the error details
2. WHEN a Download Operation fails, THE System SHALL continue processing the next URL Entry
3. WHEN the System encounters an unreadable Input File, THE System SHALL display an error message and terminate the Batch Session
4. WHEN the System completes a Batch Session with failures, THE System SHALL exit with a non-zero status code
5. WHEN the System completes a Batch Session with all successes, THE System SHALL exit with a zero status code

### Requirement 5

**User Story:** As a user, I want to control batch execution behavior, so that I can pause, resume, or limit concurrent operations.

#### Acceptance Criteria

1. WHEN a user sends an interrupt signal during a Batch Session, THE System SHALL complete the current Download Operation and then pause
2. WHEN the System pauses a Batch Session, THE System SHALL save the current progress to a resume file
3. WHEN a user invokes batch mode with a resume file, THE System SHALL skip already-completed URL Entries
4. WHEN a user specifies a delay between downloads in batch mode, THE System SHALL wait the specified duration between Download Operations
5. WHEN a user specifies a dry-run flag in batch mode, THE System SHALL simulate all Download Operations without downloading files

### Requirement 6

**User Story:** As a user, I want to validate my batch file before running it, so that I can catch errors early.

#### Acceptance Criteria

1. WHEN a user invokes the validate command with an Input File, THE System SHALL parse all URL Entries
2. WHEN the System validates an Input File, THE System SHALL report any syntax errors with line numbers
3. WHEN the System validates an Input File, THE System SHALL verify that all referenced presets and profiles exist
4. WHEN the System validates an Input File, THE System SHALL report the total number of valid URL Entries
5. WHEN the System completes validation with no errors, THE System SHALL exit with a zero status code
