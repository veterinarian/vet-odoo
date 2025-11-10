# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in
this repository.

## Project Overview

A veterinary clinic management system built on Odoo 17, deployed using the Doodba
framework. The main custom module is `vet_clinic`, which provides patient management,
appointment scheduling, owner records, and resource booking functionality.

## Architecture

### Doodba Framework

This project uses Doodba (Docker-based Odoo deployment) with three environment
configurations:

- **devel.yaml**: Development environment with auto-reload, debugging tools (port 17069)
- **test.yaml**: Testing environment with minimal workers
- **prod.yaml**: Production configuration

### Module Structure

The custom veterinary module lives at `odoo/custom/src/private/vet_clinic/` with
standard Odoo structure:

- **models/**: Core business logic (vet_patient, vet_appointment, vet_owner, vet_room,
  resource_booking, etc.)
- **views/**: XML UI definitions
- **security/**: Access control (vet_clinic_security.xml, ir.model.access.csv)
- **data/**: Initial data (species, room types, provider types)
- **tests/**: Test modules
- **hooks.py**: Post-installation hooks

Key dependencies: base, mail, calendar, resource_booking (OCA module)

### Data Models

- **vet.patient**: Animal patient records with species, breed, age/birth_date, owner
  relationship
- **vet.appointment**: Appointment scheduling with workflow states (draft → confirmed →
  in_progress → done/cancelled)
- **vet.owner**: Pet owner contact information
- **resource.booking**: Integration with OCA resource_booking for room/resource
  scheduling
- **res.users**: Extended with provider_type_ids for veterinarian specializations

## Common Commands

### Development Environment

```bash
# Start development server (with auto-reload)
docker-compose -f devel.yaml up

# Initialize fresh database with all modules
./init-db.sh

# Stop containers
docker-compose -f devel.yaml down

# Rebuild after dependency changes
docker-compose -f devel.yaml build

# Access Odoo shell
docker-compose -f devel.yaml run --rm odoo shell
```

### Module Management

```bash
# Install/reinstall vet_clinic module
docker-compose -f devel.yaml run --rm odoo --init=vet_clinic --stop-after-init

# Update module after code changes
docker-compose -f devel.yaml run --rm odoo --update=vet_clinic --stop-after-init

# Install without demo data
docker-compose -f devel.yaml run --rm odoo -i vet_clinic --stop-after-init --without-demo=all
```

### Testing

```bash
# Run all tests
docker-compose -f test.yaml run --rm odoo

# Run specific module tests
docker-compose -f devel.yaml run --rm odoo test --test-tags /vet_clinic

# Run tests for single test file (local pytest)
pytest odoo/custom/src/private/vet_clinic/tests/test_vet_patient.py
```

### Code Quality

```bash
# Run pre-commit hooks manually
pre-commit run --all-files

# Python linting
ruff check odoo/custom/src/private/
pylint odoo/custom/src/private/vet_clinic

# Python formatting
ruff format odoo/custom/src/private/

# XML formatting
prettier --write "odoo/custom/src/private/**/*.xml"
```

### Debugging

```bash
# Start with debugger support
docker-compose -f devel.yaml up
# Then add in code: import ipdb; ipdb.set_trace()

# View logs
docker-compose -f devel.yaml logs -f odoo

# Execute command in running container
docker-compose -f devel.yaml exec odoo bash
```

### Database Operations

```bash
# Backup database
docker-compose -f devel.yaml exec db pg_dump -U odoo devel > backup.sql

# Restore database
docker-compose -f devel.yaml exec -T db psql -U odoo devel < backup.sql

# Connect to PostgreSQL
# Web interface: http://localhost:17081 (pgweb)
# Or: docker-compose -f devel.yaml exec db psql -U odoo devel
```

## Development Workflow

### Adding Dependencies

**For production/Docker**: Add to `odoo/custom/dependencies/pip.txt`, then rebuild:

```bash
docker-compose -f devel.yaml build --no-cache
```

**For local development**: Add to `requirements-dev.txt`

### Module Development Pattern

1. Make changes to Python models in `odoo/custom/src/private/vet_clinic/models/`
2. Update XML views in `odoo/custom/src/private/vet_clinic/views/`
3. Add/update security rules in `security/` directory
4. Update module version in `__manifest__.py` if needed
5. Run module update command (see above)
6. Test changes with `--test-tags /vet_clinic`
7. Commit with pre-commit hooks

### Odoo Development Specifics

- **Inheritance patterns**: Use `_inherit` to extend existing models (e.g., res.users)
- **Tracking**: Fields with `tracking=True` log changes in chatter
- **Sequences**: Appointment references use `ir.sequence` with code 'vet.appointment'
- **Compute fields**: Use `@api.depends()` decorator with `store=True/False`
- **Onchange methods**: Use `@api.onchange()` for real-time field updates
- **Constraints**: Use `@api.constrains()` for validation
- **Post-init hooks**: Defined in `hooks.py` and referenced in `__manifest__.py`

## File Locations

- **Custom module**: `odoo/custom/src/private/vet_clinic/`
- **Dependencies**: `odoo/custom/dependencies/pip.txt` (primary for Docker)
- **Docker configs**: `devel.yaml`, `test.yaml`, `prod.yaml`, `common.yaml`
- **Invoke tasks**: `tasks.py` (run with `invoke --list`)
- **Pre-commit config**: `.pre-commit-config.yaml`
- **Linter configs**: `.pylintrc`, `.pylintrc-mandatory`, `.ruff.toml`, `.eslintrc.yml`

## Services and Ports (Development)

- Odoo: http://localhost:17069
- pgweb (DB admin): http://localhost:17081
- MailHog (email testing): http://localhost:17025
- WDB debugger: http://localhost:17984

## Important Notes

- The development environment uses `--dev=reload,qweb,werkzeug,xml` for auto-reload
- Database name for devel: `devel`, for test: varies
- Pre-commit hooks enforce OCA code standards, ruff formatting, pylint rules
- The project uses Python 3.11 (see `.python-version`)
- Odoo version: 17.0
- PostgreSQL version: 15

## Pre-commit Hooks

Pre-commit hooks are mandatory. Key checks:

- **oca-checks-odoo-module**: Validates Odoo module structure
- **ruff**: Python linting and formatting
- **pylint_odoo**: Odoo-specific Python linting
- **prettier**: XML/JS formatting
- **oca-gen-addon-readme**: Auto-generates module README from fragments

Install hooks before committing:

```bash
pre-commit install
```
