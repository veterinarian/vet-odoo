[![Doodba deployment](https://img.shields.io/badge/deployment-doodba-informational)](https://github.com/Tecnativa/doodba)
[![Last template update](https://img.shields.io/badge/last%20template%20update-v9.0.3-informational)](https://github.com/Tecnativa/doodba-copier-template/tree/v9.0.3)
[![Odoo](https://img.shields.io/badge/odoo-v17.0-a3478a)](https://github.com/odoo/odoo/tree/17.0)
[![AGPL-3.0-or-later license](https://img.shields.io/badge/license-AGPL--3.0--or--later-success})](LICENSE)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)

# Vet Odoo - Veterinary Clinic Management System

A professional Odoo 17 deployment for veterinary clinic management, built with Doodba.

## Features

- **Patient Management** - Comprehensive animal patient records with medical history
- **Owner Management** - Pet owner contact information and relationships
- **Appointment System** - Calendar-based scheduling with workflow management
- **Medical Records** - Diagnosis, treatment plans, and prescriptions
- **Security** - Role-based access control (User and Manager roles)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd vet-odoo

# Build the Docker images (first time only)
docker-compose -f devel.yaml build

# Initialize database with all required modules
./init-db.sh

# Start development environment
docker-compose -f devel.yaml up

# Access Odoo at http://localhost:17069
# Login with admin credentials set during initialization
```

### Automatic Module Installation

The `init-db.sh` script automatically installs the following modules on a fresh
database:

- **account** - Accounting & Invoicing
- **stock** - Inventory Management
- **purchase** - Purchase Management
- **point_of_sale** - Point of Sale
- **base_accounting_kit** - Extended accounting features
- **hr** - Human Resources
- **vet_clinic** - Veterinary Clinic Management (custom)
- **calendar** - Calendar & Activities

To customize the module list, edit `ODOO_DEFAULT_MODULES` in `devel.yaml`.

## Project Structure

```
vet-odoo/
├── odoo/custom/src/private/vet_clinic/    # Veterinary clinic module
├── requirements.txt                        # Python dependencies (reference)
├── requirements-dev.txt                    # Development dependencies
├── DEVELOPMENT.md                          # Development guide
├── devel.yaml                              # Development environment
├── test.yaml                               # Testing environment
└── prod.yaml                               # Production environment
```

## Documentation

- **[Development Guide](DEVELOPMENT.md)** - Setup instructions, workflows, and best
  practices
- **[Module README](odoo/custom/src/private/vet_clinic/README.md)** - Veterinary clinic
  module documentation

## Doodba Resources

This project is a Doodba scaffolding. Check upstream docs:

- [General Doodba docs](https://github.com/Tecnativa/doodba)
- [Doodba copier template docs](https://github.com/Tecnativa/doodba-copier-template)
- [Doodba QA docs](https://github.com/Tecnativa/doodba-qa)

## Requirements Files

- `odoo/custom/dependencies/pip.txt` - Docker/Doodba dependencies (primary)
- `requirements.txt` - Complete dependency reference for local setup
- `requirements-dev.txt` - Development tools (testing, linting, debugging)

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup instructions.

## License

AGPL-3.0-or-later

## Credits

This project is maintained by: veterinarian
