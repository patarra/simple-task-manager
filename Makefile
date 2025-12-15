.PHONY: install clean clean-venv clean-all help install-service uninstall-service service-start service-stop service-restart service-status service-logs test-scheduler

# Color output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
RESET := \033[0m

# Detect OS
UNAME_S := $(shell uname -s)

# List of all tasks (subdirectories in tasks/)
TASKS := calendar-sync

# Service settings (OS-specific)
ifeq ($(UNAME_S),Darwin)
	# macOS: launchd
	SERVICE_NAME := com.patarra.scheduler
	SERVICE_FILE := $(SERVICE_NAME).plist
	SERVICE_DIR := $(HOME)/Library/LaunchAgents
	SERVICE_PATH := $(SERVICE_DIR)/$(SERVICE_FILE)
	LOG_DIR := $(HOME)/Library/Logs
else
	# Linux: systemd user service
	SERVICE_NAME := scheduler
	SERVICE_FILE := $(SERVICE_NAME).service
	SERVICE_DIR := $(HOME)/.config/systemd/user
	SERVICE_PATH := $(SERVICE_DIR)/$(SERVICE_FILE)
	LOG_DIR := $(HOME)/.local/share/scheduler/logs
endif

REPO_ROOT := $(shell pwd)

help:
	@echo "$(CYAN)Task Scheduler$(RESET)"
	@echo ""
	@echo "$(YELLOW)Detected OS: $(UNAME_S)$(RESET)"
ifeq ($(UNAME_S),Darwin)
	@echo "$(YELLOW)Service type: launchd$(RESET)"
else
	@echo "$(YELLOW)Service type: systemd (user)$(RESET)"
endif
	@echo ""
	@echo "$(GREEN)Installation:$(RESET)"
	@echo "  make install              - Install scheduler + all tasks"
	@echo "  make install-service      - Install system service"
	@echo ""
	@echo "$(GREEN)Service Management:$(RESET)"
	@echo "  make service-start        - Start the scheduler daemon"
	@echo "  make service-stop         - Stop the scheduler daemon"
	@echo "  make service-restart      - Restart the scheduler daemon"
	@echo "  make service-status       - Show scheduler status"
	@echo "  make service-logs         - Show scheduler logs"
	@echo "  make uninstall-service    - Uninstall the scheduler service"
	@echo ""
	@echo "$(GREEN)Testing:$(RESET)"
	@echo "  make test-scheduler       - Test scheduler locally (no service)"
	@echo ""
	@echo "$(GREEN)Cleanup:$(RESET)"
	@echo "  make clean                - Clean cache files"
	@echo "  make clean-venv           - Remove all virtual environments"
	@echo "  make clean-all            - Deep clean (cache + venv + .idea)"
	@echo ""
	@echo "$(YELLOW)Available tasks:$(RESET)"
	@for task in $(TASKS); do \
		if [ -d tasks/$$task ]; then \
			echo "  📦 tasks/$$task/"; \
		fi; \
	done
	@echo ""
	@echo "$(YELLOW)Configuration:$(RESET)"
	@echo "  Create a config.yaml (you can use config.yaml.example) to add/modify tasks"

# Install scheduler and all tasks
install:
	@echo "$(CYAN)Installing task scheduler...$(RESET)"
	@echo ""
	@echo "$(GREEN)Installing scheduler daemon...$(RESET)"
	@$(MAKE) -C scheduler install
	@echo ""
	@echo "$(GREEN)Installing tasks...$(RESET)"
	@for task in $(TASKS); do \
		if [ -d tasks/$$task ] && [ -f tasks/$$task/Makefile ]; then \
			echo "$(CYAN)Installing $$task...$(RESET)"; \
			$(MAKE) -C tasks/$$task install; \
		fi; \
	done
	@echo ""
	@echo "$(GREEN)✓ Installation complete$(RESET)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit config.yaml to configure tasks"
	@echo "  2. Run: make install-service"
	@echo "  3. Run: make service-start"

# Generate and install service (macOS launchd or Linux systemd)
install-service:
	@echo "$(CYAN)Installing scheduler service for $(UNAME_S)...$(RESET)"
	@mkdir -p $(SERVICE_DIR)
	@mkdir -p $(LOG_DIR)
ifeq ($(UNAME_S),Darwin)
	@echo "$(YELLOW)Creating launchd plist from template...$(RESET)"
	@sed -e 's|{{REPO_ROOT}}|$(REPO_ROOT)|g' \
	     -e 's|{{LOG_DIR}}|$(LOG_DIR)|g' \
	     scheduler/config/scheduler.plist.template > $(SERVICE_PATH)
	@echo "$(GREEN)✓ Service installed: $(SERVICE_PATH)$(RESET)"
	@echo "To start: $(CYAN)make service-start$(RESET)"
else
	@echo "$(YELLOW)Creating systemd user service from template...$(RESET)"
	@sed -e 's|{{REPO_ROOT}}|$(REPO_ROOT)|g' \
	     -e 's|{{LOG_DIR}}|$(LOG_DIR)|g' \
	     scheduler/config/scheduler.service.template > $(SERVICE_PATH)
	@systemctl --user daemon-reload
	@echo "$(GREEN)✓ Service installed: $(SERVICE_PATH)$(RESET)"
	@echo "To enable at boot: $(CYAN)systemctl --user enable $(SERVICE_NAME)$(RESET)"
	@echo "To start: $(CYAN)make service-start$(RESET)"
endif

# Start the service
service-start:
	@if [ ! -f "$(SERVICE_PATH)" ]; then \
		echo "$(RED)ERROR: Service not installed. Run 'make install-service' first.$(RESET)"; \
		exit 1; \
	fi
	@echo "$(CYAN)Starting scheduler service...$(RESET)"
ifeq ($(UNAME_S),Darwin)
	@launchctl load $(SERVICE_PATH) 2>/dev/null || true
else
	@systemctl --user start $(SERVICE_NAME)
endif
	@echo "$(GREEN)✓ Service started$(RESET)"
	@echo ""
	@echo "Check status: $(CYAN)make service-status$(RESET)"
	@echo "View logs: $(CYAN)make service-logs$(RESET)"

# Stop the service
service-stop:
	@echo "$(CYAN)Stopping scheduler service...$(RESET)"
ifeq ($(UNAME_S),Darwin)
	@launchctl unload $(SERVICE_PATH) 2>/dev/null || true
else
	@systemctl --user stop $(SERVICE_NAME)
endif
	@echo "$(GREEN)✓ Service stopped$(RESET)"

# Restart the service
service-restart: service-stop service-start

# Show service status
service-status:
	@echo "$(CYAN)Scheduler Service Status:$(RESET)"
	@echo ""
ifeq ($(UNAME_S),Darwin)
	@launchctl list | grep $(SERVICE_NAME) || echo "$(YELLOW)Service is not running$(RESET)"
	@echo ""
	@if [ -f "$(SERVICE_PATH)" ]; then \
		echo "$(GREEN)Service installed: $(SERVICE_PATH)$(RESET)"; \
	else \
		echo "$(RED)Service not installed$(RESET)"; \
	fi
else
	@systemctl --user status $(SERVICE_NAME) --no-pager || echo "$(YELLOW)Service is not running$(RESET)"
	@echo ""
	@if [ -f "$(SERVICE_PATH)" ]; then \
		echo "$(GREEN)Service installed: $(SERVICE_PATH)$(RESET)"; \
	else \
		echo "$(RED)Service not installed$(RESET)"; \
	fi
endif

# Show service logs
service-logs:
	@echo "$(CYAN)Scheduler Logs:$(RESET)"
	@echo ""
	@if [ -f "$(LOG_DIR)/scheduler.log" ]; then \
		echo "$(GREEN)=== Standard Output (last 50 lines) ===$(RESET)"; \
		tail -50 $(LOG_DIR)/scheduler.log; \
		echo ""; \
	else \
		echo "$(YELLOW)No log file found$(RESET)"; \
	fi
	@if [ -f "$(LOG_DIR)/scheduler.error.log" ]; then \
		echo "$(RED)=== Error Output ===$(RESET)"; \
		tail -50 $(LOG_DIR)/scheduler.error.log; \
	else \
		echo "$(GREEN)No errors logged$(RESET)"; \
	fi

# Uninstall the service
uninstall-service: service-stop
	@echo "$(CYAN)Uninstalling scheduler service...$(RESET)"
	@rm -f $(SERVICE_PATH)
ifeq ($(UNAME_S),Linux)
	@systemctl --user daemon-reload
endif
	@echo "$(GREEN)✓ Service uninstalled$(RESET)"
	@echo ""
	@echo "Logs are still available at: $(LOG_DIR)/"

# Test scheduler locally (without service)
test-scheduler:
	@echo "$(CYAN)Testing scheduler locally...$(RESET)"
	@echo "$(YELLOW)Press Ctrl+C to stop$(RESET)"
	@echo ""
	@cd scheduler && $(MAKE) run

# Clean cache files
clean:
	@echo "$(CYAN)Cleaning cache files...$(RESET)"
	@$(MAKE) -C scheduler clean
	@for task in $(TASKS); do \
		if [ -d tasks/$$task ] && [ -f tasks/$$task/Makefile ]; then \
			$(MAKE) -C tasks/$$task clean; \
		fi; \
	done
	@find . -maxdepth 1 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned$(RESET)"

# Remove all virtual environments
clean-venv:
	@echo "$(CYAN)Removing virtual environments...$(RESET)"
	@rm -rf scheduler/.venv
	@for task in $(TASKS); do \
		if [ -d tasks/$$task/.venv ]; then \
			echo "Removing tasks/$$task/.venv"; \
			rm -rf tasks/$$task/.venv; \
		fi; \
	done
	@echo "$(GREEN)✓ Virtual environments removed$(RESET)"

# Deep clean
clean-all: clean clean-venv
	@echo "$(CYAN)Deep cleaning...$(RESET)"
	@rm -rf .idea __pycache__
	@echo "$(GREEN)✓ Deep clean complete$(RESET)"
