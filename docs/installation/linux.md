# Linux Installation

Install Simple Task Manager on Linux using systemd for service management.

## Requirements

- **Linux**: systemd-based distribution (Ubuntu, Debian, Fedora, Arch, etc.)
- **Python**: 3.7 or higher
- **Git**: For cloning the repository

### Install Prerequisites

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-venv git make
```

**Fedora:**
```bash
sudo dnf install python3 git make
```

**Arch:**
```bash
sudo pacman -S python git make
```

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/patarra/simple-task-manager.git
cd simple-task-manager
```

### 2. Install Dependencies

```bash
make install
```

This will:
- Create a Python virtual environment in `scheduler/.venv/`
- Install APScheduler and PyYAML
- Install dependencies for each task in `tasks/*/`

### 3. Configure Tasks

Edit `config.yaml`:

```yaml
scheduler:
  log_file: ~/.local/share/scheduler/logs/scheduler.log
  default_timeout: 300

tasks:
  - name: my-task
    path: tasks/my-task
    cron: "*/30 * * * *"
    args: []
    enabled: true
```

### 4. Install systemd Service

```bash
make install-service
```

This creates: `~/.config/systemd/user/scheduler.service`

The service file configures systemd to:
- Run the scheduler as a user service
- Restart on failure
- Log to `~/.local/share/scheduler/logs/scheduler.log`

### 5. Enable and Start the Service

```bash
# Start the service
make service-start

# Enable auto-start at boot (optional)
systemctl --user enable scheduler
```

## Verification

### Check Service Status

```bash
make service-status
```

Output should show:

```
● scheduler.service - Task Scheduler
     Loaded: loaded (/home/user/.config/systemd/user/scheduler.service; disabled)
     Active: active (running)
```

### View Logs

```bash
make service-logs
```

Or use journalctl:

```bash
journalctl --user -u scheduler -f
```

You should see:

```
[2025-12-15 10:00:00] INFO: Scheduler started, loaded 1 tasks
[2025-12-15 10:00:00] INFO: Registered task 'my-task' with cron '*/30 * * * *'
```

## Service Management

### Start/Stop/Restart

```bash
make service-start     # Start the scheduler
make service-stop      # Stop the scheduler
make service-restart   # Restart the scheduler
```

Or use systemctl directly:

```bash
systemctl --user start scheduler
systemctl --user stop scheduler
systemctl --user restart scheduler
systemctl --user status scheduler
```

### Enable Auto-Start at Boot

```bash
# Enable the service
systemctl --user enable scheduler

# Check if enabled
systemctl --user is-enabled scheduler
```

### Disable Auto-Start

```bash
systemctl --user disable scheduler
```

## Logs

### View Live Logs

```bash
# Using make
make service-logs

# Or using journalctl
journalctl --user -u scheduler -f
```

### View Last N Lines

```bash
journalctl --user -u scheduler -n 50
```

### View Logs Since Time

```bash
journalctl --user -u scheduler --since "1 hour ago"
journalctl --user -u scheduler --since "2025-12-15 10:00:00"
```

### Export Logs

```bash
journalctl --user -u scheduler --since today > scheduler-logs.txt
```

## Lingering (Run Without Login)

By default, user services stop when you log out. To keep the scheduler running:

```bash
# Enable lingering for your user
loginctl enable-linger $USER

# Verify
loginctl show-user $USER | grep Linger
```

Now the scheduler will:
- Start at system boot
- Keep running even when you're not logged in
- Stop only at system shutdown

## Troubleshooting

### Service Won't Start

```bash
# Check for syntax errors
systemd-analyze --user verify scheduler.service

# View detailed logs
journalctl --user -u scheduler -xe
```

### Permission Denied

```bash
# Make sure run.sh files are executable
chmod +x tasks/*/run.sh

# Check service file permissions
ls -la ~/.config/systemd/user/scheduler.service
```

### Service Stops After Logout

Enable lingering:

```bash
loginctl enable-linger $USER
```

### Task-Specific Issues

Some tasks may be OS-specific. Check if the task supports Linux:

```bash
cd tasks/calendar-sync
make install
```

Tasks that require macOS-specific frameworks (like EventKit) will show a warning and skip installation.

## Uninstallation

```bash
# Disable and stop the service
systemctl --user disable scheduler
make uninstall-service

# Remove dependencies
make clean-venv
make clean-all

# Disable lingering (if enabled)
loginctl disable-linger $USER

# Remove the repository
cd ..
rm -rf simple-task-manager
```

Logs remain in `~/.local/share/scheduler/logs/` for reference.

## Advanced Configuration

### Custom Log Location

Edit `~/.config/systemd/user/scheduler.service`:

```ini
[Service]
StandardOutput=append:/custom/path/scheduler.log
StandardError=append:/custom/path/scheduler.error.log
```

Then reload and restart:

```bash
systemctl --user daemon-reload
make service-restart
```

### Environment Variables

Add environment variables to the service file:

```ini
[Service]
Environment="MY_VAR=value"
Environment="ANOTHER_VAR=another_value"
```

Reload and restart:

```bash
systemctl --user daemon-reload
make service-restart
```

### Resource Limits

Limit CPU or memory usage:

```ini
[Service]
CPUQuota=50%
MemoryMax=512M
```

### Nice Level (Priority)

Adjust process priority:

```ini
[Service]
Nice=10  # Lower priority (higher nice value)
```

## Integration with System Services

If you need root-level access, you can install as a system service instead:

```bash
# Copy service file to system location
sudo cp ~/.config/systemd/user/scheduler.service /etc/systemd/system/

# Edit paths to use absolute paths
sudo nano /etc/systemd/system/scheduler.service

# Enable and start
sudo systemctl enable scheduler
sudo systemctl start scheduler
```

Note: This is usually not necessary for personal task automation.

## Next Steps

- [Configuration Reference](../configuration.md)
- [Adding Tasks](../guides/adding-tasks.md)
- [Troubleshooting](../troubleshooting.md)
