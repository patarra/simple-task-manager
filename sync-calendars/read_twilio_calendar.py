#!/usr/bin/env python3
"""
Fast calendar event reader and synchronization tool using EventKit.
Provides efficient calendar event querying and idempotent synchronization between calendars.
"""

import sys
import argparse
import hashlib
from datetime import datetime, timedelta

from EventKit import EKEventStore, EKEntityTypeEvent, EKEvent
from Foundation import NSDate, NSCalendar


def is_event_declined_by_user(event):
    """
    Check if the current user has declined the given event.

    Args:
        event: EKEvent object to check

    Returns:
        bool: True if the current user has declined the event, False otherwise
    """
    attendees = event.attendees()

    # If there are no attendees, the user hasn't declined (it's probably a personal event)
    if not attendees:
        return False

    # Check if the current user has declined
    for attendee in attendees:
        if attendee.isCurrentUser():
            # EKParticipantStatusDeclined = 3
            if attendee.participantStatus() == 3:
                return True
            break

    return False


def get_user_participation_status(event):
    """
    Get the current user's participation status for an event.

    Args:
        event: EKEvent object to check

    Returns:
        int: Participation status (0=Unknown, 1=Pending, 2=Accepted, 3=Declined, 4=Tentative)
    """
    attendees = event.attendees()

    # If there are no attendees, assume accepted
    if not attendees:
        return 2  # Accepted

    # Check the current user's status
    for attendee in attendees:
        if attendee.isCurrentUser():
            return attendee.participantStatus()

    # If current user not found in attendees, assume pending
    return 1  # Pending


def get_event_unique_id(event):
    """
    Generate a unique identifier for an event based on title, start, and end times.
    This is used to match events between source and destination calendars.

    Args:
        event: EKEvent object

    Returns:
        str: Unique identifier string (MD5 hash)
    """
    title = event.title() or "Untitled"
    start = event.startDate().description()
    end = event.endDate().description()
    unique_string = f"{title}|{start}|{end}"
    return hashlib.md5(unique_string.encode()).hexdigest()


