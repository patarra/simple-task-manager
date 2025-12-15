.PHONY: install clean run help

# Colors
CYAN := \033[0;36m
GREEN := \033[0;32m
RESET := \033[0m

# Virtual environment settings
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

help:
	@echo "$(CYAN)Scheduler - Available targets:$(RESET)"
	@echo ""
	@echo "  make install  - Create venv and install dependencies"
	@echo "  make run      - Run scheduler daemon (for testing)"
	@echo "  make clean    - Remove Python cache files"
	@echo "  make clean-venv - Remove virtual environment"

# Create virtual environment if it doesn't exist
$(VENV)/bin/activate:
	@echo "Creating virtual environment..."
	@python3 -m venv $(VENV)
	@echo "$(GREEN)✓ Virtual environment created$(RESET)"

# Install dependencies
install: $(VENV)/bin/activate
	@echo "$(CYAN)Installing scheduler dependencies...$(RESET)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Scheduler dependencies installed$(RESET)"

# Run scheduler (for testing)
run: install
	@echo "$(CYAN)Starting scheduler...$(RESET)"
	@$(PYTHON) scheduler.py

# Clean cache files
clean:
	@echo "Cleaning Python cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned$(RESET)"

# Remove virtual environment
clean-venv:
	@echo "Removing virtual environment..."
	@rm -rf $(VENV)
	@echo "$(GREEN)✓ Virtual environment removed$(RESET)"
