# Agent Instructions: Feature Completion Orchestration

## Overview

This orchestration system guides multiple AI agent sessions to complete design and implementation planning for 5 insta-mash features. Each agent completes ONE feature, then hands off to the next agent.

## Quick Start for Agents

1. **Read the handoff**: Open `.kiro/specs/feature-completion-orchestration/HANDOFF.md`
2. **Identify your feature**: The "Next Feature" section tells you which feature to work on
3. **Follow the workflow**: Execute tasks from `.kiro/specs/feature-completion-orchestration/tasks.md`
4. **Create handoff**: When done, update HANDOFF.md for the next agent

## Feature Sequence

Features are completed in this order:

1. ✅ **batch-mode** - COMPLETE (requirements, design, tasks)
2. ⏭️ **progress-display** - NEXT (requirements exist, need design & tasks)
3. ⏸️ **resume-support** - PENDING (requirements exist)
4. ⏸️ **smart-platform-detection** - PENDING (requirements exist)
5. ⏸️ **shell-completions** - PENDING (requirements exist)
6. ⏸️ **post-download-hooks** - PENDING (requirements exist)

## Workflow for Each Agent

### Step 1: Read Handoff
```bash
# Location: .kiro/specs/feature-completion-orchestration/HANDOFF.md
# This tells you which feature to work on
```

### Step 2: Read Requirements
```bash
# Location: .kiro/specs/[feature-name]/requirements.md
# Understand the feature's user stories and acceptance criteria
```

### Step 3: Perform Prework
```python
# Use the prework tool to analyze acceptance criteria
prework(
    featureName="[feature-name]",
    preworkAnalysis="[your analysis]"
)
```

### Step 4: Create Design
```bash
# Location: .kiro/specs/[feature-name]/design.md
# Include: Overview, Architecture, Components, Data Models,
#          Correctness Properties, Error Handling, Testing Strategy
```

### Step 5: Get Design Approval
```python
userInput(
    question="Does the design look good? If so, we can move on to the implementation plan.",
    reason="spec-design-review"
)
```

### Step 6: Create Tasks
```bash
# Location: .kiro/specs/[feature-name]/tasks.md
# Generate implementation tasks with property-based test tasks
```

### Step 7: Get Tasks Approval
```python
userInput(
    question="The current task list marks some tasks (e.g. tests, documentation) as optional...",
    options=["Keep optional tasks (faster MVP)", "Make all tasks required (comprehensive from start)"],
    reason="spec-tasks-review"
)
```

### Step 8: Create Handoff
```bash
# Update: .kiro/specs/feature-completion-orchestration/HANDOFF.md
# Specify next feature and provide context for next agent
```

## Key Principles

### 1. Consistency
- Follow the same structure for all features
- Use EARS format for requirements (already done)
- Include all required design sections
- Format tasks the same way

### 2. Correctness Properties
- Use prework tool BEFORE writing properties
- Base properties on prework analysis
- Every testable criterion should have a property
- Properties start with "For any" (universal quantification)

### 3. User Approval
- Always get approval for design
- Always get approval for tasks
- Use correct reason codes
- Iterate if user requests changes

### 4. Handoff Quality
- Clearly state what was completed
- Clearly state what's next
- Provide helpful context
- Update progress counters

## File Locations

```
.kiro/specs/
├── feature-completion-orchestration/
│   ├── requirements.md          # This orchestration spec
│   ├── design.md                # Orchestration design
│   ├── tasks.md                 # Workflow steps
│   ├── HANDOFF.md              # Current state (READ THIS FIRST!)
│   └── AGENT_INSTRUCTIONS.md   # This file
│
├── batch-mode/                  # ✅ COMPLETE
│   ├── requirements.md
│   ├── design.md
│   └── tasks.md
│
├── progress-display/            # ⏭️ NEXT
│   └── requirements.md
│
├── resume-support/              # ⏸️ PENDING
│   └── requirements.md
│
├── smart-platform-detection/    # ⏸️ PENDING
│   └── requirements.md
│
├── shell-completions/           # ⏸️ PENDING
│   └── requirements.md
│
└── post-download-hooks/         # ⏸️ PENDING
    └── requirements.md
```

## Example Handoff Update

When you complete a feature, update HANDOFF.md like this:

```markdown
# Feature Completion Handoff

## Completed Feature
progress-display

## Status Summary
- Requirements: ✅ Complete
- Design: ✅ Complete
- Tasks: ✅ Complete

## Next Feature
resume-support

Location: `.kiro/specs/resume-support/`

## Remaining Features
- [x] batch-mode
- [x] progress-display
- [ ] resume-support
- [ ] smart-platform-detection
- [ ] shell-completions
- [ ] post-download-hooks

## Notes for Next Agent
[Your notes here]

## Progress
Completed: 2 of 6 features
Remaining: 4 of 6 features
```

## Completion

When the last feature (post-download-hooks) is complete:
1. Create `COMPLETION_SUMMARY.md` instead of updating HANDOFF.md
2. List all completed features
3. Provide statistics (total properties, total tasks)
4. Suggest next steps for implementation

## Questions?

If you're an agent reading this:
- Your current task is specified in HANDOFF.md
- Follow the workflow in tasks.md
- Maintain consistency with batch-mode (the reference implementation)
- Create a clear handoff for the next agent

Good luck! 🚀
