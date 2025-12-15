#!/usr/bin/env python3
"""
Task Scheduler Daemon

Reads config.yaml and schedules tasks using APScheduler with cron triggers.
Each task is executed via its run.sh script with configurable arguments and timeout.
"""

import os
import sys
import time
import yaml
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger


class TaskScheduler:
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.repo_root = self.config_path.parent
        self.config = None
        self.scheduler = BlockingScheduler()
        self.logger = None

    def setup_logging(self):
        """Configure logging based on config.yaml settings."""
        log_file = self.config.get('scheduler', {}).get('log_file', '~/Library/Logs/scheduler.log')
        log_file = Path(log_file).expanduser()

        # Create log directory if it doesn't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self):
        """Load and validate config.yaml."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        if not self.config:
            raise ValueError("Config file is empty")

        if 'tasks' not in self.config:
            raise ValueError("Config file must contain 'tasks' section")

    def validate_task(self, task):
        """Validate a task configuration."""
        required_fields = ['name', 'path', 'cron']
        for field in required_fields:
            if field not in task:
                raise ValueError(f"Task missing required field: {field}")

        # Check if run.sh exists
        task_path = self.repo_root / task['path']
        run_script = task_path / 'run.sh'

        if not task_path.exists():
            raise ValueError(f"Task directory does not exist: {task_path}")

        if not run_script.exists():
            raise ValueError(f"run.sh not found for task '{task['name']}': {run_script}")

        if not os.access(run_script, os.X_OK):
            raise ValueError(f"run.sh is not executable for task '{task['name']}': {run_script}")

        # Validate cron expression (will raise if invalid)
        try:
            CronTrigger.from_crontab(task['cron'])
        except Exception as e:
            raise ValueError(f"Invalid cron expression for task '{task['name']}': {e}")

        return True

    def execute_task(self, task):
        """Execute a task with timeout and logging."""
        task_name = task['name']
        task_path = self.repo_root / task['path']
        args = task.get('args', [])
        timeout = task.get('timeout', self.config.get('scheduler', {}).get('default_timeout', 300))

        self.logger.info(f"Executing '{task_name}' with args {args}")

        start_time = time.time()

        try:
            # Execute run.sh with arguments
            result = subprocess.run(
                ['./run.sh'] + args,
                cwd=task_path,
                timeout=timeout,
                capture_output=True,
                text=True
            )

            duration = time.time() - start_time
            exit_code = result.returncode

            # Log results
            self.logger.info(f"Task '{task_name}' completed in {duration:.1f}s (exit code: {exit_code})")

            # Log stdout if present
            if result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    self.logger.info(f"[{task_name}] STDOUT: {line}")

            # Log stderr if present
            if result.stderr.strip():
                for line in result.stderr.strip().split('\n'):
                    if exit_code == 0:
                        self.logger.warning(f"[{task_name}] STDERR: {line}")
                    else:
                        self.logger.error(f"[{task_name}] STDERR: {line}")

            if exit_code != 0:
                self.logger.error(f"Task '{task_name}' failed with exit code: {exit_code}")

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.logger.error(f"Task '{task_name}' exceeded timeout of {timeout}s (killed after {duration:.1f}s)")

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Task '{task_name}' failed with exception after {duration:.1f}s: {e}")

    def register_tasks(self):
        """Register all enabled tasks with the scheduler."""
        tasks = self.config.get('tasks', [])
        enabled_count = 0

        for task in tasks:
            task_name = task['name']

            # Skip disabled tasks
            if not task.get('enabled', True):
                self.logger.info(f"Task '{task_name}' is disabled, skipping")
                continue

            # Validate task
            try:
                self.validate_task(task)
            except Exception as e:
                self.logger.error(f"Failed to validate task '{task_name}': {e}")
                continue

            # Register with scheduler
            try:
                trigger = CronTrigger.from_crontab(task['cron'])
                self.scheduler.add_job(
                    self.execute_task,
                    trigger=trigger,
                    args=[task],
                    id=task_name,
                    name=task_name,
                    replace_existing=True
                )
                self.logger.info(f"Registered task '{task_name}' with cron '{task['cron']}'")
                enabled_count += 1

            except Exception as e:
                self.logger.error(f"Failed to register task '{task_name}': {e}")

        if enabled_count == 0:
            self.logger.warning("No tasks registered! Check your config.yaml")
        else:
            self.logger.info(f"Successfully registered {enabled_count} task(s)")

    def run(self):
        """Main entry point: load config, register tasks, and start scheduler."""
        try:
            # Load configuration
            self.load_config()

            # Setup logging
            self.setup_logging()

            self.logger.info("=" * 70)
            self.logger.info(f"Task Scheduler starting...")
            self.logger.info(f"Config file: {self.config_path}")
            self.logger.info(f"Repository root: {self.repo_root}")
            self.logger.info("=" * 70)

            # Register tasks
            self.register_tasks()

            # Start scheduler
            self.logger.info("Scheduler started, waiting for scheduled tasks...")
            self.scheduler.start()

        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, shutting down...")
            self.scheduler.shutdown()

        except Exception as e:
            if self.logger:
                self.logger.error(f"Fatal error: {e}", exc_info=True)
            else:
                print(f"Fatal error: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    # Determine config path (repo root / config.yaml)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    config_path = repo_root / 'config.yaml'

    # Create and run scheduler
    scheduler = TaskScheduler(config_path)
    scheduler.run()


if __name__ == '__main__':
    main()
