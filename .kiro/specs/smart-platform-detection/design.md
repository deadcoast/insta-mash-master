# Design Document: Smart Platform Detection

## Overview

Smart platform detection automatically identifies the source platform from a URL and applies appropriate presets without requiring manual user specification. The design introduces a pattern-matching system that recognizes common social media platforms (Instagram, Twitter, Reddit, TikTok, Tumblr) and applies optimized download settings automatically.

The implementation adds a detection layer that runs before download execution, analyzing URLs against built-in and custom patterns, determining the best matching platform, and applying the corresponding preset. Users retain full control through explicit preset specification and opt-out flags.

## Architecture

### High-Level Flow

```
URL Input → Platform Detector → Preset Resolver → Download Executor
                ↓                      ↓
         Pattern Matcher        Config Merger
                ↓
         Confidence Scorer
```

### Components

1. **Platform Detector**: Analyzes URLs and identifies source platforms
2. **Pattern Matcher**: Matches URLs against platform-specific patterns
3. **Confidence Scorer**: Evaluates detection certainty
4. **Preset Resolver**: Determines which preset to apply based on detection
5. **Config Merger**: Combines auto-detected presets with user configuration
6. **Detection Reporter**: Displays detection results and applied presets

### Integration Points

- Runs before download execution in the `grab` command
- Integrates with existing preset system
- Extends configuration with custom detection rules
- Respects user-specified presets (explicit overrides auto-detection)
- Adds CLI flags for controlling detection behavior

## Components and Interfaces

### PlatformPattern

Represents a URL pattern for platform detection.

```python
@dataclass
class PlatformPattern:
    """A pattern for detecting a platform from a URL."""
    platform: str
    pattern: str  # regex pattern
    preset: str
    content_type: str = ""  # e.g., "stories", "reels", "post"
    priority: int = 0  # higher priority patterns checked first
    
    def matches(self, url: str) -> bool:
        """Check if URL matches this pattern."""
        pass
    
    def __post_init__(self):
        """Compile regex pattern."""
        self._compiled = re.compile(self.pattern)
```

### DetectionResult

Represents the result of platform detection.

```python
@dataclass
class DetectionResult:
    """Result of platform detection."""
    platform: str
    preset: str
    content_type: str = ""
    confidence: float = 1.0  # 0.0 to 1.0
    matched_pattern: str = ""
    
    @property
    def is_low_confidence(self) -> bool:
        """Check if confidence is below threshold."""
        return self.confidence < 0.7
    
    def display_message(self, verbose: bool = False) -> str:
        """Generate display message for detection result."""
        pass
```

### PlatformDetector

Main detection engine.

```python
class PlatformDetector:
    """Detects platform from URLs using pattern matching."""
    
    def __init__(
        self,
        custom_patterns: list[PlatformPattern] = None,
        enabled: bool = True,
    ):
        self.custom_patterns = custom_patterns or []
        self.enabled = enabled
        self.built_in_patterns = self._load_built_in_patterns()
        
    def detect(self, url: str) -> Optional[DetectionResult]:
        """Detect platform from URL. Returns None if no match."""
        pass
    
    def _load_built_in_patterns(self) -> list[PlatformPattern]:
        """Load built-in platform patterns."""
        pass
    
    def _match_patterns(
        self,
        url: str,
        patterns: list[PlatformPattern],
    ) -> Optional[DetectionResult]:
        """Match URL against pattern list."""
        pass
    
    def _calculate_confidence(
        self,
        url: str,
        pattern: PlatformPattern,
    ) -> float:
        """Calculate confidence score for a match."""
        pass
```

### PresetResolver

Resolves which preset to apply based on detection and user input.

```python
class PresetResolver:
    """Resolves preset based on detection and user preferences."""
    
    def resolve(
        self,
        detection: Optional[DetectionResult],
        user_preset: Optional[str],
        auto_detect_enabled: bool,
    ) -> tuple[Optional[str], str]:
        """
        Resolve preset to use.
        
        Returns:
            (preset_name, source) where source is "user", "auto", or "default"
        """
        pass
```

### DetectionConfig

Configuration for platform detection.

```python
@dataclass
class DetectionConfig:
    """Configuration for platform detection."""
    enabled: bool = True
    custom_rules: list[dict] = field(default_factory=list)
    confidence_threshold: float = 0.7
    
    @classmethod
    def from_config_dict(cls, config: dict) -> DetectionConfig:
        """Load from configuration dictionary."""
        pass
    
    def load_custom_patterns(self) -> list[PlatformPattern]:
        """Parse custom rules into PlatformPattern objects."""
        pass
```

