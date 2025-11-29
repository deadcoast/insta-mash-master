# Design Document: Feature Completion Orchestration

## Overview

This design specifies how AI agents will sequentially complete the design and implementation planning for five insta-mash features. Each agent session follows a deterministic workflow: identify the current feature from a handoff document, complete its design and tasks, then create a handoff for the next agent. This approach ensures consistent, high-quality specifications across all features.

## Architecture

### Workflow

```
Start Session
    ↓
Read HANDOFF.md (or start with Feature 1)
    ↓
Read requirements.md for current feature
    ↓
Perform prework analysis
    ↓
Create design.md with correctness properties
    ↓
Request user approval
    ↓
Create tasks.md with implementation plan
    ↓
Request user approval
    ↓
Create HANDOFF.md for next feature
    ↓
End Session
```

### State Management

State is maintained through the filesystem:
- `HANDOFF.md` - Current progress and next feature
- Feature directories - Presence of design.md and tasks.md indicates completion
- Requirements documents - Already exist for all features

## Components and Interfaces

### HandoffDocument

Tracks progress and specifies next feature.

```python
@dataclass
class HandoffDocument:
    """Represents the handoff state between agent sessions."""
    completed_feature: str
    next_feature: str
    remaining_features: list[str]
    notes: str
    progress: tuple[int, int]  # (completed, total)
    
    @classmethod
    def load(cls, path: Path) -> Optional[HandoffDocument]:
        """Load handoff from file, return None if doesn't exist."""
        pass
    
    def save(self, path: Path) -> None:
        """Save handoff to file."""
        pass
    
    def get_next_feature(self) -> Optional[str]:
        """Get the next feature to work on, None if all complete."""
        pass
```

### FeatureSpec

Represents a complete feature specification.

```python
@dataclass
class FeatureSpec:
    """A complete feature specification."""
    name: str
    requirements_path: Path
    design_path: Path
    tasks_path: Path
    
    def has_requirements(self) -> bool:
        """Check if requirements.md exists."""
        pass
    
    def has_design(self) -> bool:
        """Check if design.md exists."""
        pass
    
    def has_tasks(self) -> bool:
        """Check if tasks.md exists."""
        pass
    
    def is_complete(self) -> bool:
        """Check if all three documents exist."""
        pass
```

### OrchestrationAgent

Manages the workflow for a single agent session.

```python
class OrchestrationAgent:
    """Manages feature completion workflow."""
    
    FEATURE_SEQUENCE = [
        "progress-display",
        "resume-support", 
        "smart-platform-detection",
        "shell-completions",
        "post-download-hooks"
    ]
    
    def __init__(self):
        self.handoff_path = Path(".kiro/specs/feature-completion-orchestration/HANDOFF.md")
        self.specs_dir = Path(".kiro/specs")
        
    def get_current_feature(self) -> Optional[str]:
        """Determine which feature to work on."""
        handoff = HandoffDocument.load(self.handoff_path)
        if handoff:
            return handoff.next_feature
        return self.FEATURE_SEQUENCE[0]
    
    def complete_feature(self, feature_name: str) -> None:
        """Complete design and tasks for a feature."""
        # 1. Read requirements
        # 2. Perform prework
        # 3. Create design with properties
        # 4. Get user approval
        # 5. Create tasks
        # 6. Get user approval
        pass
    
    def create_handoff(self, completed_feature: str) -> None:
        """Create handoff document for next agent."""
        pass
    
    def is_orchestration_complete(self) -> bool:
        """Check if all features are complete."""
        pass
```

## Data Models

### Feature Sequence

Features are completed in this fixed order:

1. `progress-display` - Progress bars, ETA, throughput
2. `resume-support` - Interrupt handling, resume from checkpoint
3. `smart-platform-detection` - Auto-detect platform, apply presets
4. `shell-completions` - Tab completion for bash/zsh/fish
5. `post-download-hooks` - Execute scripts after downloads

### Handoff Document Structure

```markdown
# Feature Completion Handoff

## Completed Feature
[feature-name]

## Status Summary
- Requirements: ✅ Complete
- Design: ✅ Complete
- Tasks: ✅ Complete

## Next Feature
[next-feature-name]

Location: `.kiro/specs/[next-feature-name]/`

## Remaining Features
- [ ] Feature 2
- [ ] Feature 3
...

## Notes for Next Agent
- Any important decisions or context
- Patterns established that should be followed
- Issues encountered and how they were resolved

## Progress
Completed: X of 5 features
Remaining: Y of 5 features
```

