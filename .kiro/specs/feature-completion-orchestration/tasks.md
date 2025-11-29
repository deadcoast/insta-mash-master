# Implementation Plan: Feature Completion Orchestration

## Overview

This task list guides each agent session through completing one feature specification. The agent should execute these tasks in order, then the next agent will start fresh with the same task list for the next feature.

## Tasks for Each Agent Session

- [ ] 1. Identify current feature
  - Read `.kiro/specs/feature-completion-orchestration/HANDOFF.md` if it exists
  - If no handoff exists, start with `progress-display`
  - If handoff exists, use the "Next Feature" specified
  - Display which feature will be worked on
  - _Requirements: 1.1, 1.2, 1.3, 1.5_

- [ ] 2. Verify feature requirements exist
  - Check that `.kiro/specs/[feature-name]/requirements.md` exists
  - If missing, display error and abort
  - Read the requirements document to understand the feature
  - _Requirements: 2.1_

- [ ] 3. Perform prework analysis
  - Use the `prework` tool with feature name
  - Analyze each acceptance criterion for testability
  - Classify as: property, example, edge-case, or not testable
  - Store analysis for use in correctness properties
  - _Requirements: 2.2_

- [ ] 4. Create design document
  - Create `.kiro/specs/[feature-name]/design.md`
  - Include sections: Overview, Architecture, Components and Interfaces, Data Models
  - Stop before Correctness Properties section
  - Complete prework analysis
  - Continue with Correctness Properties section using prework
  - Include sections: Error Handling, Testing Strategy
  - Ensure all testable criteria have corresponding properties
  - _Requirements: 2.3, 2.4, 5.2_

- [ ] 5. Request design approval
  - Use `userInput` tool with reason `spec-design-review`
  - Ask: "Does the design look good? If so, we can move on to the implementation plan."
  - If user requests changes, iterate on design
  - Do not proceed until user approves
  - _Requirements: 2.5_

- [ ] 6. Create tasks document
  - Create `.kiro/specs/[feature-name]/tasks.md`
  - Generate implementation tasks from design
  - Create property-based test tasks for each correctness property
  - Mark test tasks as optional with `*` suffix
  - Follow consistent format across all features
  - _Requirements: 3.1, 3.2, 3.3, 5.3_

- [ ] 7. Request tasks approval
  - Use `userInput` tool with reason `spec-tasks-review`
  - Ask about optional tasks: "The current task list marks some tasks (e.g. tests, documentation) as optional to focus on core features first."
  - Provide options: "Keep optional tasks (faster MVP)" or "Make all tasks required (comprehensive from start)"
  - If user wants comprehensive, remove `*` markers from test tasks
  - Do not proceed until user approves
  - _Requirements: 3.4, 3.5_

- [ ] 8. Verify feature completion
  - Confirm all three files exist:
    - `.kiro/specs/[feature-name]/requirements.md` ✅
    - `.kiro/specs/[feature-name]/design.md` ✅
    - `.kiro/specs/[feature-name]/tasks.md` ✅
  - _Requirements: 5.5_

- [ ] 9. Determine next feature
  - Identify current feature's position in sequence
  - Determine next feature from sequence:
    1. progress-display
    2. resume-support
    3. smart-platform-detection
    4. shell-completions
    5. post-download-hooks
  - If current is last feature, mark orchestration as complete
  - _Requirements: 4.1_

- [ ] 10. Create handoff document
  - Create or update `.kiro/specs/feature-completion-orchestration/HANDOFF.md`
  - Include completed feature name
  - Include next feature name (or "ALL COMPLETE")
  - List remaining features with checkboxes
  - Add any notes for next agent
  - Show progress: "Completed: X of 5 features"
  - _Requirements: 4.2, 4.3, 4.4, 4.5_

- [ ] 11. Display completion message
  - Show which feature was completed
  - Show which feature is next (or that all are complete)
  - Provide brief summary of what was accomplished
  - If all complete, congratulate and suggest next steps

## Feature Sequence Reference

Complete features in this order:

1. **progress-display** - Real-time download progress with ETA and throughput
2. **resume-support** - Graceful interrupt handling with automatic resume  
3. **smart-platform-detection** - Auto-detect platform from URL and apply preset
4. **shell-completions** - Bash, zsh, fish autocompletions
5. **post-download-hooks** - Run scripts after downloads complete

## Notes for Agents

- Each agent session completes ONE feature
- Follow the same workflow for consistency
- Use the prework tool before writing correctness properties
- Always request user approval for design and tasks
- Create a clear handoff for the next agent
- If you're working on the 5th feature, create a completion summary instead of a handoff

## Handoff Template

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
- [x] progress-display (if complete)
- [ ] resume-support (if not complete)
- [ ] smart-platform-detection
- [ ] shell-completions
- [ ] post-download-hooks

## Notes for Next Agent
[Any important context, patterns, or decisions]

## Progress
Completed: X of 5 features
Remaining: Y of 5 features
```