## Data Models

### Built-in Platform Patterns

The system includes these built-in patterns (in priority order):

**Instagram Content-Specific:**
- Stories: `instagram\.com/stories/` → preset: `instagram-stories`
- Reels: `instagram\.com/reels/` → preset: `instagram-reels`
- Posts: `instagram\.com/p/` → preset: `instagram-post`

**Instagram General:**
- `instagram\.com` → preset: `instagram`
- `instagr\.am` → preset: `instagram`

**Other Platforms:**
- Twitter: `(twitter\.com|x\.com)` → preset: `twitter`
- Reddit: `reddit\.com` → preset: `reddit`
- Tumblr: `tumblr\.com` → preset: `tumblr`
- TikTok: `tiktok\.com` → preset: `tiktok`

### Custom Detection Rules Format

Custom rules in configuration file:

```yaml
platform_detection:
  enabled: true
  confidence_threshold: 0.7
  custom_rules:
    - platform: "YouTube"
      pattern: "youtube\\.com|youtu\\.be"
      preset: "youtube"
      priority: 10
    - platform: "Vimeo"
      pattern: "vimeo\\.com"
      preset: "vimeo"
      content_type: ""
```

### Confidence Scoring

Confidence is calculated based on:
- Pattern specificity (more specific = higher confidence)
- URL structure completeness
- Presence of expected path components

Scoring rules:
- Content-specific patterns (e.g., /stories/): 1.0
- Domain-only patterns: 0.9
- Partial matches: 0.6-0.8
- Ambiguous matches: < 0.7 (triggers warning)

## Error Handling

### Error Categories

1. **Invalid Custom Rules**: Malformed regex patterns or missing required fields
2. **Detection Failures**: No platform matches URL
3. **Low Confidence**: Platform detected but with low certainty
4. **Preset Not Found**: Detected preset doesn't exist in configuration
5. **Configuration Errors**: Invalid detection configuration

### Error Handling Strategy

- **Invalid Custom Rules**: Log warning with rule details, skip rule, continue with remaining rules
- **Detection Failures**: Return None, proceed with default settings, optionally display "no platform detected" message
- **Low Confidence**: Proceed with detection but display warning to user
- **Preset Not Found**: Log error, fall back to default settings
- **Configuration Errors**: Log warning, disable auto-detection, use defaults

### Error Reporting

Detection errors include:
- Rule validation errors (line number if from file)
- Pattern matching failures
- Confidence warnings
- Preset resolution failures

All errors are logged with context (URL, pattern, preset name).

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Platform domain detection

*For any* URL containing a known platform domain (instagram.com, instagr.am, twitter.com, x.com, reddit.com, tumblr.com, or tiktok.com), the detection result should identify the corresponding platform.
**Validates: Requirements 1.1, 1.3, 2.1, 2.2, 2.3, 2.4**

### Property 2: Detected platform applies corresponding preset

*For any* URL where a platform is detected, the applied preset should match the preset associated with that platform.
**Validates: Requirements 1.2, 2.5**

### Property 3: Auto-preset display

*For any* URL where an auto-preset is applied, the output message should contain the name of the applied preset.
**Validates: Requirements 1.4, 4.2**

### Property 4: User preset precedence

*For any* URL with both auto-detection and an explicitly specified preset, the final applied preset should be the user-specified preset, not the auto-detected one.
**Validates: Requirements 1.5**

### Property 5: Instagram content-type detection

*For any* Instagram URL containing a content-type marker (/stories/, /reels/, or /p/), the applied preset should be the content-type specific preset (instagram-stories, instagram-reels, or instagram-post respectively).
**Validates: Requirements 3.1, 3.2, 3.3**

### Property 6: Instagram default fallback

*For any* Instagram URL without content-type markers, the applied preset should be the default instagram preset.
**Validates: Requirements 3.4**

### Property 7: Content-type display

*For any* URL where a content-specific preset is detected, the output message should contain the detected content type.
**Validates: Requirements 3.5**

### Property 8: Platform name display

*For any* URL where platform detection succeeds, the output message should contain the detected platform name.
**Validates: Requirements 4.1**

### Property 9: Verbose pattern display

*For any* URL processed with the verbose flag enabled, the output should contain information about which URL pattern was matched.
**Validates: Requirements 4.4**

### Property 10: Low confidence warning

*For any* detection result with confidence below the threshold (< 0.7), the output should contain a warning message.
**Validates: Requirements 4.5**

### Property 11: No-auto-detect disables preset application

