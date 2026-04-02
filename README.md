# Self-Editing AI Agent

A sophisticated self-editing AI agent that can modify its own codebase, track all changes, and restart itself seamlessly.

---

> **Built by an agent, for agents.** This entire framework was created autonomously by another self-editing agent.

## Features

### Core Capabilities

- **Self-Editing**: Modify any file in the codebase with full audit trail
- **State Persistence**: Complete state serialization and deserialization
- **Version Control**: Git integration for tracking all self-edits
- **Configuration Management**: YAML/JSON config editing with validation
- **Code Editing**: Python AST-based editing for safe code modifications
- **Restart Mechanism**: Graceful restart with state preservation

### Architecture

```
agent-built-agent/
├── src/
│   ├── core/
│   │   ├── agent.py          # Main SelfEditingAgent class
│   │   ├── state.py          # State management and persistence
│   │   └── config.py         # Configuration management
│   ├── editors/
│   │   ├── code_editor.py    # Base code editor
│   │   ├── python_editor.py  # Python-specific editor
│   │   └── config_editor.py  # Config file editor
│   ├── version_control/
│   │   ├── git_manager.py    # Git operations
│   │   └── edit_tracker.py   # Edit tracking
│   └── cli.py                # Command-line interface
├── tests/
│   ├── test_state.py         # State tests
│   ├── test_config.py        # Config tests
│   ├── test_editors.py       # Editor tests
│   └── test_version_control.py # VCS tests
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd agent-built-agent

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Usage

### Command-Line Interface

```bash
# Start the agent
agent start --name "MyAgent" --config agent_config.yaml

# Check status
agent status

# View edit history
agent history

# Perform a restart
agent restart
```

### Programmatic Usage

```python
from src.core.agent import SelfEditingAgent
from src.core.config import ConfigManager

# Create agent
agent = SelfEditingAgent(
    name="MyAgent",
    config_path="agent_config.yaml"
)

# Edit a file
agent.edit_file(
    file_path="src/core/agent.py",
    new_content="# Modified content",
    reason="Updated agent logic"
)

# Get status
status = agent.get_status()
print(f"Total edits: {status['total_edits']}")

# Restart
agent.restart("Scheduled restart")
```

### Advanced Editing

```python
from src.editors.python_editor import PythonEditor

# Python-specific editing
editor = PythonEditor("src/core/agent.py")
editor.load()

# Add an import
editor.add_import("os")

# Add a function
editor.add_function(
    func_name="new_method",
    parameters=["self", "arg1"],
    body_lines=['"""New method"""', 'print(arg1)']
)

# Save changes
editor.save()
```

### Configuration

Create `agent_config.yaml`:

```yaml
name: SelfEditingAgent
agent_id: default
version: 0.2.0

edit_config:
  enabled: true
  dry_run: false
  backup_before_edit: true
  max_edit_size: 10000
  require_reason: true
  auto_commit: false

state_config:
  state_dir: .agent_state
  auto_save: true
  save_interval_seconds: 60
  max_history_entries: 100

logging_config:
  level: INFO
  log_to_console: true
  include_timestamps: true

max_edits_per_session: 100
enable_self_modification: true
require_confirmation_for_major_changes: true
```

## Key Components

### SelfEditingAgent

The main agent class that handles:
- File editing with audit trail
- State persistence
- Edit hooks (custom callbacks)
- Restart management

### StateManager

Handles state persistence:
- Save/load agent state to disk
- Edit history tracking
- State integrity verification

### GitManager

Manages git operations:
- Initialize repositories
- Add/commit/push changes
- Get status and history

### EditTracker

Tracks edits and integrates with git:
- Queue edits for batch commit
- Sync with git repository
- Push to remote

## Safety Features

1. **Dry Run Mode**: Preview changes before applying
2. **Backup Creation**: Automatic backups before editing
3. **Edit Limits**: Maximum edit size enforcement
4. **Reason Requirements**: Mandatory edit reasons
5. **Rollback Support**: Restore previous states
6. **Hook System**: Custom validation before edits

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_state.py -v
```

## Development

### Adding New Editors

1. Create new editor class in `src/editors/`
2. Inherit from `CodeEditor` or `ConfigEditor`
3. Implement editing methods
4. Add tests

### Extending Functionality

1. Add hooks in `SelfEditingAgent`
2. Implement new edit operations
3. Update configuration schema
4. Add CLI commands

## License

MIT License - See LICENSE file for details

## Version History

- **0.2.0** (Current): Multi-file architecture, version control, configuration management
- **0.1.0**: Initial self-editing agent with basic functionality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues and feature requests, please use the issue tracker.
