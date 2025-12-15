# Simple Task Manager

A centralized YAML-configured task scheduler for macOS and Linux periodic tasks. Each task runs in its own isolated environment with a standardized `run.sh` interface.

## Key Features

- **🎯 Simple Configuration**: Single YAML file for all tasks
- **🔌 Decoupled Architecture**: Scheduler only knows about `run.sh` + args
- **🔒 Isolated Environments**: Each task has its own venv/dependencies
- **🌐 Cross-Platform**: Works on macOS (launchd) and Linux (systemd)
- **🗣️ Polyglot**: Write tasks in Python, Go, Bash, or any language
- **⏱️ Cron Scheduling**: Standard cron expressions for flexible scheduling
- **📝 Centralized Logging**: All task executions logged in one place

!!! info "Personal Project"
    This is a personal project, primarily built for my own use. It is provided as-is, without any warranty or guarantee. Use at your own risk.

## Architecture Overview

```
simple-task-manager/
├── config.yaml              # Central configuration for all tasks
├── Makefile                 # Installation and service management
├── scheduler/               # Scheduling daemon (APScheduler)
│   ├── scheduler.py
│   ├── config/              # Service templates
│   │   ├── scheduler.plist.template      (macOS)
│   │   └── scheduler.service.template    (Linux)
│   └── .venv/
└── tasks/                   # Your periodic tasks
    └── calendar-sync/       # Example task
        ├── run.sh          # Standard entry point
        ├── Makefile
        └── .venv/
```

## Quick Start

Get started in 3 steps:

```bash
# 1. Install scheduler and all tasks
make install

# 2. Install system service
make install-service

# 3. Start the scheduler
make service-start
```

See the [Quick Start Guide](quick-start.md) for detailed instructions.

## Design Principles

- **Decoupled**: Scheduler executes `run.sh`, doesn't know about Python/Go/etc
- **Isolated**: Each task manages its own environment and dependencies
- **Simple**: YAML config instead of multiple plist/systemd files
- **Portable**: Same code works on macOS and Linux
- **Transparent**: All logs in one place with clear execution tracking

## Use Cases

- Synchronize calendars between services
- Backup files periodically
- Run health checks and monitoring
- Data pipeline orchestration
- Automated reports generation
- Any recurring task you need to run on a schedule

## Requirements

- **macOS**: 10.14+ (for launchd service)
- **Linux**: systemd-based distribution
- **Python**: 3.7+ (for scheduler daemon)
- **Task-specific**: Each task may have additional requirements

## Next Steps

- [Installation Guide](installation/index.md) - Platform-specific installation
- [Configuration Reference](configuration.md) - Complete config.yaml guide
- [Adding Tasks](guides/adding-tasks.md) - Create your own tasks
- [Available Tasks](tasks/index.md) - Browse existing tasks
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
