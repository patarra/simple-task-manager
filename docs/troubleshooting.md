# Troubleshooting

Common issues and solutions for Simple Task Manager.

## Installation Issues

### Python Version Too Old

**Symptom:** `ERROR: Python 3.7+ required`

**Solution:**

```bash
# Check Python version
python3 --version

# Install newer Python (macOS)
brew install python@3.11

# Install newer Python (Ubuntu/Debian)
sudo apt install python3.11
```

### Make Not Found

**Symptom:** `bash: make: command not found`

**Solution:**

**macOS:**
```bash
xcode-select --install
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install build-essential

# Fedora
sudo dnf groupinstall "Development Tools"
```

### Permission Denied Creating Venv

**Symptom:** `Permission denied: '.venv'`

**Solution:**

```bash
# Check directory permissions
ls -la

# Ensure you own the directory
sudo chown -R $USER:$USER .
```

## Service Issues

### Service Won't Start (macOS)

**Check for errors:**

```bash
# View launchd logs
log show --predicate 'process == "launchd"' --last 5m | grep scheduler

# Check plist syntax
plutil -lint ~/Library/LaunchAgents/com.patarra.scheduler.plist

# Try loading manually
launchctl load ~/Library/LaunchAgents/com.patarra.scheduler.plist
```

**Common fixes:**

```bash
# Unload and reload
launchctl unload ~/Library/LaunchAgents/com.patarra.scheduler.plist
launchctl load ~/Library/LaunchAgents/com.patarra.scheduler.plist
```

### Service Won't Start (Linux)

**Check for errors:**

```bash
# View systemd status
systemctl --user status scheduler

# View detailed logs
journalctl --user -u scheduler -xe
```

**Common fixes:**

```bash
# Reload systemd configuration
systemctl --user daemon-reload

# Check service file syntax
systemd-analyze --user verify scheduler.service
```

### Service Stops After Logout (Linux)

**Symptom:** Scheduler stops when you log out

**Solution:** Enable lingering

```bash
loginctl enable-linger $USER
```

Verify:

```bash
loginctl show-user $USER | grep Linger
# Should show: Linger=yes
```

### Service Not Loaded

**Symptom:** `make service-status` shows "Service not installed"

**Solution:**

```bash
make install-service
make service-start
```

## Task Execution Issues

### Task Fails with "Virtual Environment Not Found"

**Symptom:**
```
Error: Virtual environment not found. Run 'make install' first.
```

**Solution:**

```bash
# From repository root
make install

# Or install specific task
cd tasks/task-name
make install
```

### Task Fails with "Permission Denied"

**Symptom:**
```
bash: ./run.sh: Permission denied
```

**Solution:**

```bash
chmod +x tasks/*/run.sh
```

### Task Times Out

**Symptom:**
```
ERROR: Task 'my-task' exceeded timeout of 300s
```

**Solution:**

Increase timeout in `config.yaml`:

```yaml
- name: my-task
  timeout: 600  # Increase to 10 minutes
```

### Task Fails Silently

**Symptom:** No output in logs

**Check:**

1. Task is enabled:
   ```yaml
   enabled: true
   ```

2. Cron expression is valid:
   ```bash
   # Test with online tool: https://crontab.guru/
   ```

3. `run.sh` has correct shebang:
   ```bash
   #!/bin/bash
   ```

4. Test manually:
   ```bash
   cd tasks/task-name
   ./run.sh [args...]
   ```

### macOS-Only Task on Linux

**Symptom:**
```
⚠️  SKIPPING: calendar-sync (macOS only)
```

**Explanation:** This is expected. Some tasks require OS-specific frameworks.

**Solution:** Disable in `config.yaml` on Linux systems:

```yaml
- name: calendar-sync
  enabled: false  # Disable on Linux
```

## Configuration Issues

### Invalid YAML Syntax

**Symptom:**
```
ERROR: Failed to parse config.yaml
```

**Solution:**

Validate YAML syntax:

```bash
# Install yamllint
pip install yamllint

# Check syntax
yamllint config.yaml
```

Common issues:
- Inconsistent indentation (mix of tabs and spaces)
- Missing colons
- Unquoted strings with special characters

### Config Changes Not Applied

**Symptom:** Old configuration still running

**Solution:**

```bash
make service-restart
```

The scheduler loads config on startup, not during runtime.

### Cron Not Triggering

**Verify cron expression:**

```python
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

trigger = CronTrigger.from_crontab("*/30 * * * *")
print("Next run:", trigger.get_next_fire_time(None, datetime.now()))
```

**Common mistakes:**
- `0 */2 * * *` (correct: every 2 hours)
- `*/2 0 * * *` (wrong: only at midnight)

