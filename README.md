# Utility Scripts Collection

A collection of useful utility scripts for macOS/Linux automation and productivity tasks.

## Quick Start

Install all utilities at once:

```bash
make install
```

Or work with a specific utility:

```bash
cd sync-calendars
make install
make help
```

See all available commands:

```bash
make help
```

## Available Utilities

### 📅 [Calendar Sync](sync-calendars/)

Fast and efficient calendar synchronization tool using EventKit for native macOS calendar access.

[→ See full documentation](sync-calendars/README.md)

## Makefile Targets

### Global Targets (from repository root)

- `make install` - Install dependencies for ALL utilities (creates venv in each)
- `make clean` - Clean cache files from ALL utilities
- `make clean-venv` - Remove virtual environments from ALL utilities
- `make clean-all` - Deep clean (cache + venv + .idea)
- `make help` - Show all available commands and utilities

### Working with Individual Utilities

To work with a specific utility, navigate to its directory:

```bash
cd <utility-name>
make help        # See available commands
make install     # Install dependencies
make test        # Run tests (if available)
make clean       # Clean cache
```

**Example:**
```bash
cd sync-calendars
make install
make run ARGS="--days 14"
```

**Note**: Each utility uses its own isolated Python virtual environment (`.venv`) for dependency management.

## Adding New Utilities

Each utility should be contained in its own directory with:

- Main script(s)
- `README.md` with usage instructions
- `Makefile` with at least `install`, `clean`, and `help` targets

### Steps to Add a New Utility

1. Create a new directory for your utility:

   ```bash
   mkdir my-new-tool
   ```

2. Add your scripts and a `Makefile`:

   ```makefile
   .PHONY: install clean help

   install:
       # Install commands here

   clean:
       # Cleanup commands here

   help:
       @echo "My Tool - Available targets:"
       @echo "  make install    - Install dependencies"
       @echo "  make clean      - Clean cache files"
   ```

3. Update the root `Makefile`:
   - Add `my-new-tool` to the `UTILITIES` list

4. Update this README to list the new utility in the "Available Utilities" section

## Requirements

Individual utilities have additional requirements listed in their respective directories.

## License

MIT
