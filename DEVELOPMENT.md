# Development Guide

## Requirements Files Overview

This project has multiple requirements files for different purposes:

### 📦 Dependency Files

1. **`odoo/custom/dependencies/pip.txt`** (Recommended for Doodba/Docker)
   - Used by Doodba Docker builds
   - Automatically installed in Docker containers
   - **This is the primary file for Docker-based development**

2. **`requirements.txt`** (Reference/Local Development)
   - Complete list of Odoo 17 core dependencies
   - Use for local virtual environment setup
   - Reference for understanding all project dependencies

3. **`requirements-dev.txt`** (Development Tools)
   - Development-only dependencies (testing, linting, debugging)
   - Not needed in production
   - Install alongside `requirements.txt` for local development

## Setup Instructions

### Option 1: Docker/Doodba (Recommended)

Dependencies are automatically managed. Just run:

```bash
# Start development environment
docker-compose -f devel.yaml up

# Dependencies from odoo/custom/dependencies/pip.txt are auto-installed
```

To add a new dependency:
1. Edit `odoo/custom/dependencies/pip.txt`
2. Rebuild the container:
   ```bash
   docker-compose -f devel.yaml build
   docker-compose -f devel.yaml up
   ```

### Option 2: Local Virtual Environment

For local development without Docker:

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Odoo (clone from source)
git clone --depth 1 --branch 17.0 https://github.com/odoo/odoo.git odoo-src
pip install -e odoo-src

# Install project dependencies
pip install -r requirements.txt

# Install development tools
pip install -r requirements-dev.txt

# Run Odoo
./odoo-src/odoo-bin -c odoo.conf --addons-path=odoo/custom/src/private
```

### Option 3: System-wide Installation (Not Recommended)

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Development Workflow

### With Docker (Doodba)

```bash
# Start development server with auto-reload
docker-compose -f devel.yaml up

# Run tests
docker-compose -f devel.yaml run --rm odoo test

# Run specific module tests
docker-compose -f devel.yaml run --rm odoo test --test-tags /vet_clinic

# Access Python shell
docker-compose -f devel.yaml run --rm odoo shell

# Install pre-commit hooks
pre-commit install
```

### With Local Environment

```bash
# Activate virtual environment
source venv/bin/activate

# Run Odoo
odoo-bin -c config.conf --addons-path=odoo/custom/src/private -d dev_db

# Run with auto-reload
odoo-bin -c config.conf --dev=all --addons-path=odoo/custom/src/private -d dev_db

# Run tests
odoo-bin -c config.conf -d test_db --test-enable -i vet_clinic --stop-after-init

# Run linting
ruff check .
black --check .
pylint odoo/custom/src/private/vet_clinic
```

## Adding New Dependencies

### For Docker/Production

Add to `odoo/custom/dependencies/pip.txt`:
```txt
# Example
pandas>=2.0.0
numpy>=1.24.0
```

Then rebuild:
```bash
docker-compose -f devel.yaml build --no-cache
```

### For Local Development Only

Add to `requirements-dev.txt`:
```txt
# Example
pytest-mock>=3.11.0
```

## Code Quality

### Pre-commit Hooks

The project uses pre-commit hooks for code quality:

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

### Manual Linting

```bash
# Python linting
ruff check odoo/custom/src/private/
black odoo/custom/src/private/
pylint odoo/custom/src/private/vet_clinic

# JavaScript linting (if applicable)
eslint odoo/custom/src/private/**/*.js

# XML formatting
prettier --write "odoo/custom/src/private/**/*.xml"
```

## Testing

### Run All Tests

```bash
# Docker
docker-compose -f test.yaml run --rm odoo

# Local
pytest odoo/custom/src/private/vet_clinic/tests/
```

### Run Specific Tests

```bash
# Docker
docker-compose -f devel.yaml run --rm odoo test --test-tags /vet_clinic

# Local
pytest odoo/custom/src/private/vet_clinic/tests/test_vet_patient.py::TestVetPatient::test_patient_creation
```

### Coverage Report

```bash
# Local
pytest --cov=odoo/custom/src/private/vet_clinic --cov-report=html
# Open htmlcov/index.html in browser
```

## Debugging

### IPython Shell

```bash
# Docker
docker-compose -f devel.yaml run --rm odoo shell

# Local
odoo-bin shell -c config.conf -d dev_db
```

### Debugger

Add to your Python code:
```python
import ipdb; ipdb.set_trace()
```

Or use VS Code debugger (see `.vscode/launch.json`)

## Database Management

### Create Database

```bash
# Docker
docker-compose -f devel.yaml run --rm odoo --init=vet_clinic --stop-after-init

# Local
odoo-bin -c config.conf -d new_db -i vet_clinic --stop-after-init
```

### Update Module

```bash
# Docker
docker-compose -f devel.yaml run --rm odoo --update=vet_clinic --stop-after-init

# Local
odoo-bin -c config.conf -d dev_db -u vet_clinic --stop-after-init
```

### Backup/Restore

```bash
# Backup
docker-compose -f devel.yaml exec db pg_dump -U odoo prod > backup.sql

# Restore
docker-compose -f devel.yaml exec -T db psql -U odoo prod < backup.sql
```

## Useful Commands

### Docker

```bash
# View logs
docker-compose -f devel.yaml logs -f odoo

# Execute command in container
docker-compose -f devel.yaml exec odoo bash

# Clean up
docker-compose -f devel.yaml down -v
```

### Invoke Tasks

The project includes `invoke` tasks (see `tasks.py`):

```bash
# List available tasks
invoke --list

# Common tasks (when Docker is available)
invoke develop
invoke test
```

## Troubleshooting

### Port Already in Use

```bash
# Change port in devel.yaml
# Or kill process using port 8069
sudo lsof -ti:8069 | xargs kill -9
```

### Module Not Found

```bash
# Update addons path
# Restart Odoo
# Update apps list in Odoo UI
```

### Permission Issues (Docker)

```bash
# Fix ownership
sudo chown -R $USER:$USER odoo/
```

## Resources

- [Odoo 17 Documentation](https://www.odoo.com/documentation/17.0/)
- [Doodba Documentation](https://github.com/Tecnativa/doodba)
- [OCA Guidelines](https://github.com/OCA/odoo-community.org)
- [Odoo Development Tutorials](https://www.odoo.com/documentation/17.0/developer.html)
