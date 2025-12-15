# macOS Installation

Install Simple Task Manager on macOS using launchd for service management.

## Requirements

- **macOS**: 10.14 (Mojave) or later
- **Python**: 3.7+ (usually pre-installed)
- **Xcode Command Line Tools**: For build tools

```bash
xcode-select --install
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
  log_file: ~/Library/Logs/scheduler.log
  default_timeout: 300

tasks:
  - name: calendar-sync
    path: tasks/calendar-sync
    cron: "*/30 * * * *"
    args: ["--days", "30"]
    enabled: true
```

### 4. Install launchd Service

```bash
make install-service
```

This creates: `~/Library/LaunchAgents/com.patarra.scheduler.plist`

The plist file configures launchd to:
- Run the scheduler at login (`RunAtLoad`)
- Keep the scheduler running (`KeepAlive`)
- Log to `~/Library/Logs/scheduler.log`

### 5. Start the Service

```bash
make service-start
```

The scheduler will now:
- Start automatically at login
- Restart if it crashes
- Execute tasks according to their cron schedules

## Verification

### Check Service Status

```bash
make service-status
```

Output should show:

```
Scheduler Service Status:

12345  0  com.patarra.scheduler

✓ Service installed: /Users/you/Library/LaunchAgents/com.patarra.scheduler.plist
```

### View Logs

```bash
make service-logs
```

You should see:

```
[2025-12-15 10:00:00] INFO: Scheduler started, loaded 1 tasks
[2025-12-15 10:00:00] INFO: Registered task 'calendar-sync' with cron '*/30 * * * *'
```

### Manual Log Access

```bash
tail -f ~/Library/Logs/scheduler.log
```

## Service Management

### Start/Stop/Restart

```bash
make service-start     # Start the scheduler
make service-stop      # Stop the scheduler
make service-restart   # Restart the scheduler
```

### Enable/Disable Auto-Start

The service starts automatically at login by default.

To disable auto-start:

```bash
# Stop the service
make service-stop

# Edit the plist
nano ~/Library/LaunchAgents/com.patarra.scheduler.plist

# Change RunAtLoad to false:
# <key>RunAtLoad</key>
# <false/>
```

### Manual Start (for testing)

```bash
# Stop the service first
make service-stop

# Run scheduler manually
make test-scheduler
```

Press `Ctrl+C` to stop.

## Permissions

### Calendar Access (for calendar-sync task)

On first run of the calendar-sync task, macOS will prompt:

```
"Terminal" would like to access your calendar.
```

Click **OK** to grant access.

If you accidentally denied it:

1. Open **System Preferences** → **Security & Privacy**
2. Select **Privacy** tab
3. Select **Calendars** from the left sidebar
4. Check the box next to **Terminal** (or **Python**)

### Full Disk Access (if needed)

Some tasks may require Full Disk Access:

1. **System Preferences** → **Security & Privacy**
2. **Privacy** tab → **Full Disk Access**
3. Add Python or Terminal if needed

## Troubleshooting

### Service Won't Start

```bash
# Check for errors in the plist
plutil -lint ~/Library/LaunchAgents/com.patarra.scheduler.plist

# Check system logs
log show --predicate 'process == "launchd"' --last 5m
```

### Permission Denied

```bash
# Make sure run.sh files are executable
chmod +x tasks/*/run.sh

# Check launchd permissions
ls -la ~/Library/LaunchAgents/com.patarra.scheduler.plist
```

### Task Fails on macOS

Check if the task is macOS-compatible. Some tasks are OS-specific:

```bash
# Check task Makefile for OS detection
cd tasks/calendar-sync
make install
```

OS-specific tasks will show a warning on unsupported platforms.

## Uninstallation

```bash
# Stop and remove the service
make uninstall-service

# Remove dependencies
make clean-venv
make clean-all

# Remove the repository
cd ..
rm -rf simple-task-manager
```

Logs remain in `~/Library/Logs/scheduler.log` for reference.

## Advanced Configuration

### Custom Log Location

Edit `~/Library/LaunchAgents/com.patarra.scheduler.plist`:

```xml
<key>StandardOutPath</key>
<string>/custom/path/scheduler.log</string>
```

Then restart:

```bash
make service-restart
```

### Environment Variables

Add environment variables to the plist:

```xml
<key>EnvironmentVariables</key>
<dict>
    <key>MY_VAR</key>
    <string>value</string>
</dict>
```

## Next Steps

- [Configuration Reference](../configuration.md)
- [Adding Tasks](../guides/adding-tasks.md)
- [Troubleshooting](../troubleshooting.md)
