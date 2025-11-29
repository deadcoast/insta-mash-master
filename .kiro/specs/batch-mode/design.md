# Design Document: Batch Mode

## Overview

Batch mode extends insta-mash to process multiple URLs from an input file in a single execution. The design introduces a new `batch` command that reads a specially-formatted text file, parses URL entries with optional per-URL configuration, and executes downloads sequentially while providing progress feedback and error resilience.

The implementation leverages the existing configuration system (profiles, presets) and download execution logic, adding a new orchestration layer that manages multiple download operations with state tracking for pause/resume functionality.

## Architecture

### High-Level Flow

```
Input File → Parser → Validator → Executor → Reporter
                ↓                     ↓
            URL Entries          Progress Tracker
                                      ↓
                                 Resume State
```

### Components

1. **Batch Parser**: Reads and parses the input file into structured URL entries
2. **Batch Validator**: Validates URL entries and configuration references
3. **Batch Executor**: Orchestrates sequential download operations
4. **Progress Tracker**: Monitors and displays batch progress
5. **Resume Manager**: Handles pause/resume state persistence
6. **Batch Reporter**: Generates summary reports of batch execution

### Integration Points

- Reuses `Config.resolve_options()` for per-URL configuration merging
- Reuses `grab` command logic for individual download execution
- Extends CLI with new `batch` command group
- Integrates with existing validation system

## Components and Interfaces

### BatchEntry

Represents a single URL entry from the input file.

```python
@dataclass
class BatchEntry:
    """A single entry in a batch file."""
    line_number: int
    url: str
    preset: str = ""
    profile: str = ""
    options: Optional[DownloadOptions] = None
    
    @classmethod
    def parse(cls, line: str, line_number: int) -> Optional[BatchEntry]:
        """Parse a line from batch file into BatchEntry."""
        pass
```

### BatchFile

Represents the parsed batch file with all entries.

```python
@dataclass
class BatchFile:
    """Parsed batch file with all entries."""
    path: Path
    entries: list[BatchEntry]
    
    @classmethod
    def load(cls, path: Path) -> BatchFile:
        """Load and parse a batch file."""
        pass
    
    def validate(self, config: Config) -> list[ValidationError]:
        """Validate all entries against current config."""
        pass
```

### BatchProgress

Tracks progress during batch execution.

```python
@dataclass
class BatchProgress:
    """Tracks batch execution progress."""
    total: int
    completed: int
    succeeded: int
    failed: int
    current_url: str = ""
    
    def update(self, success: bool) -> None:
        """Update progress after completing a download."""
        pass
    
    def display(self) -> None:
        """Display current progress to console."""
        pass
```

### ResumeState

Manages pause/resume state persistence.

```python
@dataclass
class ResumeState:
    """State for resuming interrupted batch operations."""
    batch_file_path: Path
    completed_indices: set[int]
    timestamp: datetime
    
    def save(self, path: Path) -> None:
        """Save resume state to file."""
        pass
    
    @classmethod
    def load(cls, path: Path) -> Optional[ResumeState]:
        """Load resume state from file."""
        pass
```

### BatchExecutor

Orchestrates batch execution.

```python
class BatchExecutor:
    """Executes batch downloads with progress tracking."""
    
    def __init__(
        self,
        batch_file: BatchFile,
        config: Config,
        delay: float = 0.0,
        dry_run: bool = False,
        resume_state: Optional[ResumeState] = None,
    ):
        self.batch_file = batch_file
        self.config = config
        self.delay = delay
        self.dry_run = dry_run
        self.resume_state = resume_state
        self.progress = BatchProgress(total=len(batch_file.entries))
        
    def execute(self) -> BatchProgress:
        """Execute all downloads in batch."""
        pass
    
    def execute_entry(self, entry: BatchEntry) -> bool:
        """Execute a single batch entry. Returns success status."""
        pass
```

## Data Models

### Batch File Format

The input file uses a simple line-based format:

```
# Comments start with hash
https://instagram.com/user1
https://instagram.com/user2 preset:instagram
https://twitter.com/user3 profile:slow
https://reddit.com/r/pics preset:reddit profile:archive

# Empty lines are ignored

# Inline options (future enhancement)
https://example.com --sleep 2.0 --destination ./custom
```

### Parsing Rules

1. Lines starting with `#` are comments (ignored)
2. Empty lines are ignored
3. First token is the URL (required)
4. Subsequent tokens are configuration in format `key:value`
5. Recognized keys: `preset`, `profile`
6. Invalid lines generate warnings and are skipped

### Resume State Format

Resume state is stored as JSON:

