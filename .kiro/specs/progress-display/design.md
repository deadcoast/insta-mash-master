# Design Document: Progress Display

## Overview

Progress display provides real-time visual feedback during download operations in insta-mash. The design introduces a progress tracking system that monitors download state, calculates metrics (speed, ETA), and renders adaptive terminal UI using the Rich library. The implementation must handle various terminal configurations, support quiet/verbose modes, and provide comprehensive summaries upon completion.

The progress display integrates with gallery-dl's output stream, parsing progress events and transforming them into user-friendly visual representations. The design emphasizes terminal adaptation, ensuring usability across different terminal sizes and capabilities.

## Architecture

### High-Level Flow

```
Download Operation → Progress Events → Progress Tracker → Display Renderer → Terminal
                                            ↓
                                      Metrics Calculator
                                            ↓
                                    (Speed, ETA, Percentage)
```

### Components

1. **Progress Tracker**: Maintains download state and metrics
2. **Event Parser**: Extracts progress information from gallery-dl output
3. **Metrics Calculator**: Computes speed, ETA, and completion percentage
4. **Display Renderer**: Generates terminal output using Rich library
5. **Terminal Adapter**: Detects terminal capabilities and adjusts display
6. **Summary Generator**: Creates completion summaries

### Integration Points

- Intercepts gallery-dl stdout/stderr streams
- Uses Rich library for progress bars and formatting
- Integrates with CLI flags (--quiet, --verbose)
- Coordinates with download execution logic

## Components and Interfaces

### ProgressState

Tracks the current state of a download operation.

```python
@dataclass
class ProgressState:
    """Current state of download progress."""
    total_files: int
    completed_files: int
    current_file: str
    current_file_size: Optional[int]
    bytes_downloaded: int
    total_bytes: Optional[int]
    start_time: float
    last_update_time: float
    failed_count: int = 0
    
    def completion_percentage(self) -> float:
        """Calculate overall completion percentage."""
        pass
    
    def elapsed_time(self) -> float:
        """Calculate elapsed time in seconds."""
        pass
```

### MetricsCalculator

Calculates download metrics.

```python
class MetricsCalculator:
    """Calculates download speed and ETA."""
    
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.samples: deque[tuple[float, int]] = deque(maxlen=window_size)
    
    def add_sample(self, timestamp: float, bytes_downloaded: int) -> None:
        """Add a data point for metric calculation."""
        pass
    
    def current_speed(self) -> float:
        """Calculate current download speed in bytes/sec."""
        pass
    
    def estimate_eta(self, bytes_remaining: int) -> Optional[float]:
        """Estimate time remaining in seconds."""
        pass
    
    def format_speed(self, bytes_per_sec: float) -> str:
        """Format speed with appropriate units."""
        pass
    
    def format_eta(self, seconds: Optional[float]) -> str:
        """Format ETA as human-readable string."""
        pass
```

### TerminalAdapter

Detects and adapts to terminal capabilities.

```python
class TerminalAdapter:
    """Adapts display to terminal capabilities."""
    
    def __init__(self):
        self.is_tty = sys.stdout.isatty()
        self.supports_ansi = self._detect_ansi_support()
        self.width = self._get_terminal_width()
    
    def _detect_ansi_support(self) -> bool:
        """Detect if terminal supports ANSI escape codes."""
        pass
    
    def _get_terminal_width(self) -> int:
        """Get current terminal width in characters."""
        pass
    
    def should_use_rich_display(self) -> bool:
        """Determine if Rich animated display should be used."""
        pass
    
    def get_display_mode(self) -> str:
        """Return 'full', 'compact', or 'simple' based on terminal."""
        pass
```

### ProgressRenderer

Renders progress display using Rich library.

```python
class ProgressRenderer:
    """Renders progress display to terminal."""
    
    def __init__(
        self,
        adapter: TerminalAdapter,
        quiet: bool = False,
        verbose: bool = False,
    ):
        self.adapter = adapter
        self.quiet = quiet
        self.verbose = verbose
        self.progress = None  # Rich Progress instance
        self.task_id = None
    
    def start(self, total_files: int) -> None:
        """Initialize progress display."""
        pass
    
    def update(self, state: ProgressState, metrics: dict) -> None:
        """Update progress display with current state."""
        pass
    
    def finish(self, summary: DownloadSummary) -> None:
        """Display completion summary and cleanup."""
        pass
    
    def _render_full(self, state: ProgressState, metrics: dict) -> None:
        """Render full progress display (terminal width >= 80)."""
        pass
    
    def _render_compact(self, state: ProgressState, metrics: dict) -> None:
        """Render compact progress display (terminal width < 80)."""
        pass
    
    def _render_simple(self, state: ProgressState) -> None:
        """Render simple text progress (no ANSI support)."""
        pass
    
    def _truncate_filename(self, filename: str, max_width: int) -> str:
        """Truncate filename with ellipsis if too long."""
        pass
```

