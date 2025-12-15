# Task Scheduler

A centralized YAML-configured task scheduler for macOS periodic tasks. Each task runs in its own isolated environment with standardized `run.sh` interface.

## Architecture

```
sync-calendars/
├── config.yaml              # Central configuration for all tasks
├── Makefile                 # Installation and service management
├── scheduler/               # Scheduling daemon (APScheduler)
│   ├── scheduler.py
│   ├── requirements.txt
│   ├── Makefile
│   └── .venv/
└── tasks/                   # Your periodic tasks
    └── calendar-sync/       # Example task
        ├── run.sh          # Standard entry point
        ├── Makefile
        ├── requirements.txt
        └── .venv/
```

**Key Design Principles:**
- **Decoupled**: Scheduler only knows about `run.sh` + args, nothing about task internals
- **Isolated**: Each task has its own environment (Python venv, Go modules, etc.)
- **Simple**: Single YAML config instead of multiple plist files
- **Polyglot**: Tasks can be written in any language (Python, Go, Bash, etc.)

## Quick Start

### 1. Install

```bash
make install
```

This installs:
- Scheduler daemon and dependencies
- All tasks and their dependencies

### 2. Configure

Edit `config.yaml` to configure your tasks:

```yaml
scheduler:
  log_file: ~/Library/Logs/scheduler.log
  default_timeout: 300

tasks:
  - name: calendar-sync
    path: tasks/calendar-sync
    cron: "*/30 * * * *"  # Every 30 minutes
    args:
      - "--days"
      - "30"
    timeout: 600
    enabled: true
```

### 3. Start the Service

```bash
make install-service  # Generate launchd plist
make service-start    # Start the scheduler daemon
```

### 4. Monitor

```bash
make service-status   # Check if running
make service-logs     # View execution logs
```

## Available Commands

```bash
# Installation
make install              # Install scheduler + all tasks
make install-service      # Generate and install launchd service

# Service Management
make service-start        # Start the scheduler daemon
make service-stop         # Stop the scheduler daemon
make service-restart      # Restart the scheduler daemon
make service-status       # Show scheduler status
make service-logs         # Show scheduler logs
make uninstall-service    # Uninstall the scheduler service

# Testing
make test-scheduler       # Test scheduler locally (no service)

# Cleanup
make clean                # Clean cache files
make clean-venv           # Remove all virtual environments
make clean-all            # Deep clean

# Help
make help                 # Show all available commands
```

## Configuration

### config.yaml Format

```yaml
# Global scheduler settings
scheduler:
  log_file: ~/Library/Logs/scheduler.log
  default_timeout: 300  # Default timeout in seconds

# Task definitions
tasks:
  - name: task-name            # Unique identifier (used in logs)
    path: tasks/task-name      # Path to task directory (relative to repo root)
    cron: "*/30 * * * *"       # Standard 5-field cron expression
    args:                      # Arguments passed to run.sh
      - "--arg1"
      - "value1"
    timeout: 600               # Max execution time (seconds, optional)
    enabled: true              # Enable/disable without deleting config
```

### Cron Expression Format

Standard 5-field cron syntax:

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday=0)
│ │ │ │ │
* * * * *
```

**Examples:**
- `*/30 * * * *` - Every 30 minutes
- `0 2 * * *` - Daily at 2 AM
- `0 9-17 * * 1-5` - Every hour from 9 AM to 5 PM, Monday to Friday
- `0 0 1 * *` - First day of every month at midnight

## Available Tasks

### 📅 Calendar Sync

Synchronizes calendar events between calendars with filtering options.

**Configuration:**
```yaml
- name: calendar-sync
  path: tasks/calendar-sync
  cron: "*/30 * * * *"
  args:
    - "--source-calendar"
    - "work@example.com"
    - "--days"
    - "30"
    - "--exclude-declined-events"
    - "--exclude-all-day-events"
    - "--do-sync"
    - "Personal"
  timeout: 600
  enabled: true
```

See [tasks/calendar-sync/README.md](tasks/calendar-sync/README.md) for full documentation.

## Adding New Tasks

Each task must provide:

### 1. Directory Structure

```
tasks/my-task/
├── run.sh           # Executable entry point (required)
├── Makefile         # With install, clean, help targets (required)
├── README.md        # Documentation (recommended)
└── [task files]     # Your actual implementation
```

### 2. run.sh Template

```bash
#!/bin/bash
set -e  # Exit on error

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate environment if needed
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Run your task with arguments
python "$SCRIPT_DIR/main.py" "$@"
# OR: go run . "$@"
# OR: ./my-binary "$@"
```

Make it executable:
```bash
chmod +x tasks/my-task/run.sh
```

### 3. Makefile Template

```makefile
.PHONY: install clean help

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

help:
	@echo "My Task - Available targets:"
	@echo "  make install  - Install dependencies"
	@echo "  make clean    - Clean cache files"
```

### 4. Add to config.yaml

```yaml
tasks:
  - name: my-task
    path: tasks/my-task
    cron: "0 * * * *"
    args: []
    enabled: true
```

### 5. Update Root Makefile

Add your task to the `TASKS` variable:

```makefile
TASKS := calendar-sync my-task
```

### 6. Install and Test

```bash
make install          # Install new task dependencies
make test-scheduler   # Test locally
make service-restart  # Reload service with new config
```

## Task Contract

Tasks communicate with the scheduler via:

### Input
- **Arguments**: Passed from `config.yaml` args list to `run.sh`
- **Working Directory**: Scheduler runs `run.sh` from the task directory

### Output
- **Exit Code**:
  - `0` = Success
  - Non-zero = Failure (logged as error)
- **stdout**: Logged with `[task-name] STDOUT:` prefix
- **stderr**: Logged with `[task-name] STDERR:` prefix (warnings/errors)

### Timeout
- If task exceeds `timeout`, scheduler kills the process
- Logged as error with timeout duration

## Logging

All task executions are logged to `~/Library/Logs/scheduler.log`:

```
[2025-12-12 10:00:00] INFO: Scheduler started, loaded 1 tasks
[2025-12-12 10:00:00] INFO: Registered task 'calendar-sync' with cron '*/30 * * * *'
[2025-12-12 10:30:00] INFO: Executing 'calendar-sync' with args ['--days', '30', ...]
[2025-12-12 10:30:15] INFO: Task 'calendar-sync' completed in 15.2s (exit code: 0)
[2025-12-12 10:30:15] [calendar-sync] STDOUT: Fetching events from 2025-12-12 to 2026-01-11...
[2025-12-12 10:30:15] [calendar-sync] STDOUT: Sync complete: Created: 3, Updated: 1, Deleted: 0
```

View logs:
```bash
make service-logs
# OR
tail -f ~/Library/Logs/scheduler.log
```

## Troubleshooting

### Scheduler not running
```bash
make service-status   # Check if service is loaded
make service-logs     # Check for errors
```

### Task failing
1. Check logs: `make service-logs`
2. Test task manually:
   ```bash
   cd tasks/task-name
   ./run.sh [args...]
   ```
3. Check task's virtual environment is installed:
   ```bash
   cd tasks/task-name
   make install
   ```

### Config changes not applied
```bash
make service-restart  # Reload configuration
```

### Remove old service
If migrating from old setup:
```bash
# Stop old service
launchctl unload ~/Library/LaunchAgents/com.patarra.calendar-sync.plist
rm ~/Library/LaunchAgents/com.patarra.calendar-sync.plist
```

## Requirements

- **macOS**: 10.14 or later (for launchd service)
- **Python**: 3.7+ (for scheduler daemon)
- **Task-specific**: Each task may have additional requirements

## License

MIT
