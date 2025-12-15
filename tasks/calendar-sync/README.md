# Calendar Sync Tool

A fast and efficient macOS calendar synchronization tool that uses EventKit for native calendar access. This tool allows you to read events from one calendar and optionally sync them to another calendar with powerful filtering options.

## Features

- **Fast Event Querying**: Uses EventKit's native predicates for efficient database-level filtering
- **Idempotent Synchronization**: Safely sync events between calendars with automatic create/update/delete operations
- **Flexible Filtering**:
  - Exclude declined events
  - Exclude all-day events
  - Exclude events by title patterns (case-insensitive)
- **Configurable Date Range**: Query events for any number of days from today
- **Force Sync**: Force a refresh of calendar sources before fetching events

## Requirements

- macOS 10.14 or later
- Python 3.x
- PyObjC (installed via requirements.txt)

## Installation

### Using Make (Recommended)

The Makefile automatically creates and manages a virtual environment (`.venv`):

```bash
make install
```

This will:
- Create a Python virtual environment in `.venv/`
- Upgrade pip
- Install all dependencies from `requirements.txt`

On first run, macOS will prompt you to grant calendar access.

### Manual Installation (with venv)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Available Make Targets

**Installation:**
- `make install` - Create venv and install Python dependencies
- `make install-service` - Install launchd service for automatic syncing

**Running:**
- `make test` - Run a quick test (fetch next 7 days of events)
- `make run ARGS="..."` - Run with custom arguments

**Service Management:**
- `make service-start` - Start the background service
- `make service-stop` - Stop the background service
- `make service-restart` - Restart the background service
- `make service-status` - Show service status
- `make service-logs` - Show service logs
- `make uninstall-service` - Uninstall the background service

**Cleanup:**
- `make clean` - Remove Python cache files
- `make clean-venv` - Remove virtual environment
- `make help` - Show available commands

### Running with Custom Arguments

```bash
# Using make run
make run ARGS="--days 14 --exclude-declined-events"

# Or activate venv manually
source .venv/bin/activate
python read_twilio_calendar.py --days 14
```

## Automatic Background Sync (launchd Service)

The tool can run automatically in the background using macOS launchd.

### Quick Setup

```bash
# 1. Install the service
make install-service

# 2. Edit the configuration (optional)
#    File: ~/Library/LaunchAgents/com.patarra.calendar-sync.plist
#    - Change sync interval (default: 30 minutes)
#    - Change destination calendar (default: 'Personal')
#    - Modify filters

# 3. Start the service
make service-start
```

### Service Configuration

The default service configuration:
- **Runs every**: 30 minutes (1800 seconds)
- **Syncs**: Next 30 days of events
- **Filters**: Declined events and all-day events
- **Destination**: 'Personal' calendar
- **Logs**: `~/Library/Logs/calendar-sync.log`

To customize, edit: `~/Library/LaunchAgents/com.patarra.calendar-sync.plist`

### Managing the Service

```bash
# Start the service
make service-start

# Stop the service
make service-stop

# Restart after configuration changes
make service-restart

# Check if running
make service-status

# View logs
make service-logs

# Uninstall completely
make uninstall-service
```

### Service Logs

Logs are stored in:
- Standard output: `~/Library/Logs/calendar-sync.log`
- Errors: `~/Library/Logs/calendar-sync.error.log`

View the last 50 lines with `make service-logs`

## Manual Usage

### Basic Event Querying

Fetch events from the next 7 days (default):

```bash
python read_twilio_calendar.py
```

### Specify Date Range

Fetch events for the next 14 days:

```bash
python read_twilio_calendar.py --days 14
```

### Filter Declined Events

Exclude events where you've declined the invitation:

```bash
python read_twilio_calendar.py --exclude-declined-events
```

### Filter All-Day Events

Exclude all-day events:

```bash
python read_twilio_calendar.py --exclude-all-day-events
```

### Filter by Title Patterns

Exclude events matching specific title patterns (case-insensitive, comma-separated):

```bash
python read_twilio_calendar.py --exclude-title "Focus Time,1:1,All Hands"
```

### Force Calendar Sync

Force a refresh of calendar sources before fetching:

```bash
python read_twilio_calendar.py --force-sync
```

### Sync to Another Calendar

Sync filtered events to a destination calendar (idempotent):

```bash
python read_twilio_calendar.py --do-sync "My Personal Calendar"
```

### Combined Example

Fetch the next 30 days, exclude declined and all-day events, filter out "Focus Time" events, and sync to a local calendar:

```bash
python read_twilio_calendar.py \
  --days 30 \
  --exclude-declined-events \
  --exclude-all-day-events \
  --exclude-title "Focus Time" \
  --do-sync "Work Calendar Sync"
```

## How Synchronization Works

The sync operation is **idempotent**, meaning you can run it multiple times safely:

1. **Create**: Events in the source calendar that don't exist in the destination are created
2. **Update**: Events that have changed (title, time, location) are updated in the destination
3. **Delete**: Events in the destination that no longer exist in the source are removed

Events are tracked using a unique ID (MD5 hash of title + start + end time) stored in the notes field with the format `SOURCE_ID: <hash>`.

### Availability Status

When syncing events:
- **Declined events**: Marked as "Free" in the destination calendar
- **All other events**: Marked as "Busy" in the destination calendar

## Calendar Types

- **Local Calendars** (Mac only): Events appear instantly after sync
- **Remote Calendars** (iCloud, Exchange, CalDAV): May take 1-2 minutes to sync across devices

For best results when syncing to other devices, create a local calendar and enable iCloud sync in Calendar.app preferences.

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--days N` | Number of days from today to query | 7 |
| `--exclude-declined-events` | Exclude events you've declined | False |
| `--exclude-all-day-events` | Exclude all-day events | False |
| `--exclude-title PATTERNS` | Comma-separated title patterns to exclude | None |
| `--force-sync` | Force refresh of calendar sources | False |
| `--do-sync CALENDAR` | Sync to destination calendar (idempotent) | None |
| `--force-recreate` | Force recreate all events (reserved for future use) | False |

## Configuration

The default source calendar is hardcoded in the script as `jfelguerarodriguez@twilio.com`. To change this, edit the `calendar_name` parameter in the `get_todays_events()` function call within `main()`, or modify the function signature to accept it as a command-line argument.

## Troubleshooting

### Calendar Not Found

If you see "Error: Calendar 'X' not found", the script will list all available calendars. Make sure you're using the exact calendar name as it appears in Calendar.app.

### Events Not Appearing

- **Remote calendars**: Wait 1-2 minutes for sync
- **Local calendars**: Events appear instantly
- Check Calendar.app to verify the events were created

### Permission Denied

On first run, macOS will prompt you to grant calendar access. If you denied it:

1. Open System Preferences > Security & Privacy > Privacy
2. Select "Calendars" from the left sidebar
3. Grant access to Terminal or your Python interpreter

## Architecture

The tool is built using:

- **EventKit**: Apple's native calendar framework for macOS/iOS
- **Foundation**: Core macOS date/time handling (NSDate, NSCalendar)
- **PyObjC**: Python bridge to Objective-C frameworks

### Key Functions

- `get_todays_events()`: Query events with filters
- `sync_events()`: Idempotent synchronization
- `is_event_declined_by_user()`: Check user's participation status
- `get_event_unique_id()`: Generate tracking hash for events

## License

MIT
