.PHONY: install test clean clean-venv help run install-service uninstall-service service-start service-stop service-restart service-status service-logs

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
$(VENV)/bin/activate:
	@echo "Creating virtual environment..."
	@python3 -m venv $(VENV)
	@echo "$(GREEN)✓ Virtual environment created$(RESET)"

# Main install target - installs deps only
# Note: This task is now managed by the central scheduler
install:
	@if [ "$(UNAME_S)" != "Darwin" ]; then \
		echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"; \
		echo "$(YELLOW)⚠️  SKIPPING: calendar-sync (macOS only)$(RESET)"; \
		echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"; \
		echo "$(YELLOW)   Current OS: $(UNAME_S)$(RESET)"; \
		echo "$(YELLOW)   This task requires EventKit framework (macOS only)$(RESET)"; \
		echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"; \
		echo ""; \
	else \
		$(MAKE) $(VENV)/bin/activate; \
		echo "$(CYAN)Installing Calendar Sync dependencies...$(RESET)"; \
		$(PIP) install --upgrade pip > /dev/null; \
		$(PIP) install -r requirements.txt; \
		echo "$(GREEN)✓ Calendar Sync dependencies installed$(RESET)"; \
	fi

test: install
	@if [ "$(UNAME_S)" != "Darwin" ]; then \
		echo "$(RED)ERROR: This task only works on macOS$(RESET)"; \
		exit 1; \
	fi
	@echo "Testing Calendar Sync (fetching next 7 days)..."
	@$(PYTHON) read_twilio_calendar.py --days 7

run: install
	@if [ "$(UNAME_S)" != "Darwin" ]; then \
		echo "$(RED)ERROR: This task only works on macOS$(RESET)"; \
		exit 1; \
	fi
	@echo "Running Calendar Sync..."
	@$(PYTHON) read_twilio_calendar.py $(ARGS)

# Start the service (deprecated - use central scheduler)
service-start:
	@echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo "$(YELLOW)⚠️  DEPRECATED: This task is now managed by the central scheduler$(RESET)"
	@echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo ""
	@echo "Use these commands from the repository root:"
	@echo "  $(CYAN)make install-service$(RESET)  # Install scheduler service"
	@echo "  $(CYAN)make service-start$(RESET)    # Start scheduler"

# Stop the service (deprecated - use central scheduler)
service-stop:
	@echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo "$(YELLOW)⚠️  DEPRECATED: This task is now managed by the central scheduler$(RESET)"
	@echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo ""
	@echo "Use: $(CYAN)make service-stop$(RESET) (from repository root)"

# Restart the service (deprecated - use central scheduler)
service-restart:
	@echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo "$(YELLOW)⚠️  DEPRECATED: This task is now managed by the central scheduler$(RESET)"
	@echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo ""
	@echo "Use: $(CYAN)make service-restart$(RESET) (from repository root)"

# Show service status (deprecated - use central scheduler)
service-status:
	@echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo "$(YELLOW)⚠️  DEPRECATED: This task is now managed by the central scheduler$(RESET)"
	@echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo ""
	@echo "Use: $(CYAN)make service-status$(RESET) (from repository root)"

# Show service logs (deprecated - use central scheduler)
service-logs:
	@echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo "$(YELLOW)⚠️  DEPRECATED: This task is now managed by the central scheduler$(RESET)"
	@echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo ""
	@echo "Use: $(CYAN)make service-logs$(RESET) (from repository root)"

# Uninstall the service (deprecated - use central scheduler)
uninstall-service:
	@echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo "$(YELLOW)⚠️  DEPRECATED: This task is now managed by the central scheduler$(RESET)"
	@echo "$(YELLOW)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo ""
	@echo "Use: $(CYAN)make uninstall-service$(RESET) (from repository root)"

clean:
	@echo "Cleaning Python cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned$(RESET)"

clean-venv:
	@echo "Removing virtual environment..."
	@rm -rf $(VENV)
	@echo "$(GREEN)✓ Virtual environment removed$(RESET)"