### Directory Structure

```
.kiro/specs/
├── feature-completion-orchestration/
│   ├── requirements.md (this spec)
│   ├── design.md (this document)
│   ├── tasks.md (workflow steps)
│   └── HANDOFF.md (current state)
├── progress-display/
│   ├── requirements.md ✅
│   ├── design.md (to be created)
│   └── tasks.md (to be created)
├── resume-support/
│   ├── requirements.md ✅
│   ├── design.md (to be created)
│   └── tasks.md (to be created)
├── smart-platform-detection/
│   ├── requirements.md ✅
│   ├── design.md (to be created)
│   └── tasks.md (to be created)
├── shell-completions/
│   ├── requirements.md ✅
│   ├── design.md (to be created)
│   └── tasks.md (to be created)
└── post-download-hooks/
    ├── requirements.md ✅
    ├── design.md (to be created)
    └── tasks.md (to be created)
```

## Agent Workflow

### Session Start

1. Check if `HANDOFF.md` exists
2. If exists: read next feature from handoff
3. If not exists: start with first feature (progress-display)
4. Display which feature will be worked on

### Design Phase

1. Read `requirements.md` for current feature
2. Use `prework` tool to analyze acceptance criteria
3. Generate correctness properties based on prework
4. Create `design.md` with all required sections:
   - Overview
   - Architecture
   - Components and Interfaces
   - Data Models
   - Correctness Properties (with prework-based properties)
   - Error Handling
   - Testing Strategy
5. Use `userInput` tool with reason `spec-design-review` to get approval

### Tasks Phase

1. Generate implementation task list from design
2. Create property-based test tasks for each correctness property
3. Mark test tasks as optional (with `*` suffix)
4. Create `tasks.md` with structured task list
5. Use `userInput` tool with reason `spec-tasks-review` to get approval
6. If user wants comprehensive testing, remove `*` markers

### Handoff Phase

1. Determine next feature from sequence
2. Create `HANDOFF.md` with:
   - Completed feature name
   - Next feature name
   - Remaining features checklist
   - Progress counter
   - Notes for next agent
3. Display completion message

### Final Session

When all 5 features are complete:
1. Create `COMPLETION_SUMMARY.md` instead of handoff
2. List all completed features with links
3. Provide statistics (total properties, total tasks, etc.)
4. Suggest next steps for implementation

## Error Handling

### Missing Requirements

If requirements.md doesn't exist for current feature:
- Display error message
- List available features with requirements
- Abort session

### Corrupted Handoff

If HANDOFF.md is malformed:
- Display warning
- Attempt to determine progress from filesystem
- Fall back to first incomplete feature

### User Rejection

If user rejects design or tasks:
- Iterate on the document
- Request approval again
- Do not proceed until approved

## Testing Strategy

This is a meta-specification that guides agent behavior rather than code implementation. Testing occurs through:

1. **Manual Verification**: Each agent session produces visible artifacts (design.md, tasks.md, HANDOFF.md)
2. **User Review**: User approves each design and tasks document
3. **Filesystem Validation**: Presence of files indicates completion
4. **Handoff Continuity**: Each handoff correctly identifies next feature

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Feature sequence preservation

*For any* agent session, the next feature specified in the handoff should be the next feature in the predefined sequence after the completed feature.
**Validates: Requirements 1.1, 4.1**

### Property 2: Document completeness

*For any* feature marked as complete, all three documents (requirements.md, design.md, tasks.md) should exist in the feature directory.
**Validates: Requirements 5.5**

### Property 3: Handoff continuity

*For any* handoff document, the next feature should not have a design.md file yet.
**Validates: Requirements 1.3**

### Property 4: Progress accuracy

*For any* handoff document showing N completed features, exactly N feature directories should have all three documents.
**Validates: Requirements 4.2, 4.3**

### Property 5: Workflow consistency

*For any* two features completed by the orchestration, both should have design documents with the same section structure.
**Validates: Requirements 5.2**

### Property 6: Property coverage

*For any* completed feature, the number of correctness properties in design.md should be at least equal to the number of testable acceptance criteria.
**Validates: Requirements 2.3**

### Property 7: Task-property correspondence

*For any* correctness property in a design document, there should be a corresponding property-based test task in tasks.md.
**Validates: Requirements 3.2**

### Property 8: Completion detection

*For any* orchestration state where all 5 features have complete specifications, the system should indicate orchestration is finished.
**Validates: Requirements 1.4**