def get_todays_events(calendar_name="jfelguerarodriguez@twilio.com", date_from=None, date_to=None, exclude_declined=False, exclude_all_day=False, force_sync=False, exclude_title_patterns=None, return_store=False):
    """
    Fetch events from the specified calendar within a date range.
    Much faster than AppleScript because it uses EventKit's native predicates.

    Args:
        calendar_name: Name of the calendar to query
        date_from: Start date (datetime object). If None, uses today at 00:00:00
        date_to: End date (datetime object). If None, uses tomorrow at 00:00:00
        exclude_declined: If True, exclude events where the user has declined
        exclude_all_day: If True, exclude all-day events
        force_sync: If True, force a refresh of calendar sources before fetching events
        exclude_title_patterns: List of title patterns to exclude (case-insensitive match)
        return_store: If True, return a tuple (events, store) instead of just events

    Returns:
        list or tuple: List of events, or (events, store) if return_store=True
    """
    if exclude_title_patterns is None:
        exclude_title_patterns = []
    # Create event store
    store = EKEventStore.alloc().init()

    # Request calendar access (required on macOS 10.14+)
    # Note: This will show a permission dialog on first run
    access_granted = store.requestAccessToEntityType_completion_(
        EKEntityTypeEvent, None
    )

    # Force refresh of calendar sources if requested
    if force_sync:
        print("Forcing calendar sync...")
        store.refreshSourcesIfNecessary()

    # Find the calendar
    calendars = store.calendarsForEntityType_(EKEntityTypeEvent)
    target_calendar = None

    for calendar in calendars:
        if calendar.title() == calendar_name:
            target_calendar = calendar
            break

    if not target_calendar:
        print(f"Error: Calendar '{calendar_name}' not found", file=sys.stderr)
        print(f"Available calendars:", file=sys.stderr)
        for cal in calendars:
            print(f"  - {cal.title()}", file=sys.stderr)
        sys.exit(1)

    # Define date range
    calendar_obj = NSCalendar.currentCalendar()

    if date_from is None:
        # Default: start of today
        now = NSDate.date()
        start_date = calendar_obj.startOfDayForDate_(now)
    else:
        # Convert Python datetime to NSDate
        start_date = NSDate.dateWithTimeIntervalSince1970_(date_from.timestamp())
        start_date = calendar_obj.startOfDayForDate_(start_date)

    if date_to is None:
        # Default: start of tomorrow
        end_date = calendar_obj.dateByAddingUnit_value_toDate_options_(
            16,  # NSCalendarUnitDay
            1,
            start_date,
            0
        )
    else:
        # Convert Python datetime to NSDate and go to end of that day
        end_date = NSDate.dateWithTimeIntervalSince1970_(date_to.timestamp())
        end_date = calendar_obj.startOfDayForDate_(end_date)
        # Add one day to include events on date_to
        end_date = calendar_obj.dateByAddingUnit_value_toDate_options_(
            16,  # NSCalendarUnitDay
            1,
            end_date,
            0
        )

    # Create predicate for efficient querying
    # This is the key optimization - EventKit filters at the database level
    predicate = store.predicateForEventsWithStartDate_endDate_calendars_(
        start_date,
        end_date,
        [target_calendar]
    )

    # Fetch events
    events = store.eventsMatchingPredicate_(predicate)

    # Apply filters if requested
    if not exclude_declined and not exclude_all_day and not exclude_title_patterns:
        if return_store:
            return events, store
        return events

    filtered_events = []
    for event in events:
        # Filter all-day events if requested
        if exclude_all_day and event.isAllDay():
            continue

        # Filter declined events if requested
        if exclude_declined and is_event_declined_by_user(event):
            continue

        # Filter events by title patterns if requested
        if exclude_title_patterns and event.title():
            title_lower = event.title().lower()
            # Check if any pattern matches the event title (case-insensitive)
            if any(pattern.lower() in title_lower for pattern in exclude_title_patterns):
                continue

        # Event passed all filters, include it
        filtered_events.append(event)

    if return_store:
        return filtered_events, store
    return filtered_events


