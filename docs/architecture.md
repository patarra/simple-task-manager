# Architecture

Understanding how Simple Task Manager works.

## System Overview

Simple Task Manager consists of three main components:

1. **Scheduler Daemon** - Python process using APScheduler
2. **Tasks** - Independent scripts with `run.sh` interface
3. **Configuration** - Single YAML file defining tasks and schedules

```
┌─────────────────────────────────────────────────┐
│  OS Service Manager (launchd/systemd)           │
│  Keeps scheduler daemon running                 │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Scheduler Daemon (scheduler.py)                │
│  - Reads config.yaml                            │
│  - Registers cron jobs with APScheduler         │
│  - Executes tasks via run.sh                    │
│  - Captures output and logs execution           │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
   ┌─────────┐       ┌─────────┐
   │ Task 1  │       │ Task 2  │
   │ run.sh  │       │ run.sh  │
   └─────────┘       └─────────┘
```

## Components

### 1. Scheduler Daemon

**Location:** `scheduler/scheduler.py`

**Responsibilities:**
- Load and validate `config.yaml`
- Register cron jobs with APScheduler
- Execute tasks at scheduled times
- Capture stdout/stderr
- Log execution results
- Handle timeouts
- Restart failed tasks (handled by OS service manager)

**Lifecycle:**

1. **Startup:**
   - Read `config.yaml`
   - Validate each enabled task
   - Register cron jobs
   - Start APScheduler

2. **Execution:**
   - APScheduler triggers job
   - Change to task directory
   - Execute `./run.sh [args...]` with timeout
   - Capture output
   - Log results

3. **Shutdown:**
   - Graceful shutdown on SIGTERM
   - Wait for running tasks to complete (or timeout)

### 2. Tasks

**Location:** `tasks/*/`

**Structure:**
```
tasks/task-name/
├── run.sh              # Entry point (required)
├── Makefile            # Build commands (required)
├── requirements.txt    # Dependencies (Python)
├── go.mod              # Dependencies (Go)
├── .venv/              # Virtual environment
└── [implementation]    # Task code
```

**Lifecycle:**

1. **Installation:** `make install`
   - Create virtual environment
   - Install dependencies
   - Build binaries if needed

2. **Execution:** Scheduler runs `./run.sh`
   - Activate environment
   - Run task with arguments
   - Return exit code

3. **Cleanup:** `make clean`
   - Remove cache files
   - Clean build artifacts

### 3. Configuration

**Location:** `config.yaml` (repository root)

**Schema:**
```yaml
scheduler:
  log_file: <path>
  default_timeout: <seconds>

tasks:
  - name: <string>
    path: <string>
    cron: <string>
    args: [<strings>]
    timeout: <int>
    enabled: <bool>
```

**Loading:** Read once at scheduler startup

**Validation:** Performed before registering tasks

## Design Principles

### Decoupling

**Scheduler knows:**
- Task name
- Task path
- Arguments to pass
- When to run

**Scheduler doesn't know:**
- Implementation language
- Dependencies
- Internal logic

**Benefits:**
- Tasks can be written in any language
- Task changes don't affect scheduler
- Easy to add new tasks

### Isolation

Each task has:
- Own directory
- Own dependencies (venv, go.mod, etc.)
- Own build process

**Benefits:**
- No dependency conflicts
- Independent upgrades
- Parallel development

### Simplicity

**Single interface:** Every task exposes `run.sh`

**Single config:** All scheduling in one YAML file

**Single log:** All executions in one place

**Benefits:**
- Easy to understand
- Easy to debug
- Easy to maintain

## Data Flow

### Task Execution Flow

```
1. APScheduler triggers job at cron time
   ↓
2. Scheduler logs: "Executing 'task-name' with args [...]"
   ↓
3. Change directory: cd tasks/task-name
   ↓
4. Execute: timeout <seconds> ./run.sh <args...>
   ↓
5. Capture stdout/stderr in real-time
   ↓
6. Task completes (or times out)
   ↓
7. Log exit code and duration
   ↓
8. Write captured output to log with [task-name] prefix
```

### Example Log Output

```
[2025-12-15 10:00:00] INFO: Executing 'calendar-sync' with args ['--days', '30']
[2025-12-15 10:00:15] INFO: Task 'calendar-sync' completed in 15.2s (exit code: 0)
[2025-12-15 10:00:15] [calendar-sync] STDOUT: Fetching events...
[2025-12-15 10:00:15] [calendar-sync] STDOUT: Sync complete: Created: 3
```

## Service Integration

### macOS (launchd)