### ProgressTracker

Main orchestrator for progress tracking.

```python
class ProgressTracker:
    """Orchestrates progress tracking and display."""
    
    def __init__(
        self,
        renderer: ProgressRenderer,
        calculator: MetricsCalculator,
    ):
        self.renderer = renderer
        self.calculator = calculator
        self.state = None
    
    def start_session(self, total_files: int, total_bytes: Optional[int] = None) -> None:
        """Start a new download session."""
        pass
    
    def start_file(self, filename: str, file_size: Optional[int] = None) -> None:
        """Mark start of a new file download."""
        pass
    
    def update_progress(self, bytes_downloaded: int) -> None:
        """Update progress with new byte count."""
        pass
    
    def complete_file(self, success: bool) -> None:
        """Mark current file as complete."""
        pass
    
    def finish_session(self) -> DownloadSummary:
        """Complete the session and return summary."""
        pass
```

### DownloadSummary

Summary of completed download session.

```python
@dataclass
class DownloadSummary:
    """Summary of a completed download session."""
    total_files: int
    successful_files: int
    failed_files: int
    total_bytes: int
    elapsed_time: float
    average_speed: float
    
    def format(self) -> str:
        """Format summary as human-readable string."""
        pass
```

## Data Models

### Progress Events

The system processes events from gallery-dl output:

```python
@dataclass
class ProgressEvent:
    """Event from gallery-dl progress stream."""
    event_type: str  # 'start', 'progress', 'complete', 'error'
    filename: Optional[str] = None
    file_size: Optional[int] = None
    bytes_downloaded: Optional[int] = None
    error_message: Optional[str] = None
```

### Display Modes

Three display modes based on terminal capabilities:

1. **Full Mode** (width >= 80, ANSI support):
   ```
   Downloading: image_001.jpg (2.4 MB) [File 5/20]
   ████████████████░░░░░░░░░░░░ 45% | 1.2 MB/s | ETA: 00:15
   ```

2. **Compact Mode** (width < 80, ANSI support):
   ```
   [5/20] image_001.jpg
   ████████░░░░ 45% | 1.2 MB/s
   ```

3. **Simple Mode** (no ANSI support):
   ```
   [5/20] Downloading: image_001.jpg (45%)
   ```

## Error Handling

### Error Categories

1. **Terminal Detection Errors**: Cannot determine terminal capabilities
2. **Rendering Errors**: Rich library fails to render
3. **Metric Calculation Errors**: Invalid data for speed/ETA calculation
4. **Stream Parsing Errors**: Cannot parse gallery-dl output

### Error Handling Strategy

- **Terminal Detection Errors**: Fall back to simple text mode
- **Rendering Errors**: Fall back to simple text mode, log error if verbose
- **Metric Calculation Errors**: Display "N/A" for unavailable metrics
- **Stream Parsing Errors**: Log warning if verbose, continue with last known state

### Quiet Mode Behavior

