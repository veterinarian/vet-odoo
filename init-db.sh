#!/bin/bash
# Initialize Odoo database with pre-selected modules
# Usage: ./init-db.sh
#
# The list of modules to install is defined in devel.yaml under ODOO_DEFAULT_MODULES
# Default modules: account, stock, purchase, point_of_sale, base_accounting_kit, hr, vet_clinic, calendar

set -e

# Default modules (can be overridden by environment variable)
MODULES="${ODOO_DEFAULT_MODULES:-account,stock,purchase,point_of_sale,base_accounting_kit,hr,vet_clinic,calendar}"

echo "Initializing Odoo database with pre-configured modules..."
echo "Modules to install: $MODULES"
echo ""

# Stop any running containers
echo "Stopping any running containers..."
docker-compose -f devel.yaml down

# Initialize database with modules
echo "Initializing database (this may take a few minutes)..."
docker-compose -f devel.yaml run --rm odoo \
    --stop-after-init \
    -i "$MODULES" \
    --without-demo=all

echo ""
echo "✓ Database initialized successfully!"
echo ""
echo "To start Odoo, run:"
echo "  docker-compose -f devel.yaml up"
