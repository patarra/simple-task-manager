.PHONY: install test clean clean-venv help run check-os install-service uninstall-service service-start service-stop service-restart service-status service-logs

# Detect OS
UNAME_S := $(shell uname -s)

# Colors
YELLOW := \033[0;33m
RED := \033[0;31m
GREEN := \033[0;32m
CYAN := \033[0;36m
RESET := \033[0m

# Virtual environment settings
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Service settings
SERVICE_NAME := com.patarra.calendar-sync
PLIST_TEMPLATE := $(SERVICE_NAME).plist.template
PLIST_FILE := $(SERVICE_NAME).plist
LAUNCH_AGENTS_DIR := $(HOME)/Library/LaunchAgents
PLIST_PATH := $(LAUNCH_AGENTS_DIR)/$(PLIST_FILE)
SCRIPT_DIR := $(shell pwd)

# Check if running on macOS (warning only, doesn't fail)
check-os:
	@if [ "$(UNAME_S)" != "Darwin" ]; then \
		echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"; \
		echo "$(YELLOW)⚠️  WARNING: This tool is designed for macOS only!$(RESET)"; \
		echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"; \
		echo "$(RED)   Current OS: $(UNAME_S)$(RESET)"; \
		echo "$(YELLOW)   This tool requires EventKit framework (macOS only).$(RESET)"; \
		echo "$(YELLOW)   Installation will proceed, but the script will NOT work.$(RESET)"; \
		echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"; \
		echo ""; \
	fi

help:
	@echo "$(CYAN)Calendar Sync Tool - Available targets:$(RESET)"
	@echo ""
	@echo "$(GREEN)Installation:$(RESET)"
	@echo "  make install              - Create venv, install dependencies, and setup service"
	@echo ""
	@echo "$(GREEN)Running:$(RESET)"
	@echo "  make test                 - Run the script with default parameters (7 days)"
	@echo "  make run ARGS=...         - Run the script with custom arguments"
	@echo ""
	@echo "$(GREEN)Service Management:$(RESET)"
	@echo "  make service-start        - Start the background service"
	@echo "  make service-stop         - Stop the background service"
	@echo "  make service-restart      - Restart the background service"
	@echo "  make service-status       - Show service status"
	@echo "  make service-logs         - Show service logs"
	@echo "  make uninstall-service    - Uninstall the background service"
	@echo ""
	@echo "$(GREEN)Cleanup:$(RESET)"
	@echo "  make clean                - Remove Python cache files"
	@echo "  make clean-venv           - Remove virtual environment"
	@echo ""
	@echo "$(YELLOW)Note: This tool only works on macOS (requires EventKit framework)$(RESET)"
	@echo ""
	@echo "Example usage:"
	@echo "  make run ARGS='--days 14 --exclude-declined-events'"

# Create virtual environment if it doesn't exist
$(VENV)/bin/activate: check-os
	@echo "Creating virtual environment..."
	@python3 -m venv $(VENV)
	@echo "$(GREEN)✓ Virtual environment created$(RESET)"

# Main install target - installs deps and service
install: $(VENV)/bin/activate
	@echo "$(CYAN)Installing Calendar Sync...$(RESET)"
	@echo ""
	@echo "Installing dependencies..."
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed successfully$(RESET)"
	@echo ""
	@if [ "$(UNAME_S)" = "Darwin" ]; then \
		echo "$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"; \
		echo "$(CYAN)Setting up automatic background sync service...$(RESET)"; \
		echo "$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"; \
		echo ""; \
		$(MAKE) install-service-interactive; \
	else \
		echo "$(YELLOW)Skipping service installation (macOS only)$(RESET)"; \
	fi

# Interactive service installation
install-service-interactive:
	@echo "$(GREEN)Configure the automatic sync service:$(RESET)"
	@echo ""
	@echo "$(YELLOW)Available calendars:$(RESET)"
	@$(PYTHON) list_calendars.py | sed 's/^/  - /'
	@echo ""
	@read -p "$(CYAN)Source calendar name? $(RESET)[default: jfelguerarodriguez@twilio.com]: " SOURCE_CAL; \
	SOURCE_CAL=$${SOURCE_CAL:-jfelguerarodriguez@twilio.com}; \
	echo ""; \
	read -p "$(CYAN)Destination calendar name? $(RESET)[default: Personal]: " DEST_CAL; \
	DEST_CAL=$${DEST_CAL:-Personal}; \
	echo ""; \
	read -p "$(CYAN)How many days to sync? $(RESET)[default: 30]: " DAYS; \
	DAYS=$${DAYS:-30}; \
	echo ""; \
	read -p "$(CYAN)Exclude declined events? $(RESET)[Y/n]: " EXCLUDE_DECLINED; \
	EXCLUDE_DECLINED=$${EXCLUDE_DECLINED:-Y}; \
	echo ""; \
	read -p "$(CYAN)Exclude all-day events? $(RESET)[Y/n]: " EXCLUDE_ALLDAY; \
	EXCLUDE_ALLDAY=$${EXCLUDE_ALLDAY:-Y}; \
	echo ""; \
	read -p "$(CYAN)Sync interval in minutes? $(RESET)[default: 30]: " INTERVAL; \
	INTERVAL=$${INTERVAL:-30}; \
	INTERVAL_SECONDS=$$((INTERVAL * 60)); \
	echo ""; \
	echo "$(YELLOW)Creating service configuration...$(RESET)"; \
	mkdir -p $(LAUNCH_AGENTS_DIR); \
	ARGS_ARRAY="        <string>$(SCRIPT_DIR)/$(VENV)/bin/python</string>\n        <string>$(SCRIPT_DIR)/read_twilio_calendar.py</string>\n        <string>--source-calendar</string>\n        <string>$$SOURCE_CAL</string>\n        <string>--days</string>\n        <string>$$DAYS</string>"; \
	if [ "$$EXCLUDE_DECLINED" = "Y" ] || [ "$$EXCLUDE_DECLINED" = "y" ]; then \
		ARGS_ARRAY="$$ARGS_ARRAY\n        <string>--exclude-declined-events</string>"; \
	fi; \
	if [ "$$EXCLUDE_ALLDAY" = "Y" ] || [ "$$EXCLUDE_ALLDAY" = "y" ]; then \
		ARGS_ARRAY="$$ARGS_ARRAY\n        <string>--exclude-all-day-events</string>"; \
	fi; \
	ARGS_ARRAY="$$ARGS_ARRAY\n        <string>--do-sync</string>\n        <string>$$DEST_CAL</string>"; \
	printf '<?xml version="1.0" encoding="UTF-8"?>\n' > $(PLIST_PATH); \
	printf '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n' >> $(PLIST_PATH); \
	printf '<plist version="1.0">\n' >> $(PLIST_PATH); \
	printf '<dict>\n' >> $(PLIST_PATH); \
	printf '    <key>Label</key>\n' >> $(PLIST_PATH); \
	printf '    <string>$(SERVICE_NAME)</string>\n\n' >> $(PLIST_PATH); \
	printf '    <key>ProgramArguments</key>\n' >> $(PLIST_PATH); \
	printf '    <array>\n' >> $(PLIST_PATH); \
	printf "$$ARGS_ARRAY\n" >> $(PLIST_PATH); \
	printf '    </array>\n\n' >> $(PLIST_PATH); \
	printf '    <key>WorkingDirectory</key>\n' >> $(PLIST_PATH); \
	printf '    <string>$(SCRIPT_DIR)</string>\n\n' >> $(PLIST_PATH); \
	printf '    <key>StandardOutPath</key>\n' >> $(PLIST_PATH); \
	printf '    <string>$(HOME)/Library/Logs/calendar-sync.log</string>\n\n' >> $(PLIST_PATH); \
	printf '    <key>StandardErrorPath</key>\n' >> $(PLIST_PATH); \
	printf '    <string>$(HOME)/Library/Logs/calendar-sync.error.log</string>\n\n' >> $(PLIST_PATH); \
	printf '    <key>StartInterval</key>\n' >> $(PLIST_PATH); \
	printf '    <integer>%s</integer>\n\n' "$$INTERVAL_SECONDS" >> $(PLIST_PATH); \
	printf '    <key>RunAtLoad</key>\n' >> $(PLIST_PATH); \
	printf '    <true/>\n\n' >> $(PLIST_PATH); \
	printf '    <key>KeepAlive</key>\n' >> $(PLIST_PATH); \
	printf '    <false/>\n\n' >> $(PLIST_PATH); \
	printf '    <key>ProcessType</key>\n' >> $(PLIST_PATH); \
	printf '    <string>Background</string>\n' >> $(PLIST_PATH); \
	printf '</dict>\n' >> $(PLIST_PATH); \
	printf '</plist>\n' >> $(PLIST_PATH); \
	echo "$(GREEN)✓ Service configured$(RESET)"; \
	echo ""; \
	echo "$(GREEN)Configuration summary:$(RESET)"; \
	echo "  Source calendar: $$SOURCE_CAL"; \
	echo "  Destination calendar: $$DEST_CAL"; \
	echo "  Days to sync: $$DAYS"; \
	echo "  Exclude declined: $$EXCLUDE_DECLINED"; \
	echo "  Exclude all-day: $$EXCLUDE_ALLDAY"; \
	echo "  Sync interval: $$INTERVAL minutes"; \
	echo ""; \
	echo "$(GREEN)Service will start automatically on next login.$(RESET)"; \
	echo "To start it now, run: $(CYAN)make service-start$(RESET)"; \
	echo "To view status: $(CYAN)make service-status$(RESET)"; \
	echo "To view logs: $(CYAN)make service-logs$(RESET)"; \
	echo ""

test: check-os install
	@echo "Testing Calendar Sync (fetching next 7 days)..."
	@$(PYTHON) read_twilio_calendar.py --days 7

run: check-os install
	@echo "Running Calendar Sync..."
	@$(PYTHON) read_twilio_calendar.py $(ARGS)

# Start the service
service-start: check-os
	@echo "$(CYAN)Starting Calendar Sync service...$(RESET)"
	@if [ ! -f "$(PLIST_PATH)" ]; then \
		echo "$(RED)ERROR: Service not installed. Run 'make install' first.$(RESET)"; \
		exit 1; \
	fi
	@launchctl load $(PLIST_PATH) 2>/dev/null || true
	@launchctl start $(SERVICE_NAME)
	@echo "$(GREEN)✓ Service started$(RESET)"
	@echo ""
	@echo "Check status with: make service-status"
	@echo "View logs with: make service-logs"

# Stop the service
service-stop: check-os
	@echo "$(CYAN)Stopping Calendar Sync service...$(RESET)"
	@launchctl stop $(SERVICE_NAME) 2>/dev/null || true
	@launchctl unload $(PLIST_PATH) 2>/dev/null || true
	@echo "$(GREEN)✓ Service stopped$(RESET)"

# Restart the service
service-restart: service-stop service-start

# Show service status
service-status: check-os
	@echo "$(CYAN)Calendar Sync Service Status:$(RESET)"
	@echo ""
	@launchctl list | grep $(SERVICE_NAME) || echo "$(YELLOW)Service is not running$(RESET)"
	@echo ""
	@if [ -f "$(PLIST_PATH)" ]; then \
		echo "$(GREEN)Service configuration: $(PLIST_PATH)$(RESET)"; \
	else \
		echo "$(RED)Service not installed$(RESET)"; \
	fi

# Show service logs
service-logs: check-os
	@echo "$(CYAN)Calendar Sync Service Logs:$(RESET)"
	@echo ""
	@if [ -f "$(HOME)/Library/Logs/calendar-sync.log" ]; then \
		echo "$(GREEN)=== Standard Output ===$(RESET)"; \
		tail -50 $(HOME)/Library/Logs/calendar-sync.log; \
		echo ""; \
	else \
		echo "$(YELLOW)No standard output log found$(RESET)"; \
	fi
	@if [ -f "$(HOME)/Library/Logs/calendar-sync.error.log" ]; then \
		echo "$(RED)=== Error Output ===$(RESET)"; \
		tail -50 $(HOME)/Library/Logs/calendar-sync.error.log; \
	else \
		echo "$(GREEN)No errors logged$(RESET)"; \
	fi

# Uninstall the service
uninstall-service: service-stop
	@echo "$(CYAN)Uninstalling Calendar Sync service...$(RESET)"
	@rm -f $(PLIST_PATH)
	@echo "$(GREEN)✓ Service uninstalled$(RESET)"
	@echo ""
	@echo "Logs are still available at:"
	@echo "  $(HOME)/Library/Logs/calendar-sync.log"
	@echo "  $(HOME)/Library/Logs/calendar-sync.error.log"

clean:
	@echo "Cleaning Python cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned$(RESET)"

clean-venv:
	@echo "Removing virtual environment..."
	@rm -rf $(VENV)
	@echo "$(GREEN)✓ Virtual environment removed$(RESET)"
