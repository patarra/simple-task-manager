.PHONY: install clean clean-all help

# Color output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RESET := \033[0m

# List of all utility directories
UTILITIES := sync-calendars

help:
	@echo "$(CYAN)Utility Scripts Collection$(RESET)"
	@echo ""
	@echo "$(GREEN)Global targets:$(RESET)"
	@echo "  make install     - Install dependencies for ALL utilities"
	@echo "  make clean       - Clean cache files from ALL utilities"
	@echo "  make clean-venv  - Remove virtual environments from ALL utilities"
	@echo "  make clean-all   - Deep clean (cache + venv + .idea)"
	@echo "  make help        - Show this help message"
	@echo ""
	@echo "$(YELLOW)Available utilities:$(RESET)"
	@for dir in $(UTILITIES); do \
		if [ -d $$dir ]; then \
			echo "  📦 $$dir/"; \
		fi; \
	done
	@echo ""
	@echo "$(GREEN)To work with individual utilities:$(RESET)"
	@echo "  cd <utility-name> && make help"
	@echo ""
	@echo "Example:"
	@echo "  cd sync-calendars && make install"

# Install all utilities
install:
	@echo "$(CYAN)Installing all utilities...$(RESET)"
	@for dir in $(UTILITIES); do \
		if [ -d $$dir ] && [ -f $$dir/Makefile ]; then \
			echo "$(GREEN)Installing $$dir...$(RESET)"; \
			$(MAKE) -C $$dir install; \
		fi; \
	done
	@echo "$(GREEN)✓ All utilities installed successfully$(RESET)"

# Clean all utilities
clean:
	@echo "$(CYAN)Cleaning all utilities...$(RESET)"
	@for dir in $(UTILITIES); do \
		if [ -d $$dir ] && [ -f $$dir/Makefile ]; then \
			echo "$(GREEN)Cleaning $$dir...$(RESET)"; \
			$(MAKE) -C $$dir clean; \
		fi; \
	done
	@echo "Removing root-level cache..."
	@find . -maxdepth 1 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ All utilities cleaned$(RESET)"

# Clean everything including virtual environments
clean-all: clean
	@echo "$(CYAN)Deep cleaning (removing .idea, etc.)...$(RESET)"
	@rm -rf .idea __pycache__
	@echo "$(GREEN)✓ Deep clean complete$(RESET)"
