# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project called "spidermail" - a web spider for email extraction. The project is in early development stages with minimal structure.

## Environment Setup

- Python 3.12+ required
- Uses virtual environment located in `.venv/`
- Managed with `pyproject.toml`

## Common Commands

### Environment Activation
```bash
# On Windows
.venv\Scripts\activate

# On Unix systems
source .venv/bin/activate
```

### Installation
```bash
pip install -e .
```

## Architecture Notes

- Currently a minimal project structure with only configuration files
- No source code modules have been created yet
- Uses standard Python project layout with `pyproject.toml`
- Virtual environment is properly configured and excluded from version control

## Development Environment

- IDE: IntelliJ IDEA (based on .idea/ directory)
- Claude Code is configured with permissions for bash commands in any directory
- Git is initialized but no commits have been made yet