**Service File:** `~/Library/LaunchAgents/com.patarra.scheduler.plist`

**Responsibilities:**
- Start scheduler at login (`RunAtLoad`)
- Keep scheduler running (`KeepAlive`)
- Restart on crash
- Redirect logs to files

**Process Supervision:**
```
launchd
  └─> scheduler.py (kept alive)
        ├─> task1 (spawned as needed)
        └─> task2 (spawned as needed)
```

### Linux (systemd)

**Service File:** `~/.config/systemd/user/scheduler.service`

**Responsibilities:**
- Start scheduler as user service
- Restart on failure (`Restart=on-failure`)
- Redirect logs to files
- Optionally run without login (lingering)

**Process Supervision:**
```
systemd (user)
  └─> scheduler.py (Type=simple)
        ├─> task1 (spawned as needed)
        └─> task2 (spawned as needed)
```

## Error Handling

### Task Failures

**Exit code != 0:**
- Logged as ERROR
- Scheduler continues running
- Next scheduled execution proceeds normally

**Timeout:**
- Process killed with SIGTERM
- Logged as ERROR with timeout duration
- Next execution proceeds

**Exception in scheduler:**
- Logged with traceback
- Scheduler continues for other tasks
- Failed task skipped for this run

### Scheduler Crashes

**macOS (launchd):**
- Automatically restarted by launchd
- `KeepAlive: true` ensures restart

**Linux (systemd):**
- Automatically restarted by systemd
- `Restart=on-failure` with `RestartSec=10`

### Configuration Errors

**On startup:**
- Invalid YAML: Scheduler exits with error
- Missing required fields: Task skipped, warning logged
- Invalid cron: Task skipped, error logged
- Missing run.sh: Task skipped, error logged

## Concurrency

### Task Execution

Tasks execute in parallel:
- Each task runs in its own process
- Multiple tasks can run simultaneously
- No shared state between tasks

### Scheduler Threading

APScheduler uses:
- Thread pool for job execution
- Single thread per job
- No lock contention between tasks

## Security Considerations

### File Permissions

**Service files:**
- `chmod 644` for plist/service files
- Owned by user

**Task scripts:**
- `chmod 755` for run.sh (executable)
- Owned by user

### Secrets Management

**Don't commit secrets:**
- Add to `.gitignore`
- Use environment variables
- Use OS keychain/keyring

**Example:**
```bash
# In run.sh
export API_KEY=$(security find-generic-password -a $USER -s my-task -w)
python main.py "$@"
```

### Isolation

Tasks run as your user:
- Same permissions as your shell
- Can access files you can access
- No privilege escalation

## Extensibility

### Adding New Features

**Scheduler enhancements:**
- Edit `scheduler/scheduler.py`
- Update `config.yaml` schema
- Document in configuration reference

**Task features:**
- Implement in task itself
- No scheduler changes needed
- Just add args to config

### Plugin System (Future)

Potential extensions:
- Pre-execution hooks
- Post-execution hooks
- Notification integrations
- Metrics collection

## Performance

### Scheduler Overhead

**Minimal:**
- ~20MB RAM for scheduler daemon
- ~1-5% CPU during task execution
- ~0% CPU when idle

**Task overhead:**
- Depends on task implementation
- Python venv activation: ~100ms
- Process spawn: ~50ms

### Scalability

**Current:**
- Designed for personal use (5-20 tasks)
- All tasks on same machine

**Limitations:**
- Single scheduler process
- No distributed execution
- No task dependencies

**If you need more:**
- Consider Apache Airflow
- Consider Prefect
- Consider Temporal

## Design Decisions

### Why APScheduler?

**Pros:**
- Python-native
- Cron support
- Simple API
- No external dependencies

**Alternatives considered:**
- `schedule` library: Less feature-rich
- Celery: Too complex for this use case
- Pure cron: Permission issues on modern macOS

### Why `run.sh` Interface?

**Pros:**
- Language-agnostic
- Simple contract
- Easy to test manually
- Standard Unix pattern

**Alternatives considered:**
- Python imports: Couples to Python
- JSON-RPC: Too complex
- REST API: Unnecessary overhead

### Why Single Config File?

**Pros:**
- One place to understand all tasks
- Easy to backup/version
- Simple to edit

**Alternatives considered:**
- Per-task configs: Harder to see big picture
- Database: Overkill for personal use
- Environment variables: Hard to manage

## Next Steps

- [Configuration Reference](configuration.md) - Detailed config
- [Adding Tasks](guides/adding-tasks.md) - Create tasks
- [Troubleshooting](troubleshooting.md) - Debug issues
