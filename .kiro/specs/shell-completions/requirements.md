# Requirements Document

## Introduction

This document specifies the requirements for shell completion functionality in insta-mash. Shell completions provide tab-completion for commands, options, and arguments in bash, zsh, and fish shells, improving user experience and reducing typing errors. This feature makes the CLI more discoverable and efficient to use.

## Glossary

- **Shell Completion**: Auto-completion suggestions provided by the shell when the user presses the tab key
- **System**: The insta-mash application
- **Completion Script**: A shell-specific script that provides completion logic
- **Completion Context**: The current command-line state when completion is requested
- **Completion Candidate**: A suggested value that could complete the current input
- **Shell**: The command-line interpreter (bash, zsh, or fish)

## Requirements

### Requirement 1

**User Story:** As a user, I want to generate completion scripts for my shell, so that I can enable tab-completion for insta-mash commands.

#### Acceptance Criteria

1. WHEN a user invokes the completions command with bash specified, THE System SHALL output a bash completion script
2. WHEN a user invokes the completions command with zsh specified, THE System SHALL output a zsh completion script
3. WHEN a user invokes the completions command with fish specified, THE System SHALL output a fish completion script
4. WHEN a user invokes the completions command without specifying a shell, THE System SHALL detect the current shell and output the appropriate script
5. WHEN the System cannot detect the shell, THE System SHALL display an error message listing supported shells

### Requirement 2

**User Story:** As a user, I want command completion, so that I can discover and quickly type insta-mash commands.

#### Acceptance Criteria

1. WHEN a user types mash and presses tab, THE System SHALL suggest all available commands
2. WHEN a user types mash g and presses tab, THE System SHALL suggest grab as a completion
3. WHEN a user types mash config and presses tab, THE System SHALL suggest all config subcommands
4. WHEN a user types mash b and presses tab, THE System SHALL suggest batch as a completion
5. WHEN a user completes a command name, THE System SHALL suggest available options for that command

### Requirement 3

**User Story:** As a user, I want option completion, so that I can quickly specify flags without memorizing them.

#### Acceptance Criteria

1. WHEN a user types mash grab -- and presses tab, THE System SHALL suggest all long-form options
2. WHEN a user types mash grab - and presses tab, THE System SHALL suggest all short-form options
3. WHEN a user types mash grab --d and presses tab, THE System SHALL suggest --destination and --dry-run
4. WHEN a user completes an option that requires a value, THE System SHALL suggest appropriate values
5. WHEN a user types an option that takes no value, THE System SHALL move to the next completion context

### Requirement 4

**User Story:** As a user, I want intelligent value completion, so that I can quickly select from valid option values.

#### Acceptance Criteria

1. WHEN a user types mash grab --profile and presses tab, THE System SHALL suggest all saved profile names
2. WHEN a user types mash preset and presses tab, THE System SHALL suggest all available preset names
3. WHEN a user types mash grab --cookies and presses tab, THE System SHALL suggest all supported browser names
4. WHEN a user types mash config set and presses tab, THE System SHALL suggest all valid configuration keys
5. WHEN a user types mash batch run and presses tab, THE System SHALL suggest file paths

### Requirement 5

**User Story:** As a user, I want file path completion, so that I can quickly specify files and directories.

#### Acceptance Criteria

1. WHEN a user types mash grab --destination and presses tab, THE System SHALL suggest directory paths
2. WHEN a user types mash batch run and presses tab, THE System SHALL suggest file paths
3. WHEN a user types mash grab --archive and presses tab, THE System SHALL suggest file paths
4. WHEN a user types a partial path and presses tab, THE System SHALL complete the path
5. WHEN a user completes a directory path, THE System SHALL append a trailing slash

### Requirement 6

**User Story:** As a user, I want completion to work with subcommands, so that I can efficiently navigate nested command structures.

#### Acceptance Criteria

1. WHEN a user types mash config and presses tab, THE System SHALL suggest config subcommands
2. WHEN a user types mash config s and presses tab, THE System SHALL suggest show, set, and save-profile
3. WHEN a user types mash batch and presses tab, THE System SHALL suggest batch subcommands
4. WHEN a user completes a subcommand, THE System SHALL suggest options for that subcommand
5. WHEN a user types mash config set and presses tab, THE System SHALL suggest configuration keys