## Logging Issues

### No Logs Appearing

**Check log file location:**

```bash
# macOS
ls -la ~/Library/Logs/scheduler.log

# Linux
ls -la ~/.local/share/scheduler/logs/scheduler.log
```

**Verify in config.yaml:**

```yaml
scheduler:
  log_file: ~/Library/Logs/scheduler.log
```

**Check permissions:**

```bash
# Ensure log directory exists and is writable
mkdir -p ~/Library/Logs
chmod 755 ~/Library/Logs
```

### Logs Filling Disk

**Rotate logs (Linux with systemd):**

Create `~/.config/systemd/user/scheduler.service.d/override.conf`:

```ini
[Service]
StandardOutput=append:/var/log/scheduler/scheduler.log
StandardError=append:/var/log/scheduler/error.log
```

Use logrotate:

```bash
sudo nano /etc/logrotate.d/scheduler
```

```
/var/log/scheduler/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

**Manual cleanup:**

```bash
# Keep last 1000 lines
tail -1000 ~/Library/Logs/scheduler.log > /tmp/scheduler.log
mv /tmp/scheduler.log ~/Library/Logs/scheduler.log
```

## Permission Issues

### Calendar Access Denied (macOS)

**Symptom:**
```
Error: Calendar access denied
```

**Solution:**

1. Open **System Preferences**
2. **Security & Privacy** → **Privacy**
3. Select **Calendars**
4. Check **Terminal** or **Python**

Or reset permissions:

```bash
tccutil reset Calendar
```

Next run will prompt again.

### Full Disk Access Needed

Some tasks may need Full Disk Access:

1. **System Preferences** → **Security & Privacy**
2. **Privacy** → **Full Disk Access**
3. Add Terminal or Python

## Performance Issues

### Scheduler Using High CPU

**Check running tasks:**

```bash
# macOS
ps aux | grep scheduler

# Linux
systemctl --user status scheduler
```

**Solutions:**
- Reduce task frequency in cron expressions
- Optimize task implementation
- Add timeout limits

### Task Running Too Long

**Add timeout:**

```yaml
- name: slow-task
  timeout: 300  # Kill after 5 minutes
```

**Optimize task:**
- Add early exit conditions
- Use incremental processing
- Cache results

## Debugging

### Enable Debug Logging

Edit `scheduler/scheduler.py` logging level:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO
    # ...
)
```

Restart scheduler:

```bash
make service-restart
```

### Test Task Manually

```bash
cd tasks/task-name
./run.sh --arg1 value1
echo "Exit code: $?"
```

### Run Scheduler Locally

```bash
make service-stop
make test-scheduler
```

Press `Ctrl+C` to stop.

### Check Task Dependencies

```bash
cd tasks/task-name
make install
make test  # If available
```

## Error Messages

### "Config file not found"

**Cause:** `config.yaml` missing from repository root

**Solution:**

```bash
# Copy example config
cp config.yaml.example config.yaml
nano config.yaml
```

### "Task directory does not exist"

**Cause:** Path in config.yaml is incorrect

**Solution:**

Check path is relative to repository root:

```yaml
# Correct
path: tasks/my-task

# Wrong
path: /absolute/path/to/tasks/my-task
path: my-task  # Missing tasks/ prefix
```

### "run.sh not found"

**Cause:** Missing `run.sh` in task directory

**Solution:**

```bash
cd tasks/task-name
nano run.sh
chmod +x run.sh
```

### "run.sh is not executable"

**Cause:** Script lacks execute permission

**Solution:**

```bash
chmod +x tasks/*/run.sh
```

### "Invalid cron expression"

**Cause:** Malformed cron expression

**Solution:**

Use standard 5-field format: `* * * * *`

Test at [crontab.guru](https://crontab.guru/)

Common mistakes:
- 6 fields (includes seconds) - not supported
- 4 fields - missing day of week
- Invalid ranges like `25-30` for hours

## Getting Help

### Check Logs First

```bash
make service-logs
```

### Test Locally

```bash
make test-scheduler
```

### Check Service Status

```bash
make service-status
```

### Manual Task Test

```bash
cd tasks/task-name
./run.sh [args...]
```

### Report Issues

If you found a bug:

1. Check [existing issues](https://github.com/patarra/simple-task-manager/issues)
2. Create new issue with:
   - OS and version
   - Python version
   - Error logs
   - Steps to reproduce

## Next Steps

- [Configuration Reference](configuration.md) - Config options
- [Adding Tasks](guides/adding-tasks.md) - Create tasks
- [Architecture](architecture.md) - System design
