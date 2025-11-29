# Requirements Document

## Introduction

This document specifies the requirements for resume support functionality in insta-mash. Resume support enables users to gracefully interrupt download operations and continue them later from where they left off, preventing data loss and avoiding redundant downloads. This feature is essential for handling large downloads, unstable connections, and user workflow flexibility.

## Glossary

- **Resume Support**: The ability to pause and continue download operations without losing progress
- **System**: The insta-mash application
- **Download Session**: A single execution of a download command from start to completion or interruption
- **Interrupt Signal**: A signal sent by the user or system to stop the current operation
- **Resume State**: Persistent data tracking which files have been downloaded
- **Checkpoint**: A point during download where progress is saved
- **Partial Download**: A file that was partially downloaded before interruption

## Requirements

### Requirement 1

**User Story:** As a user, I want to interrupt downloads gracefully, so that I can stop operations without corrupting files or losing progress.

#### Acceptance Criteria

1. WHEN a user sends an interrupt signal during a Download Session, THE System SHALL complete the current file download before stopping
2. WHEN the System receives an interrupt signal, THE System SHALL save the Resume State
3. WHEN the System saves the Resume State, THE System SHALL include all successfully downloaded file identifiers
4. WHEN the System completes saving the Resume State, THE System SHALL exit with status code one hundred thirty
5. WHEN the System receives a second interrupt signal, THE System SHALL terminate immediately without saving state

### Requirement 2

**User Story:** As a user, I want to resume interrupted downloads, so that I can continue from where I left off without re-downloading files.

#### Acceptance Criteria

1. WHEN a user invokes a download command with a Resume State present, THE System SHALL load the Resume State
2. WHEN the System loads a Resume State, THE System SHALL skip files that were already downloaded
3. WHEN the System resumes a download, THE System SHALL display the number of files being skipped
4. WHEN the System completes a resumed download, THE System SHALL delete the Resume State file
5. WHEN the System encounters a Resume State for a different URL, THE System SHALL ignore the Resume State and start fresh

### Requirement 3

**User Story:** As a user, I want partial downloads to be handled correctly, so that incomplete files don't cause issues.

#### Acceptance Criteria

1. WHEN the System is interrupted during a file download, THE System SHALL delete the Partial Download
2. WHEN the System resumes a download, THE System SHALL re-download any files that were incomplete
3. WHEN the System completes downloading a file, THE System SHALL verify the file size matches the expected size if known
4. WHEN a file fails verification, THE System SHALL mark the file as incomplete in the Resume State
5. WHEN the System encounters a Partial Download on resume, THE System SHALL delete it before re-downloading

### Requirement 4

**User Story:** As a user, I want resume state to be stored safely, so that I can resume even after system crashes or power loss.

#### Acceptance Criteria

1. WHEN the System saves Resume State, THE System SHALL write to a temporary file first
2. WHEN the System completes writing the temporary file, THE System SHALL atomically rename it to the final Resume State file
3. WHEN the System saves Resume State, THE System SHALL include a timestamp
4. WHEN the System loads Resume State, THE System SHALL validate the file format
5. WHEN the System encounters corrupted Resume State, THE System SHALL display a warning and start fresh

### Requirement 5

**User Story:** As a user, I want to manage resume state manually, so that I can clear stale state or force re-downloads.

#### Acceptance Criteria

1. WHEN a user invokes the resume clear command, THE System SHALL delete all Resume State files
2. WHEN a user invokes the resume list command, THE System SHALL display all existing Resume State files with timestamps
3. WHEN a user invokes the resume show command with a state file, THE System SHALL display the contents of that Resume State
4. WHEN a user specifies the no-resume flag, THE System SHALL ignore any existing Resume State
5. WHEN a user specifies the no-resume flag, THE System SHALL not create new Resume State on interrupt

### Requirement 6

**User Story:** As a user, I want resume support to work with archive files, so that duplicate detection and resume work together.

#### Acceptance Criteria

1. WHEN the System uses an archive file and Resume State, THE System SHALL update the archive file for each completed download
2. WHEN the System resumes with an archive file, THE System SHALL skip files present in both the archive and Resume State
3. WHEN the System completes a resumed download, THE System SHALL ensure the archive file contains all downloaded files
4. WHEN the System is interrupted, THE System SHALL ensure the archive file is consistent with the Resume State
5. WHEN the System detects a mismatch between archive and Resume State, THE System SHALL use the Resume State as authoritative