```json
{
  "batch_file_path": "/path/to/batch.txt",
  "completed_indices": [0, 1, 2, 5],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Handling

### Error Categories

1. **File Errors**: Input file not found, not readable, or invalid format
2. **Parse Errors**: Invalid syntax in batch file entries
3. **Configuration Errors**: Referenced presets/profiles don't exist
4. **Download Errors**: Individual download operations fail
5. **Interrupt Errors**: User interrupts batch execution

### Error Handling Strategy

- **File Errors**: Fail fast, display error, exit with code 1
- **Parse Errors**: Log warning with line number, skip entry, continue
- **Configuration Errors**: Log warning with line number, skip entry, continue
- **Download Errors**: Log error, mark as failed, continue to next entry
- **Interrupt Errors**: Save resume state, display progress, exit with code 130

### Error Reporting

All errors are logged to console with:
- Error type and message
- Line number (for parse/config errors)
- URL (for download errors)
- Timestamp

## Testing Strategy

### Unit Tests

1. **BatchEntry.parse()**: Test parsing various line formats
   - Valid URL only
   - URL with preset
   - URL with profile
   - URL with both preset and profile
   - Invalid formats
   - Edge cases (whitespace, special characters)

2. **BatchFile.load()**: Test file loading
   - Valid batch files
   - Files with comments and empty lines
   - Mixed valid and invalid entries
   - Empty files
   - Non-existent files

3. **BatchFile.validate()**: Test validation logic
   - Valid entries with existing presets/profiles
   - Invalid preset references
   - Invalid profile references
   - Mixed valid and invalid entries

4. **ResumeState**: Test state persistence
   - Save and load resume state
   - Handle corrupted resume files
   - Verify completed indices tracking

5. **BatchProgress**: Test progress tracking
   - Update counts correctly
   - Display formatting
   - Edge cases (0 total, all failed)

### Integration Tests

1. **End-to-end batch execution**: Create test batch file, execute, verify all downloads attempted
2. **Resume functionality**: Start batch, interrupt, resume, verify skips completed entries
3. **Error resilience**: Batch with mix of valid and invalid URLs, verify continues after failures
4. **Configuration merging**: Verify per-URL presets/profiles override defaults correctly
5. **Dry-run mode**: Verify no actual downloads occur in dry-run

### Manual Testing

1. Test with real Instagram/Twitter URLs
2. Test interrupt and resume with large batches
3. Test progress display with various terminal sizes
4. Test validation command with various error conditions


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: File reading completeness

*For any* valid batch file with N non-comment, non-empty lines, parsing the file should produce exactly N BatchEntry objects.
**Validates: Requirements 1.1, 1.2**

### Property 2: Order preservation

*For any* list of URLs in a batch file, the order of parsed BatchEntry objects should match the order of URLs in the file.
**Validates: Requirements 1.5**

### Property 3: Default configuration application

*For any* BatchEntry without preset or profile specified, resolving its configuration should produce options that match the system defaults.
**Validates: Requirements 2.1**

### Property 4: Preset application

*For any* BatchEntry with a preset specified, the resolved configuration should contain all options from that preset.
**Validates: Requirements 2.2**

### Property 5: Profile application

*For any* BatchEntry with a profile specified, the resolved configuration should contain all options from that profile.
**Validates: Requirements 2.3**

### Property 6: Invalid entry skipping

*For any* batch file containing invalid entries, parsing should skip invalid entries and return only valid BatchEntry objects.
**Validates: Requirements 2.4**

### Property 7: Configuration merging priority

*For any* BatchEntry with both global and entry-specific configuration, the entry-specific configuration should override global configuration for conflicting options.
**Validates: Requirements 2.5**

### Property 8: Progress tracking accuracy

*For any* batch execution, after processing N entries, the progress counter should show N completed out of total.
**Validates: Requirements 3.2**

### Property 9: Status reporting accuracy

*For any* completed download operation, the progress display should indicate success if the operation succeeded and failure if it failed.
**Validates: Requirements 3.3**

### Property 10: Current URL display

*For any* batch entry being processed, the progress display should show the URL from that entry.
**Validates: Requirements 3.4**

### Property 11: Final report accuracy

*For any* completed batch session with S successes and F failures, the final report should display S as success count and F as failure count.
**Validates: Requirements 3.5**

### Property 12: Error logging

*For any* failed download operation, the system should log error details including the URL and error message.
**Validates: Requirements 4.1**

### Property 13: Failure resilience

*For any* batch file where entry N fails, the system should still attempt to process entry N+1.
**Validates: Requirements 4.2**

### Property 14: Exit code on failure

*For any* batch session with at least one failure, the system should exit with a non-zero status code.
**Validates: Requirements 4.4**

### Property 15: Exit code on success

*For any* batch session with zero failures, the system should exit with status code 0.
**Validates: Requirements 4.5**

### Property 16: Resume state persistence

*For any* paused batch session, the resume file should contain the indices of all completed entries.
**Validates: Requirements 5.2**

### Property 17: Resume skip behavior

*For any* batch execution with a resume state, entries whose indices are in the completed set should be skipped.
**Validates: Requirements 5.3**

### Property 18: Delay timing

*For any* batch execution with delay D specified, the time between starting consecutive download operations should be at least D seconds.
**Validates: Requirements 5.4**

### Property 19: Dry-run file creation

*For any* batch execution in dry-run mode, no media files should be created in the destination directories.
**Validates: Requirements 5.5**

### Property 20: Validation parsing

*For any* batch file, the validate command should parse all entries and return a list of validation results.
**Validates: Requirements 6.1**

### Property 21: Validation error reporting

*For any* batch file with syntax errors on lines L1, L2, ..., Ln, the validation report should include line numbers L1, L2, ..., Ln.
**Validates: Requirements 6.2**

### Property 22: Validation reference checking

*For any* batch file referencing non-existent presets or profiles, the validation report should identify those invalid references.
**Validates: Requirements 6.3**

### Property 23: Validation count accuracy

*For any* batch file with V valid entries, the validation report should show V as the count of valid entries.
**Validates: Requirements 6.4**

### Property 24: Validation exit code

*For any* batch file with zero validation errors, the validate command should exit with status code 0.
**Validates: Requirements 6.5**
