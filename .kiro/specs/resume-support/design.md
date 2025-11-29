# Design Document: Resume Support

## Overview

Resume support enables graceful interruption and continuation of download operations in insta-mash. The design introduces a persistent state management system that tracks download progress, handles interrupt signals, manages partial files, and coordinates with archive files for duplicate detection. The implementation must ensure data integrity through atomic file operations, handle corrupted state gracefully, and provide manual state management commands.

The resume system integrates with gallery-dl's download process, intercepting signals, tracking file completion, and maintaining a persistent state file that survives crashes and power loss. The design emphasizes robustness, idempotency, and seamless integration with existing features like archive files and progress display.

## Architecture

### High-Level Flow

```
Download Start → Check Resume State → Skip Completed Files → Download Remaining
                        ↓                                              ↓
                   Load State                                    Track Progress
                        ↓                                              ↓
                   Validate                                      Save Checkpoints
                                                                       ↓
Interrupt Signal → Complete Current File → Save State → Exit (130)
                                                  ↓
                                          Atomic Write (temp → final)
```

### Components

1. **Resume State Manager**: Manages state persistence and loading
2. **Signal Handler**: Intercepts interrupt signals (SIGINT, SIGTERM)
3. **File Tracker**: Tracks completed and partial downloads
4. **State Validator**: Validates resume state format and integrity
5. **Archive Coordinator**: Synchronizes resume state with archive files
6. **Resume CLI**: Provides manual state management commands

### Integration Points

- Intercepts system signals (SIGINT, SIGTERM)
- Coordinates with gallery-dl download process
- Integrates with archive file system
- Works with progress display for skip notifications
- Provides CLI commands for state management

## Components and Interfaces

### ResumeState

Represents the persistent state of a download session.

```python
@dataclass
class ResumeState:
    """Persistent state for resuming downloads."""
    url: str
    timestamp: float
    completed_files: list[str]  # File identifiers (URLs or paths)
    total_files: Optional[int]
    version: str = "1.0"  # State format version
    
    def to_dict(self) -> dict:
        """Serialize state to dictionary."""
        pass
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ResumeState':
        """Deserialize state from dictionary."""
        pass
    
    def matches_url(self, url: str) -> bool:
        """Check if state matches the given URL."""
        pass
```

### ResumeStateManager

Manages state persistence with atomic operations.

```python
class ResumeStateManager:
    """Manages resume state persistence."""
    
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
    
    def save_state(self, state: ResumeState, url: str) -> None:
        """Save resume state atomically."""
        pass
    
    def load_state(self, url: str) -> Optional[ResumeState]:
        """Load resume state for given URL."""
        pass
    
    def delete_state(self, url: str) -> None:
        """Delete resume state for given URL."""
        pass
    
    def list_states(self) -> list[tuple[str, ResumeState]]:
        """List all resume states with their identifiers."""
        pass
    
    def clear_all_states(self) -> int:
        """Delete all resume states, return count deleted."""
        pass
    
    def _get_state_path(self, url: str) -> Path:
        """Get file path for state based on URL hash."""
        pass
    
    def _atomic_write(self, path: Path, content: str) -> None:
        """Write file atomically using temp file and rename."""
        pass
    
    def _validate_state(self, data: dict) -> bool:
        """Validate state file format and required fields."""
        pass
```

### SignalHandler

Handles interrupt signals gracefully.

```python
class SignalHandler:
    """Handles interrupt signals for graceful shutdown."""
    
    def __init__(self, on_interrupt: Callable[[], None]):
        self.on_interrupt = on_interrupt
        self.interrupt_count = 0
        self.interrupted = False
    
    def setup(self) -> None:
        """Register signal handlers."""
        pass
    
    def handle_signal(self, signum: int, frame) -> None:
        """Handle interrupt signal."""
        pass
    
    def is_interrupted(self) -> bool:
        """Check if interrupt was received."""
        pass
    
    def should_force_exit(self) -> bool:
        """Check if second interrupt was received."""
        pass
```

### FileTracker

Tracks file download progress.

```python
class FileTracker:
    """Tracks file download progress."""
    
    def __init__(self, resume_state: Optional[ResumeState] = None):
        self.completed_files: set[str] = set()
        self.current_file: Optional[str] = None
        self.partial_files: set[Path] = set()
        
        if resume_state:
            self.completed_files = set(resume_state.completed_files)
    
    def start_file(self, file_id: str, file_path: Path) -> bool:
        """Mark file as started, return True if should download."""
        pass
    
    def complete_file(self, file_id: str, file_path: Path, expected_size: Optional[int] = None) -> bool:
        """Mark file as complete, return True if verification passed."""
        pass
    
    def should_skip(self, file_id: str) -> bool:
        """Check if file should be skipped."""
        pass
    
    def mark_partial(self, file_path: Path) -> None:
        """Mark file as partial download."""
        pass
    
    def cleanup_partial(self, file_path: Path) -> None:
        """Delete partial download file."""
        pass
    
    def verify_file_size(self, file_path: Path, expected_size: int) -> bool:
        """Verify downloaded file size matches expected."""
        pass
    
    def get_completed_count(self) -> int:
        """Get count of completed files."""
        pass
```

