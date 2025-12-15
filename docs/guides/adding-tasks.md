# Adding Tasks

Learn how to create custom tasks for Simple Task Manager.

## Overview

A task is a self-contained directory with:
- `run.sh` - Executable entry point
- `Makefile` - Build and installation commands
- Task implementation (Python, Go, Bash, etc.)
- Dependencies specification

## Quick Start

### 1. Create Task Directory

```bash
mkdir -p tasks/my-task
cd tasks/my-task
```

### 2. Create `run.sh`

```bash
#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate environment if needed
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Run your task
python "$SCRIPT_DIR/main.py" "$@"
```

Make it executable:

```bash
chmod +x run.sh
```

### 3. Create Task Implementation

`main.py`:

```python
#!/usr/bin/env python3
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='My task')
    parser.add_argument('--option', help='An option')
    args = parser.parse_args()

    print(f"Running my-task with option: {args.option}")
    # Your task logic here

    return 0

if __name__ == '__main__':
    sys.exit(main())
```

### 4. Create `Makefile`

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

### 5. Create `requirements.txt`

```txt
# Add your dependencies
requests>=2.28.0
```

### 6. Add to Config

Edit root `config.yaml`:

```yaml
tasks:
  - name: my-task
    path: tasks/my-task
    cron: "0 * * * *"
    args:
      - "--option"
      - "value"
    enabled: true
```

### 7. Update Root Makefile

Edit root `Makefile`, add your task to `TASKS`:

```makefile
TASKS := calendar-sync my-task
```

### 8. Install and Test

```bash
# From repository root
make install
make test-scheduler
```

## Task Templates

### Python Task

**Directory structure:**
```
tasks/python-task/
├── run.sh
├── Makefile
├── requirements.txt
├── main.py
└── .venv/
```

**run.sh:**
```bash
#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi
python "$SCRIPT_DIR/main.py" "$@"
```

**Makefile:**
```makefile
.PHONY: install clean test

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

test:
	$(PYTHON) -m pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
```

### Go Task

**Directory structure:**
```
tasks/go-task/
├── run.sh
├── Makefile
├── go.mod
├── go.sum
└── main.go
```

**run.sh:**
```bash
#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
go run . "$@"
```

**Makefile:**
```makefile
.PHONY: install clean build test

install:
	go mod download

build:
	go build -o task

test:
	go test ./...

clean:
	rm -f task
	go clean
```

### Bash Task

**Directory structure:**
```
tasks/bash-task/
├── run.sh
├── Makefile
└── lib.sh (optional)
```

**run.sh:**
```bash
#!/bin/bash
set -e

# Source helpers if needed
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

# Your task logic
main() {
    echo "Running bash task with args: $@"
    # Task implementation
}

main "$@"
```

**Makefile:**
```makefile
.PHONY: install clean test

install:
	@echo "No dependencies to install"

test:
	shellcheck run.sh

clean:
	@echo "Nothing to clean"
```

## OS-Specific Tasks

Tasks that only work on specific operating systems should detect and handle this gracefully.

### macOS-Only Task

```makefile
# Detect OS
UNAME_S := $(shell uname -s)

install:
	@if [ "$(UNAME_S)" != "Darwin" ]; then \
		echo "⚠️  SKIPPING: This task requires macOS"; \
		echo "   Current OS: $(UNAME_S)"; \
		exit 0; \
	fi
	# Normal installation
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
```

### Linux-Only Task

```makefile
UNAME_S := $(shell uname -s)

install:
	@if [ "$(UNAME_S)" = "Darwin" ]; then \
		echo "⚠️  SKIPPING: This task requires Linux"; \
		exit 0; \
	fi
	# Normal installation
```

## Task Contract

### Input

**Arguments:**
- Passed from `config.yaml` args list
- Accessible via `$@` in bash, `sys.argv` in Python

**Working Directory:**
- Scheduler runs `run.sh` from the task directory
- Use relative paths within task

**Environment:**
- Inherits scheduler's environment
- `PATH` includes task's venv/bin if activated

### Output

**Exit Code:**
- `0` = Success
- Non-zero = Failure (logged as error)

**stdout:**
- Logged with `[task-name] STDOUT:` prefix
- Use for normal output

**stderr:**
- Logged with `[task-name] STDERR:` prefix
- Use for errors and warnings

**Example:**

```python
import sys

print("Processing item 1")  # Goes to stdout
print("Warning: slow network", file=sys.stderr)  # Goes to stderr

sys.exit(0)  # Success
```

### Timeout

If task exceeds `timeout`, scheduler kills the process.

**Handling:**
```python
import signal
import sys

def signal_handler(sig, frame):
    print("Task timed out, cleaning up...")
    # Cleanup logic
    sys.exit(1)

signal.signal(signal.SIGTERM, signal_handler)
```

## Best Practices

### 1. Make `run.sh` Robust

```bash
#!/bin/bash
set -e  # Exit on error
set -u  # Error on undefined variable
set -o pipefail  # Pipeline failures

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Validate environment
if [ ! -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    echo "Error: Virtual environment not found" >&2
    exit 1
fi

source "$SCRIPT_DIR/.venv/bin/activate"
python "$SCRIPT_DIR/main.py" "$@"
```

### 2. Handle Arguments Properly

```python
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--required', required=True)
    parser.add_argument('--optional', default='default')

    args = parser.parse_args()
    # Use args.required, args.optional
```

### 3. Provide Helpful Errors

```python
try:
    result = do_work()
except FileNotFoundError as e:
    print(f"Error: Required file not found: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}", file=sys.stderr)
    sys.exit(1)
```

### 4. Log Progress

```python
print("Starting data sync...")
print(f"Processed {count} items")
print("Sync complete")
```

### 5. Make Tasks Idempotent

Tasks should be safe to run multiple times:

```python
# Check if work is needed
if not needs_update():
    print("Already up to date")
    return 0

# Do the work
update()
```

### 6. Add README

Create `tasks/my-task/README.md`:

```markdown
# My Task

Brief description of what this task does.

## Requirements

- Python 3.7+
- API key in `~/.myservice/config`

## Configuration

```yaml
- name: my-task
  cron: "0 * * * *"
  args:
    - "--api-key"
    - "your-key"
```

## Testing

```bash
cd tasks/my-task
./run.sh --api-key test
```
```

## Testing Tasks

### Manual Testing

```bash
cd tasks/my-task
./run.sh --option value
```

### With Make

```bash
cd tasks/my-task
make install
make test
```

### In Scheduler (dry run)

Edit `config.yaml` with a test schedule:

```yaml
- name: my-task
  path: tasks/my-task
  cron: "*/5 * * * *"  # Every 5 minutes for testing
  args: ["--test-mode"]
  enabled: true
```

Run locally:

```bash
make test-scheduler
```

Watch logs:

```bash
tail -f ~/Library/Logs/scheduler.log
```

## Debugging

### Enable Verbose Output

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.debug("Detailed debug info")
logging.info("Normal info")
logging.error("Error occurred")
```

### Add Debug Mode

```python
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.DEBUG)
```

Configure in `config.yaml`:

```yaml
args:
  - "--debug"
```

## Examples

See existing tasks for reference:

- [calendar-sync](../tasks/calendar-sync.md) - Python task with macOS APIs
- Add your own examples here

## Next Steps

- [Configuration Reference](../configuration.md) - Configure your task
- [Troubleshooting](../troubleshooting.md) - Debug task issues
- [Architecture](../architecture.md) - Understand the system
