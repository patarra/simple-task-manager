# Calendar Sync

Fast macOS calendar synchronization tool using EventKit for native calendar access.

!!! warning "macOS Only"
This task requires macOS 10.14+ and the EventKit framework. It will not work on Linux.

## Features

- **Fast Event Querying**: Uses EventKit's native predicates for efficient database-level filtering
- **Idempotent Synchronization**: Safely sync events between calendars with automatic create/update/delete
- **Flexible Filtering**:
  - Exclude declined events
  - Exclude all-day events
  - Exclude events by title patterns (case-insensitive)
- **Configurable Date Range**: Query events for any number of days from today
- **Force Sync**: Force a refresh of calendar sources before fetching

## Requirements

- macOS 10.14 (Mojave) or later
- Python 3.7+
- PyObjC (automatically installed)
- Calendar access permission (prompted on first run)

## Configuration

Add to `config.yaml`:

```yaml
tasks:
  - name: calendar-sync
    path: tasks/calendar-sync
    cron: "*/30 * * * *" # Every 30 minutes
    args:
      - "--source-calendar"
      - "work@company.com"
      - "--days"
      - "30"
      - "--exclude-declined-events"
      - "--exclude-all-day-events"
      - "--exclude-title"
      - "Focus Time,1:1"
      - "--do-sync"
      - "Personal"
    timeout: 600
    enabled: true
```

## Arguments

### `--source-calendar NAME`

Source calendar name to read events from.

**Default:** `Personal`

### `--days N`

Number of days from today to sync.

**Default:** `7`
**Example:** `--days 30` syncs next 30 days

### `--exclude-declined-events`

Exclude events where you've declined the invitation.

**Flag**: No value needed

### `--exclude-all-day-events`

Exclude all-day events from synchronization.

**Flag**: No value needed

### `--exclude-title PATTERNS`

Comma-separated list of title patterns to exclude (case-insensitive).

**Example:** `--exclude-title "Focus Time,1:1,All Hands"`

### `--force-sync`

Force a refresh of calendar sources before fetching events.

**Flag**: No value needed

### `--do-sync CALENDAR`

Destination calendar name. If specified, performs synchronization.

**Example:** `--do-sync "Personal"`

Without this flag, the task only lists events without syncing.

## How Synchronization Works

The sync operation is **idempotent** (safe to run multiple times):

1. **Create**: Events in source that don't exist in destination are created
2. **Update**: Events that changed (title, time, location) are updated
3. **Delete**: Events in destination that no longer exist in source are removed

Events are tracked using a unique ID (MD5 hash of title + start + end time) stored in the notes field.

### Availability Status

When syncing events:

- **Declined events**: Marked as "Free" in destination
- **All other events**: Marked as "Busy" in destination

## Examples

### Basic Query

List events from default calendar for next 7 days:

```bash
cd tasks/calendar-sync
./run.sh --days 7
```

### Sync with Filtering

Sync next 30 days, excluding declined and all-day events:

```yaml
args:
  - "--source-calendar"
  - "work@company.com"
  - "--days"
  - "30"
  - "--exclude-declined-events"
  - "--exclude-all-day-events"
  - "--do-sync"
  - "Personal"
```

### Exclude Specific Events

Filter out "Focus Time" and "1:1" meetings:

```yaml
args:
  - "--exclude-title"
  - "Focus Time,1:1"
  - "--do-sync"
  - "Personal"
```

### Manual Testing

```bash
cd tasks/calendar-sync
./run.sh \
  --source-calendar "work@company.com" \
  --days 14 \
  --exclude-declined-events \
  --do-sync "Personal"
```

## Calendar Types

- **Local Calendars** (Mac only): Events appear instantly after sync
- **Remote Calendars** (iCloud, Exchange, CalDAV): May take 1-2 minutes to sync across devices

For best results syncing to other devices, create a local calendar and enable iCloud sync in Calendar.app preferences.

## Permissions

On first run, macOS will prompt:

```
"Terminal" would like to access your calendar.
```

Click **OK** to grant access.

### If Access Was Denied

1. Open **System Preferences** → **Security & Privacy**
2. Select **Privacy** tab
3. Select **Calendars** from left sidebar
4. Check box next to **Terminal** or **Python**

## Troubleshooting

### Calendar Not Found

If you see "Calendar 'X' not found", the script lists all available calendars.

Make sure you're using the exact name as it appears in Calendar.app.

### Events Not Appearing

**Remote calendars**: Wait 1-2 minutes for sync
**Local calendars**: Events appear instantly

Check Calendar.app to verify events were created.

### Permission Denied

Grant calendar access in System Preferences → Security & Privacy → Privacy → Calendars.

### Sync Conflicts

The sync is idempotent and uses unique IDs. Conflicts are resolved by:

- Most recent data wins for updates
- Source of truth is the source calendar

## Implementation Details

Built using:

- **EventKit**: Apple's native calendar framework
- **Foundation**: Core macOS date/time handling
- **PyObjC**: Python bridge to Objective-C frameworks

### Key Functions

- `get_todays_events()`: Query events with filters
- `sync_events()`: Idempotent synchronization
- `is_event_declined_by_user()`: Check participation status
- `get_event_unique_id()`: Generate tracking hash

## Advanced Usage

### Dry Run (List Only)

Omit `--do-sync` to see what would be synced:

```bash
./run.sh --source-calendar "work@company.com" --days 30
```

### Multiple Sync Jobs

Run different sync configs for different calendars:

```yaml
tasks:
  - name: work-to-personal
    path: tasks/calendar-sync
    cron: "*/30 * * * *"
    args: ["--source-calendar", "work@company.com", "--do-sync", "Personal"]
    enabled: true

  - name: personal-to-shared
    path: tasks/calendar-sync
    cron: "0 * * * *"
    args: ["--source-calendar", "Personal", "--do-sync", "Family"]
    enabled: true
```

## Source Code

See `tasks/calendar-sync/` for implementation:

- `sync-calendar.py` - Main sync script
- `run.sh` - Entry point

## Related

- [Adding Tasks](../guides/adding-tasks.md) - Create your own tasks
- [Configuration Reference](../configuration.md) - Task configuration
- [Troubleshooting](../troubleshooting.md) - Common issues
