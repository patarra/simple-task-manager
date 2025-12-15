# Simple Task Manager

Lightweight task scheduler with cron-based scheduling for personal automation on macOS and Linux.

**Key Features:**
- **Simple**: Single YAML configuration file for all tasks
- **Language-agnostic**: Write tasks in Python, Go, Bash, or any language
- **Isolated**: Each task runs in its own environment with zero dependency conflicts
- **Cross-platform**: Works on both macOS (launchd) and Linux (systemd)

📚 **[View Full Documentation](https://patarra.github.io/simple-task-manager/)**

> **Note:** This is a personal project, primarily built for my own use. It is provided as-is, without any warranty or guarantee. Use at your own risk.

## Quick Start

**Installation:**
```bash
make install
make install-service
make service-start
```

**Configuration:**

Edit `config.yaml` to define your tasks:

```yaml
tasks:
  - name: my-task
    path: tasks/my-task
    cron: "*/30 * * * *"
    enabled: true
```

**Learn More:**
- 📖 [Quick Start Guide](https://patarra.github.io/simple-task-manager/quick-start/)
- ⚙️ [Installation Instructions](https://patarra.github.io/simple-task-manager/installation/)
- 📝 [Configuration Reference](https://patarra.github.io/simple-task-manager/configuration/)
- 🔧 [Adding Custom Tasks](https://patarra.github.io/simple-task-manager/guides/adding-tasks/)

## Available Commands

```bash
# Installation
make install              # Install scheduler + all tasks
make install-service      # Generate and install service (launchd/systemd)

# Service Management
make service-start        # Start the scheduler daemon
make service-stop         # Stop the scheduler daemon
make service-restart      # Restart the scheduler daemon
make service-status       # Show scheduler status
make service-logs         # Show scheduler logs

# Testing
make test-scheduler       # Test scheduler locally

# Help
make help                 # Show all available commands
```

For detailed documentation, see:
- 📖 [Configuration Reference](https://patarra.github.io/simple-task-manager/configuration/)
- 🛠️ [Troubleshooting Guide](https://patarra.github.io/simple-task-manager/troubleshooting/)
- 🏗️ [Architecture](https://patarra.github.io/simple-task-manager/architecture/)

## Requirements

- **macOS**: 10.14+ (using launchd) or **Linux** (using systemd)
- **Python**: 3.7+

## License

MIT
