# Configuration Reference

Complete reference for `config.yaml` configuration file.

## Configuration File Location

The configuration file must be named `config.yaml` and located in the repository root:

```
simple-task-manager/
├── config.yaml          ← Here
├── Makefile
├── scheduler/
└── tasks/
```

## File Structure

```yaml
# Global scheduler settings
scheduler:
  log_file: <path>
  default_timeout: <seconds>

# Task definitions
tasks:
  - name: <task-name>
    path: <task-path>
    cron: "<cron-expression>"
    args: [<arg1>, <arg2>, ...]
    timeout: <seconds>
    enabled: <true|false>
```

## Scheduler Section

Global settings for the scheduler daemon.

### `log_file`

**Type:** String
**Required:** No
**Default:**
- macOS: `~/Library/Logs/scheduler.log`
- Linux: `~/.local/share/scheduler/logs/scheduler.log`

Path to the scheduler log file. Supports tilde (`~`) expansion.

```yaml
scheduler:
  log_file: ~/my-custom-location/scheduler.log
```

### `default_timeout`

**Type:** Integer
**Required:** No
**Default:** `300` (5 minutes)

Default maximum execution time in seconds for tasks that don't specify their own timeout.

```yaml
scheduler:
  default_timeout: 600  # 10 minutes
```

## Tasks Section

Array of task definitions.

### `name`

**Type:** String
**Required:** Yes
**Unique:** Yes

Unique identifier for the task. Used in logs and must be unique across all tasks.

```yaml
- name: calendar-sync
```

**Valid names:**
- `my-task`
- `backup-photos`
- `data-pipeline`

**Invalid names:**
- Names with spaces
- Duplicate names

### `path`

**Type:** String
**Required:** Yes

Relative path from the repository root to the task directory. Must contain a `run.sh` file.

```yaml
- path: tasks/calendar-sync
```

The scheduler will:
1. Change to this directory
2. Execute `./run.sh` with the specified arguments

### `cron`

**Type:** String
**Required:** Yes

Standard 5-field cron expression defining when the task runs.

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6) (Sunday=0)
│ │ │ │ │
* * * * *
```

**Examples:**

```yaml
cron: "*/30 * * * *"     # Every 30 minutes
cron: "0 * * * *"        # Every hour at minute 0
cron: "0 9 * * *"        # Every day at 9:00 AM
cron: "0 9 * * 1"        # Every Monday at 9:00 AM
cron: "0 9-17 * * 1-5"   # Every hour 9-5, Mon-Fri
cron: "0 0 1 * *"        # First day of every month
cron: "0 0 * * 0"        # Every Sunday at midnight
```

**Special characters:**
- `*` - Any value
- `,` - List (e.g., `1,15` = 1st and 15th)
- `-` - Range (e.g., `9-17` = 9 through 17)
- `/` - Step (e.g., `*/15` = every 15 minutes)

**Testing cron expressions:**
- [crontab.guru](https://crontab.guru/) - Cron expression explainer
- [crontab-generator.org](https://crontab-generator.org/) - Visual cron builder

### `args`

**Type:** Array of strings
**Required:** No
**Default:** `[]`

Arguments passed to `run.sh`. Can be flags, options, or values.

```yaml
args:
  - "--source-calendar"
  - "work@example.com"
  - "--days"
  - "30"
  - "--exclude-declined-events"
```

Executed as:

```bash
./run.sh --source-calendar work@example.com --days 30 --exclude-declined-events
```

**Empty args:**

```yaml
args: []
```

### `timeout`

**Type:** Integer
**Required:** No
**Default:** Uses `scheduler.default_timeout`

Maximum execution time in seconds. Task is killed if it exceeds this limit.

```yaml
timeout: 600  # 10 minutes
```

**Choosing timeout values:**
- Short tasks (< 1 min): 60-300 seconds
- Medium tasks (1-5 min): 300-600 seconds
- Long tasks (5-30 min): 600-1800 seconds

Set timeouts higher than expected execution time to allow for variations.

### `enabled`

**Type:** Boolean
**Required:** No
**Default:** `true`

Whether the task should be registered with the scheduler.

```yaml
enabled: true   # Task will run
enabled: false  # Task will be skipped
```

Use `enabled: false` to temporarily disable tasks without deleting configuration.

## Complete Example

```yaml
# Scheduler configuration
scheduler:
  log_file: ~/Library/Logs/scheduler.log
  default_timeout: 300

# Task definitions
tasks:
  # Calendar synchronization - runs every 30 minutes
  - name: calendar-sync
    path: tasks/calendar-sync
    cron: "*/30 * * * *"
    args:
      - "--source-calendar"
      - "work@company.com"
      - "--days"
      - "30"
      - "--exclude-declined-events"
      - "--do-sync"
      - "Personal"
    timeout: 600
    enabled: true

  # Daily backup - runs at 2 AM
  - name: backup-photos
    path: tasks/backup-photos
    cron: "0 2 * * *"
    args:
      - "--source"
      - "~/Pictures"
      - "--destination"
      - "/mnt/backup"
    timeout: 3600
    enabled: true

  # Weekly report - runs Monday at 9 AM
  - name: weekly-report
    path: tasks/weekly-report
    cron: "0 9 * * 1"
    args: []
    timeout: 300
    enabled: true

  # Disabled task - kept for reference
  - name: old-task
    path: tasks/old-task
    cron: "0 0 * * *"
    args: []
    enabled: false
```

## Configuration Validation

The scheduler validates configuration on startup:

- **Syntax errors**: Invalid YAML format
- **Missing required fields**: `name`, `path`, `cron`
- **Invalid cron expressions**: Syntax errors in cron
- **Missing `run.sh`**: Task path doesn't contain `run.sh`
- **Non-executable `run.sh`**: Script lacks execute permission
- **Duplicate names**: Multiple tasks with same name

Validation errors are logged and the scheduler will not start.

## Applying Configuration Changes

After editing `config.yaml`:

```bash
# Restart the scheduler to apply changes
make service-restart
```

The scheduler loads configuration on startup. No hot-reload is currently supported.

## Configuration Tips

### Use Comments

Document why tasks exist and what they do:

```yaml
tasks:
  # Syncs work calendar to personal calendar
  # Filters out declined events and all-day events
  # Runs every 30 minutes during work hours
  - name: calendar-sync
    # ...
```

### Group Related Tasks

Organize tasks by function or schedule:

```yaml
tasks:
  # === Hourly Tasks ===
  - name: health-check
    cron: "0 * * * *"
    # ...

  # === Daily Tasks ===
  - name: daily-backup
    cron: "0 2 * * *"
    # ...

  # === Weekly Tasks ===
  - name: weekly-report
    cron: "0 9 * * 1"
    # ...
```

### Keep Args Readable

Use one argument per line for readability:

```yaml
# Good
args:
  - "--source"
  - "~/data"
  - "--format"
  - "json"

# Less readable
args: ["--source", "~/data", "--format", "json"]
```

### Test Cron Expressions

Before deploying, verify cron expressions:

```bash
# Next 5 execution times
python -c "from apscheduler.triggers.cron import CronTrigger; \
import datetime; \
t = CronTrigger.from_crontab('*/30 * * * *'); \
for i in range(5): print(t.get_next_fire_time(None, datetime.datetime.now()))"
```

## Next Steps

- [Adding Tasks](guides/adding-tasks.md) - Create custom tasks
- [Available Tasks](tasks/index.md) - Browse existing tasks
- [Troubleshooting](troubleshooting.md) - Configuration issues