def sync_events(source_events, destination_calendar_name, store):
    """
    Sync events from source to destination calendar in an idempotent way.
    - Creates events in destination that don't exist
    - Updates events that have changed
    - Deletes events in destination that are not in source

    Args:
        source_events: List of EKEvent objects from source calendar
        destination_calendar_name: Name of the destination calendar
        store: EKEventStore instance

    Returns:
        dict: Summary of sync operations (created, updated, deleted counts)
    """
    # Find the destination calendar
    calendars = store.calendarsForEntityType_(EKEntityTypeEvent)
    dest_calendar = None

    for calendar in calendars:
        if calendar.title() == destination_calendar_name:
            dest_calendar = calendar
            break

    if not dest_calendar:
        print(f"Error: Destination calendar '{destination_calendar_name}' not found", file=sys.stderr)
        print(f"Available calendars:", file=sys.stderr)
        for cal in calendars:
            print(f"  - {cal.title()}", file=sys.stderr)
        sys.exit(1)

    # Get date range covering all source events
    if not source_events:
        print("No source events to sync.")
        return {"created": 0, "updated": 0, "deleted": 0}

    # Find min and max dates from source events
    min_date = min(event.startDate() for event in source_events)
    max_date = max(event.endDate() for event in source_events)

    # Fetch existing events in destination calendar for the same date range
    predicate = store.predicateForEventsWithStartDate_endDate_calendars_(
        min_date,
        max_date,
        [dest_calendar]
    )
    dest_events = store.eventsMatchingPredicate_(predicate)

    # Create maps for efficient lookup
    # Use notes field to store source event unique ID for tracking
    source_event_map = {}
    for event in source_events:
        unique_id = get_event_unique_id(event)
        source_event_map[unique_id] = event

    dest_event_map = {}
    for event in dest_events:
        notes = event.notes() or ""
        # Extract unique_id from notes (format: "SOURCE_ID: <id>")
        if notes.startswith("SOURCE_ID: "):
            unique_id = notes.split("SOURCE_ID: ")[1].split("\n")[0].strip()
            dest_event_map[unique_id] = event

    # Track operations
    created = 0
    updated = 0
    deleted = 0

    # Create or update events
    print(f"Comparing {len(source_event_map)} source events with {len(dest_event_map)} existing events in destination...")

    for unique_id, source_event in source_event_map.items():
        if unique_id in dest_event_map:
            # Event exists, check if needs update
            dest_event = dest_event_map[unique_id]
            needs_update = False

            # Check if title, start, end, or notes have changed
            if dest_event.title() != source_event.title():
                needs_update = True
            if dest_event.startDate().description() != source_event.startDate().description():
                needs_update = True
            if dest_event.endDate().description() != source_event.endDate().description():
                needs_update = True

            if needs_update:
                # Update the event
                dest_event.setTitle_(source_event.title())
                dest_event.setStartDate_(source_event.startDate())
                dest_event.setEndDate_(source_event.endDate())
                dest_event.setLocation_(source_event.location())

                # Preserve the SOURCE_ID in notes and add description
                description = source_event.notes() or ""
                dest_event.setNotes_(f"SOURCE_ID: {unique_id}\n{description}")

                # Save the changes
                result = store.saveEvent_span_commit_error_(dest_event, 0, True, None)
                if isinstance(result, tuple):
                    success, error = result
                else:
                    success = result
                    error = None

                if success and not error:
                    updated += 1
                else:
                    print(f"Error updating event '{source_event.title()}': {error}", file=sys.stderr)
        else:
            # Create new event in destination
            new_event = EKEvent.eventWithEventStore_(store)
            new_event.setCalendar_(dest_calendar)
            new_event.setTitle_(source_event.title())
            new_event.setStartDate_(source_event.startDate())
            new_event.setEndDate_(source_event.endDate())
            new_event.setLocation_(source_event.location())
            new_event.setAllDay_(source_event.isAllDay())

            # Store the source event's unique ID in notes for tracking
            description = source_event.notes() or ""
            new_event.setNotes_(f"SOURCE_ID: {unique_id}\n{description}")

            # Get participation status and set availability accordingly
            status = get_user_participation_status(source_event)
            # EKEventAvailabilityBusy = 0, EKEventAvailabilityFree = 1
            if status == 3:  # Declined
                new_event.setAvailability_(1)  # Free
            else:
                new_event.setAvailability_(0)  # Busy

            # Save the event
            result = store.saveEvent_span_commit_error_(new_event, 0, True, None)
            # The result can be either (success, error) or just success boolean
            if isinstance(result, tuple):
                success, error = result
            else:
                success = result
                error = None

            if success and not error:
                created += 1
            else:
                print(f"Error creating event '{source_event.title()}': {error}", file=sys.stderr)

    # Delete events in destination that are not in source
    for unique_id, dest_event in dest_event_map.items():
        if unique_id not in source_event_map:
            result = store.removeEvent_span_commit_error_(dest_event, 0, True, None)
            if isinstance(result, tuple):
                success, error = result
            else:
                success = result
                error = None

            if success and not error:
                deleted += 1
            else:
                print(f"Error deleting event '{dest_event.title()}': {error}", file=sys.stderr)

    return {"created": created, "updated": updated, "deleted": deleted}


def format_event(event):
    """Format an event for display."""
    start = event.startDate()
    end = event.endDate()
    title = event.title()
    location = event.location() or "No location"

    # Convert NSDate to Python datetime for easier formatting
    start_str = start.description()
    end_str = end.description()

    return {
        'title': title,
        'start': start_str,
        'end': end_str,
        'location': location,
        'all_day': event.isAllDay()
    }