### ArchiveCoordinator

Coordinates resume state with archive files.

```python
class ArchiveCoordinator:
    """Coordinates resume state with archive files."""
    
    def __init__(
        self,
        archive_path: Optional[Path],
        state_manager: ResumeStateManager,
    ):
        self.archive_path = archive_path
        self.state_manager = state_manager
        self.archive_entries: set[str] = set()
        
        if archive_path and archive_path.exists():
            self._load_archive()
    
    def _load_archive(self) -> None:
        """Load existing archive entries."""
        pass
    
    def should_skip_file(self, file_id: str, in_resume_state: bool) -> bool:
        """Determine if file should be skipped based on archive and resume state."""
        pass
    
    def update_archive(self, file_id: str) -> None:
        """Add file to archive."""
        pass
    
    def ensure_consistency(self, resume_state: ResumeState) -> None:
        """Ensure archive is consistent with resume state."""
        pass
    
    def resolve_conflict(self, file_id: str, in_archive: bool, in_state: bool) -> bool:
        """Resolve conflict between archive and state, return True if should skip."""
        pass
```

### ResumeDownloadSession

Orchestrates a resumable download session.

```python
class ResumeDownloadSession:
    """Orchestrates a resumable download session."""
    
    def __init__(
        self,
        url: str,
        state_manager: ResumeStateManager,
        archive_coordinator: Optional[ArchiveCoordinator],
        no_resume: bool = False,
    ):
        self.url = url
        self.state_manager = state_manager
        self.archive_coordinator = archive_coordinator
        self.no_resume = no_resume
        self.file_tracker: Optional[FileTracker] = None
        self.signal_handler: Optional[SignalHandler] = None
    
    def start(self) -> tuple[FileTracker, int]:
        """Start session, return tracker and skip count."""
        pass
    
    def on_file_start(self, file_id: str, file_path: Path) -> bool:
        """Handle file start, return True if should download."""
        pass
    
    def on_file_complete(self, file_id: str, file_path: Path, expected_size: Optional[int]) -> None:
        """Handle file completion."""
        pass
    
    def on_interrupt(self) -> None:
        """Handle interrupt signal."""
        pass
    
    def finish(self, success: bool) -> None:
        """Finish session and cleanup."""
        pass
    
    def _load_resume_state(self) -> Optional[ResumeState]:
        """Load and validate resume state."""
        pass
    
    def _save_checkpoint(self) -> None:
        """Save current progress as checkpoint."""
        pass
```

## Data Models

### State File Format

Resume state is stored as JSON:

```json
{
  "version": "1.0",
  "url": "https://example.com/gallery/12345",
  "timestamp": 1701234567.89,
  "total_files": 50,
  "completed_files": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg",
    "https://example.com/image3.jpg"
  ]
}
```

### State File Location

State files are stored in `~/.config/insta-mash/resume/` with filenames based on URL hash:
- Filename: `{sha256(url)[:16]}.json`
- Example: `a1b2c3d4e5f6g7h8.json`

### File Identifiers

Files are identified by their source URL, which provides a stable identifier across sessions.

## Error Handling

### Error Categories

1. **State Corruption**: Resume state file is corrupted or invalid
2. **State Version Mismatch**: Resume state uses incompatible version
3. **File System Errors**: Cannot read/write state files
4. **Signal Handling Errors**: Cannot register signal handlers
5. **Verification Failures**: Downloaded file size doesn't match expected
6. **Archive Conflicts**: Mismatch between archive and resume state

### Error Handling Strategy

- **State Corruption**: Display warning, delete corrupted state, start fresh
- **State Version Mismatch**: Display warning about version, attempt migration or start fresh
- **File System Errors**: Display error message, exit with non-zero status
- **Signal Handling Errors**: Log warning, continue without resume support
- **Verification Failures**: Mark file as incomplete, will be re-downloaded on resume
- **Archive Conflicts**: Use resume state as authoritative, update archive to match

### Atomic Operations

All state saves use atomic write pattern:
1. Write to temporary file (`.tmp` suffix)
2. Flush and sync to disk
3. Atomically rename to final filename
4. This ensures state file is never partially written

### Double Interrupt Handling

- First interrupt: Complete current file, save state, exit with code 130
- Second interrupt: Terminate immediately without saving, exit with code 130
- This allows users to force-quit if needed

## Testing Strategy

### Unit Tests

1. **ResumeState**: Test serialization/deserialization
   - Round-trip JSON conversion
   - URL matching logic
   - Version handling

2. **ResumeStateManager**: Test state persistence
   - Atomic write operations
   - State validation
   - File path generation from URL hash
   - List and clear operations

3. **SignalHandler**: Test signal handling
   - Single interrupt behavior
   - Double interrupt behavior
   - Interrupt flag checking

4. **FileTracker**: Test file tracking
   - Skip logic for completed files
   - Partial file cleanup
   - File size verification
   - Completion tracking

5. **ArchiveCoordinator**: Test archive integration
   - Archive loading
   - Skip logic with archive + state
   - Consistency enforcement
   - Conflict resolution

