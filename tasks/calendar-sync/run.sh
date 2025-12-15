#!/bin/bash
set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate Python virtual environment
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
else
    echo "Error: Virtual environment not found. Run 'make install' first." >&2
    exit 1
fi

# Execute the calendar sync script with all arguments
python "$SCRIPT_DIR/sync-calendar.py" "$@"