def main():
    parser = argparse.ArgumentParser(
        description='Fetch calendar events from a specified date range.'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days from today to query calendar events (default: 7)'
    )
    parser.add_argument(
        '--exclude-declined-events',
        action='store_true',
        help='Exclude events where you have declined the invitation'
    )
    parser.add_argument(
        '--exclude-all-day-events',
        action='store_true',
        help='Exclude all-day events'
    )
    parser.add_argument(
        '--force-sync',
        action='store_true',
        help='Force a refresh of calendar sources before fetching events'
    )
    parser.add_argument(
        '--exclude-title',
        type=str,
        help='Comma-separated list of title patterns to exclude (case-insensitive). Example: "Focus Time,1:1,All Hands"'
    )
    parser.add_argument(
        '--do-sync',
        type=str,
        metavar='DEST_CALENDAR',
        help='Sync filtered events to the specified destination calendar (idempotent)'
    )
    parser.add_argument(
        '--force-recreate',
        action='store_true',
        help='Force delete and recreate all events (use with --do-sync)'
    )
    parser.add_argument(
        '--source-calendar',
        '--calendar',
        type=str,
        default='jfelguerarodriguez@twilio.com',
        help='Source calendar name to sync from (default: jfelguerarodriguez@twilio.com)'
    )

    args = parser.parse_args()

    # Parse exclude_title patterns
    exclude_title_patterns = []
    if args.exclude_title:
        exclude_title_patterns = [pattern.strip() for pattern in args.exclude_title.split(',')]

    # Calculate date range
    date_from = datetime.now()
    date_to = date_from + timedelta(days=args.days)

    print(f"Fetching events from {date_from.strftime('%Y-%m-%d')} to {date_to.strftime('%Y-%m-%d')} from '{args.source_calendar}' calendar...")

    # If syncing, we need the store; otherwise just get events
    if args.do_sync:
        events, store = get_todays_events(calendar_name=args.source_calendar, date_from=date_from, date_to=date_to, exclude_declined=args.exclude_declined_events, exclude_all_day=args.exclude_all_day_events, force_sync=args.force_sync, exclude_title_patterns=exclude_title_patterns, return_store=True)
    else:
        events = get_todays_events(calendar_name=args.source_calendar, date_from=date_from, date_to=date_to, exclude_declined=args.exclude_declined_events, exclude_all_day=args.exclude_all_day_events, force_sync=args.force_sync, exclude_title_patterns=exclude_title_patterns)

    if not events or len(events) == 0:
        print("No events found in the specified date range.")
        if args.do_sync:
            print(f"Syncing to '{args.do_sync}': All events will be removed from destination.")
            sync_result = sync_events([], args.do_sync, store)
            print(f"Sync complete: {sync_result['deleted']} event(s) deleted from destination.")
        return

    print(f"\nFound {len(events)} event(s):\n")

    # Perform sync if requested
    if args.do_sync:
        print(f"\nSyncing {len(events)} event(s) to calendar '{args.do_sync}'...")
        sync_result = sync_events(events, args.do_sync, store)
        print(f"\nSync complete!")
        print(f"  Created: {sync_result['created']}")
        print(f"  Updated: {sync_result['updated']}")
        print(f"  Deleted: {sync_result['deleted']}")
        print()

    # Display events
    for event in events:
        formatted = format_event(event)
        print(f"Title: {formatted['title']}")
        print(f"Start: {formatted['start']}")
        print(f"End: {formatted['end']}")
        print(f"Location: {formatted['location']}")
        print(f"All Day: {formatted['all_day']}")
        print(f"Declined by User: {is_event_declined_by_user(event)}")
        print("-" * 50)


if __name__ == "__main__":
    main()