When `--quiet` flag is specified:
- Suppress all progress display output
- Still write errors to stderr
- Still generate summary (but don't display it)
- Return summary for programmatic access

### Verbose Mode Behavior

When `--verbose` flag is specified:
- Display all standard progress information
- Add debug information (event timestamps, raw metrics)
- Log terminal detection results
- Show detailed error messages

## Testing Strategy

### Unit Tests

1. **ProgressState**: Test state tracking and calculations
   - Completion percentage calculation
   - Elapsed time calculation
   - State updates

2. **MetricsCalculator**: Test metric calculations
   - Speed calculation with various data rates
   - ETA estimation with different progress rates
   - Speed formatting (bytes/sec, KB/s, MB/s)
   - ETA formatting (seconds, minutes, hours)

3. **TerminalAdapter**: Test terminal detection
   - TTY detection
   - ANSI support detection
   - Width detection
   - Display mode selection

4. **ProgressRenderer**: Test rendering logic
   - Filename truncation
   - Mode selection based on terminal
   - Quiet mode suppression
   - Verbose mode additions

5. **ProgressTracker**: Test orchestration
   - Session lifecycle
   - File transitions
   - Progress updates
   - Summary generation

### Property-Based Tests

Property-based tests will use Hypothesis library to verify universal properties across many randomly generated inputs. Each test will run a minimum of 100 iterations.

### Integration Tests

1. **End-to-end progress display**: Simulate download, verify progress updates
2. **Terminal adaptation**: Test with various terminal widths
3. **Mode switching**: Test quiet and verbose modes
4. **Summary generation**: Verify summary accuracy with various download scenarios

### Manual Testing

1. Test with real downloads of various sizes
2. Test terminal resizing during downloads
3. Test in different terminal emulators
4. Test with piped output (non-TTY)
5. Test with very long filenames


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Progress percentage accuracy

*For any* download state with known total bytes and downloaded bytes, the calculated completion percentage should equal (downloaded / total) * 100.
**Validates: Requirements 1.2**

### Property 2: Progress bar updates on file completion

*For any* download session, when a file completes, the completed file count should increase by exactly one.
**Validates: Requirements 1.3**

### Property 3: Speed calculation accuracy

*For any* sequence of download samples with known timestamps and byte counts, the calculated speed should match the actual data rate within a reasonable margin.
**Validates: Requirements 2.1**

### Property 4: ETA calculation reasonableness

*For any* download with sufficient progress data, if an ETA is calculated, it should be a positive number and decrease as progress increases.
**Validates: Requirements 2.2**

### Property 5: Speed formatting for low speeds

*For any* download speed below 1024 bytes per second, the formatted speed string should contain "B/s" (bytes per second) units.
**Validates: Requirements 2.5**

### Property 6: Filename display presence

*For any* file being downloaded, the progress display output should contain the filename string.
**Validates: Requirements 3.1**

### Property 7: File size display when known

*For any* file with a known size, the progress display output should contain the file size value.
**Validates: Requirements 3.2**

### Property 8: File transition updates

*For any* multi-file download session, when file N completes and file N+1 starts, the displayed filename should change from file N's name to file N+1's name.
**Validates: Requirements 3.3**

### Property 9: File counter display

*For any* multi-file download with total count T and current file C, the progress display should show "C of T" or "[C/T]" format.
**Validates: Requirements 3.4**

### Property 10: Filename truncation

*For any* filename longer than the available display width, the rendered filename should be shorter than the display width and contain an ellipsis.
**Validates: Requirements 3.5**

### Property 11: Terminal width adaptation

*For any* terminal width W, if W < 80 the display should use compact format, and if W >= 80 the display should use full format.
**Validates: Requirements 4.1, 4.2**

### Property 12: Dynamic width adaptation

*For any* terminal width change during a session, the display format should adapt to match the new width within the next update.
**Validates: Requirements 4.3**

### Property 13: Non-ANSI fallback

*For any* terminal without ANSI support, the progress display should not contain ANSI escape codes.
**Validates: Requirements 4.4**

### Property 14: No newline accumulation

*For any* sequence of progress updates in ANSI mode, the number of newlines in the output should remain constant (updates should overwrite, not append).
**Validates: Requirements 4.5**

### Property 15: Summary file count accuracy

*For any* completed download session with F files successfully downloaded, the summary should display F as the file count.
**Validates: Requirements 5.1**

### Property 16: Summary byte count accuracy

*For any* completed download session with B total bytes downloaded, the summary should display B as the total data size.
**Validates: Requirements 5.2**

### Property 17: Summary elapsed time accuracy

*For any* completed download session with start time T1 and end time T2, the summary should display (T2 - T1) as the elapsed time.
**Validates: Requirements 5.3**

### Property 18: Summary average speed accuracy

*For any* completed download session with total bytes B and elapsed time T, the summary should display B/T as the average speed.
**Validates: Requirements 5.4**

### Property 19: Summary failure count accuracy

*For any* completed download session with E failed downloads, the summary should display E as the failure count.
**Validates: Requirements 5.5**

### Property 20: Quiet mode suppression

*For any* download operation with quiet flag enabled, the standard output should not contain progress display text.
**Validates: Requirements 6.1**

### Property 21: Quiet mode error preservation

*For any* download operation with quiet flag enabled and errors occurring, the standard error stream should contain error messages.
**Validates: Requirements 6.2**

### Property 22: Non-TTY output mode

*For any* download operation where output is not a TTY, the progress display should use simple text format without ANSI codes.
**Validates: Requirements 6.3, 6.4**

### Property 23: Verbose mode information

*For any* download operation with verbose flag enabled, the output should contain additional debug information beyond standard progress display.
**Validates: Requirements 6.5**

