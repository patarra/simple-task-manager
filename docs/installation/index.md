# Installation Guide

Simple Task Manager works on both macOS and Linux with platform-specific service managers.

## Choose Your Platform

- **[macOS Installation](macos.md)** - Using launchd
- **[Linux Installation](linux.md)** - Using systemd

## General Requirements

- **Python**: 3.7 or higher
- **Git**: For cloning the repository
- **Make**: Build automation (usually pre-installed)

## Installation Overview

The installation process is the same on both platforms:

1. Clone the repository
2. Run `make install` to install dependencies
3. Configure tasks in `config.yaml`
4. Run `make install-service` to create system service
5. Run `make service-start` to start the scheduler

The Makefile automatically detects your operating system and uses the appropriate service manager (launchd for macOS, systemd for Linux).

## Verification

After installation, verify everything is working:

```bash
# Check scheduler status
make service-status

# View logs
make service-logs

# Test locally (optional)
make test-scheduler
```

## Upgrading

To upgrade to a new version:

```bash
# Pull latest changes
git pull

# Stop the service
make service-stop

# Reinstall dependencies
make clean-venv
make install

# Restart the service
make service-start
```

## Uninstallation

To completely remove Simple Task Manager:

```bash
# Stop and remove the service
make uninstall-service

# Remove virtual environments
make clean-venv
make clean-all

# Remove the repository
cd ..
rm -rf simple-task-manager
```

Logs will remain at:
- macOS: `~/Library/Logs/scheduler.log`
- Linux: `~/.local/share/scheduler/logs/scheduler.log`

## Next Steps

- [Configuration Reference](../configuration.md)
- [Adding Tasks](../guides/adding-tasks.md)
- [Troubleshooting](../troubleshooting.md)