*For any* URL processed with the no-auto-detect flag, no auto-preset should be applied regardless of URL pattern.
**Validates: Requirements 5.1, 5.2**

### Property 12: Default settings with disabled detection

*For any* URL with auto-detection disabled and no explicit preset, the applied settings should match the system defaults.
**Validates: Requirements 5.3**

### Property 13: Configuration-level detection disable

*For any* configuration with auto-detection disabled, all URL processing should skip platform detection.
**Validates: Requirements 5.4**

### Property 14: Detection skipped message

*For any* URL processed with auto-detection disabled, the output should indicate that detection was skipped.
**Validates: Requirements 5.5**

### Property 15: Custom rule loading

*For any* valid custom detection rule in the configuration, the loaded pattern list should include that custom rule.
**Validates: Requirements 6.1**

### Property 16: Custom rule precedence

*For any* URL that matches both a custom rule and a built-in rule, the detection result should use the custom rule's preset.
**Validates: Requirements 6.2**

### Property 17: Custom rule preset application

*For any* URL matching a custom detection rule, the applied preset should be the preset specified in that custom rule.
**Validates: Requirements 6.3**

### Property 18: Regex pattern matching

*For any* custom rule with a regex pattern, URL matching should follow regex semantics (e.g., character classes, quantifiers, anchors).
**Validates: Requirements 6.4**

### Property 19: Invalid rule handling

*For any* invalid custom rule (malformed regex or missing fields), the system should display a warning and the rule should not appear in the loaded pattern list.
**Validates: Requirements 6.5**

## Testing Strategy

### Property-Based Testing

We will use **Hypothesis** (Python's property-based testing library) to implement the correctness properties. Each property will be implemented as a separate test with appropriate generators.

**Configuration:**
- Minimum 100 iterations per property test
- Each test tagged with format: `**Feature: smart-platform-detection, Property N: [property text]**`
- Tests reference the specific correctness property from this design document

**Key Generators:**
1. **URL Generator**: Generates URLs with various platform domains and path structures
2. **Instagram URL Generator**: Generates Instagram URLs with different content types
3. **Custom Rule Generator**: Generates valid and invalid custom detection rules
4. **Config Generator**: Generates detection configurations with various settings

**Property Test Examples:**

1. **Property 1 (Platform domain detection)**: Generate URLs with known platform domains embedded in various positions, verify all are detected correctly

2. **Property 4 (User preset precedence)**: Generate URLs with platform patterns, add explicit presets, verify explicit preset is always used

3. **Property 5 (Content-type detection)**: Generate Instagram URLs with /stories/, /reels/, /p/ paths, verify correct content-specific presets

4. **Property 16 (Custom rule precedence)**: Generate URLs, create custom rules that overlap with built-in rules, verify custom rules win

### Unit Tests

Unit tests complement property tests by verifying specific examples and edge cases:

1. **Pattern Matching**:
   - Test exact domain matches (instagram.com, twitter.com, etc.)
   - Test subdomain handling (www.instagram.com, mobile.twitter.com)
   - Test protocol variations (http://, https://, no protocol)
   - Test query parameters and fragments

2. **Confidence Scoring**:
   - Test content-specific patterns score 1.0
   - Test domain-only patterns score 0.9
   - Test ambiguous patterns score < 0.7

3. **Preset Resolution**:
   - Test user preset overrides auto-detection
   - Test auto-detection with no user preset
   - Test disabled detection returns None
   - Test fallback to defaults

4. **Custom Rules**:
   - Test valid custom rule loading
   - Test invalid regex handling
   - Test missing field handling
   - Test priority ordering

5. **Display Messages**:
   - Test detection success message format
   - Test no detection message
   - Test low confidence warning format
   - Test verbose output includes pattern

6. **Edge Cases**:
   - Empty URL
   - Malformed URL
   - URL with no domain
   - Multiple platform domains in one URL (should match first/highest priority)

### Integration Tests

1. **End-to-end detection flow**: Provide URL, verify detection runs, preset applied, message displayed
2. **CLI flag integration**: Test --no-auto-detect flag disables detection
3. **Configuration integration**: Test detection config loaded from file, custom rules applied
4. **Preset system integration**: Verify detected presets merge correctly with other config sources
5. **Error resilience**: Test system continues with defaults when detection fails

### Manual Testing

1. Test with real URLs from Instagram, Twitter, Reddit, TikTok, Tumblr
2. Test Instagram stories, reels, and post URLs
3. Test verbose output with various URLs
4. Test custom rules with personal platform patterns
5. Test configuration file with various detection settings
6. Verify warning messages display correctly for low confidence
7. Test --no-auto-detect flag behavior