6. **ResumeDownloadSession**: Test session orchestration
   - Session lifecycle with resume
   - Checkpoint saving
   - Interrupt handling
   - Cleanup on completion

### Property-Based Tests

Property-based tests will use Hypothesis library to verify universal properties across many randomly generated inputs. Each test will run a minimum of 100 iterations. Each property-based test will be tagged with a comment explicitly referencing the correctness property from this design document using the format: '**Feature: resume-support, Property {number}: {property_text}**'.

### Integration Tests

1. **End-to-end resume**: Start download, interrupt, verify state, resume, verify completion
2. **Archive integration**: Test resume with archive file, verify skip logic
3. **Corruption handling**: Create corrupted state, verify graceful handling
4. **Manual commands**: Test resume list/show/clear commands
5. **No-resume flag**: Test that flag disables resume functionality

### Manual Testing

1. Test with real downloads and interrupts
2. Test with various network conditions
3. Test state persistence across system restarts
4. Test with very large file lists
5. Test archive file integration



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Current file completion before interrupt

*For any* download session that receives an interrupt signal while downloading a file, the system should complete that file before stopping.
**Validates: Requirements 1.1**

### Property 2: State persistence on interrupt

*For any* download session that receives an interrupt signal, a resume state file should exist after the interrupt is handled.
**Validates: Requirements 1.2**

### Property 3: Completed files in saved state

*For any* set of successfully downloaded files, all file identifiers should appear in the saved resume state.
**Validates: Requirements 1.3**

### Property 4: Interrupt exit code

*For any* download session that is interrupted and saves state, the exit code should be 130.
**Validates: Requirements 1.4**

### Property 5: Resume state loading

*For any* download command invoked with a valid resume state file present, the resume state should be loaded into memory.
**Validates: Requirements 2.1**

### Property 6: Completed file skipping

*For any* file identifier present in the resume state, that file should not be downloaded again during the resumed session.
**Validates: Requirements 2.2**

### Property 7: Skip count display

*For any* resumed download session with N files in the resume state, the output should display that N files are being skipped.
**Validates: Requirements 2.3**

### Property 8: State cleanup on completion

*For any* resumed download session that completes successfully, the resume state file should be deleted.
**Validates: Requirements 2.4**

### Property 9: URL mismatch handling

*For any* resume state with URL A and download command with URL B where A ≠ B, the resume state should be ignored and no files should be skipped.
**Validates: Requirements 2.5**

### Property 10: Partial download cleanup

*For any* file that is partially downloaded when an interrupt occurs or when resuming, the partial file should be deleted from the filesystem.
**Validates: Requirements 3.1, 3.5**

### Property 11: Incomplete file re-download

*For any* file marked as incomplete in the resume state, that file should be downloaded again during the resumed session.
**Validates: Requirements 3.2**

### Property 12: File size verification

*For any* completed file download with a known expected size, the actual file size should be verified against the expected size.
**Validates: Requirements 3.3**

### Property 13: Failed verification state update

*For any* file that fails size verification, the file identifier should be marked as incomplete (or absent) in the resume state.
**Validates: Requirements 3.4**

### Property 14: Atomic state persistence

*For any* resume state save operation, the state should be written to a temporary file first, then atomically renamed to the final filename, and the final state should include a timestamp.
**Validates: Requirements 4.1, 4.2, 4.3**

### Property 15: State format validation

*For any* resume state load operation, the state file format should be validated before use.
**Validates: Requirements 4.4**

### Property 16: Corrupted state handling

*For any* corrupted or invalid resume state file, the system should display a warning and proceed with a fresh download.
**Validates: Requirements 4.5**

### Property 17: Clear command deletion

*For any* invocation of the resume clear command, all resume state files should be deleted from the state directory.
**Validates: Requirements 5.1**

### Property 18: List command output

*For any* invocation of the resume list command, all existing resume state files should be displayed with their timestamps.
**Validates: Requirements 5.2**

### Property 19: Show command output

*For any* invocation of the resume show command with a valid state file, the contents of that state should be displayed.
**Validates: Requirements 5.3**

### Property 20: No-resume flag state ignore

*For any* download command with the no-resume flag set and existing resume state, the resume state should be ignored and all files should be downloaded.
**Validates: Requirements 5.4**

### Property 21: No-resume flag state creation

*For any* download session with the no-resume flag set that is interrupted, no resume state file should be created.
**Validates: Requirements 5.5**

### Property 22: Archive update on completion

*For any* download session using an archive file, when a file completes downloading, that file identifier should be added to the archive file.
**Validates: Requirements 6.1**

### Property 23: Archive and state skip logic

*For any* file identifier present in both the archive file and resume state, that file should be skipped during the resumed session.
**Validates: Requirements 6.2**

### Property 24: Archive completeness on finish

*For any* resumed download session that completes successfully with an archive file, the archive file should contain all downloaded file identifiers.
**Validates: Requirements 6.3**

### Property 25: Archive-state consistency

*For any* download session using both archive and resume state, when interrupted or completed, the archive file should be consistent with the resume state (resume state is authoritative).
**Validates: Requirements 6.4, 6.5**
