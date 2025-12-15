# Quick Start

Get Simple Task Manager running in under 5 minutes.

## Prerequisites

- macOS 10.14+ or Linux with systemd
- Python 3.7 or higher
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/patarra/simple-task-manager.git
cd simple-task-manager
```

### 2. Install Dependencies

This installs the scheduler daemon and all tasks:

```bash
make install
```

You'll see output like:

```
Installing task scheduler...
Installing scheduler daemon...
✓ Scheduler dependencies installed
Installing tasks...
✓ Calendar Sync dependencies installed
✓ Installation complete
```

### 3. Configure Tasks

Edit `config.yaml` to configure your tasks:

```yaml
scheduler:
  log_file: ~/Library/Logs/scheduler.log  # macOS
  # log_file: ~/.local/share/scheduler/logs/scheduler.log  # Linux
  default_timeout: 300

tasks:
  - name: calendar-sync
    path: tasks/calendar-sync
    cron: "*/30 * * * *"  # Every 30 minutes
    args:
      - "--source-calendar"
      - "your-email@example.com"
      - "--days"
      - "30"
      - "--do-sync"
      - "Personal"
    timeout: 600
    enabled: true
```

### 4. Install System Service

Generate the appropriate service file for your OS:

```bash
make install-service
```

**macOS**: Creates `~/Library/LaunchAgents/com.patarra.scheduler.plist`
**Linux**: Creates `~/.config/systemd/user/scheduler.service`

### 5. Start the Scheduler

```bash
make service-start
```

### 6. Verify It's Running

Check the scheduler status:

```bash
make service-status
```

View logs:

```bash
make service-logs
```

You should see output like:

```
[2025-12-15 10:00:00] INFO: Scheduler started, loaded 1 tasks
[2025-12-15 10:00:00] INFO: Registered task 'calendar-sync' with cron '*/30 * * * *'
```

## Test Locally (Optional)

Before installing as a service, you can test the scheduler locally:

```bash
make test-scheduler
```

Press `Ctrl+C` to stop.

## Next Steps

- **Configure more tasks**: See [Configuration Reference](configuration.md)
- **Add your own task**: Follow the [Adding Tasks Guide](guides/adding-tasks.md)
- **Browse available tasks**: Check out [Available Tasks](tasks/index.md)
- **Having issues?**: Visit [Troubleshooting](troubleshooting.md)

## Common Commands

```bash
# Service management
make service-start       # Start the scheduler
make service-stop        # Stop the scheduler
make service-restart     # Restart the scheduler
make service-status      # Check if running
make service-logs        # View execution logs

# Maintenance
make clean               # Clean cache files
make clean-venv          # Remove virtual environments

# Help
make help                # Show all available commands
```

## Platform-Specific Guides

- [macOS Installation](installation/macos.md) - Detailed macOS setup
- [Linux Installation](installation/linux.md) - Detailed Linux setup
