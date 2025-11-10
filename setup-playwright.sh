#!/bin/bash
# Setup script for Playwright UI testing
# This script installs Playwright and browsers locally (not in Docker)

set -e

echo "Setting up Playwright for UI testing..."
echo ""

# Install Python dependencies
echo "Installing Playwright Python packages..."
pip install -r requirements-dev.txt

# Install Playwright browsers
echo "Installing Playwright browsers (this may take a few minutes)..."
playwright install chromium

# Install system dependencies if needed
echo "Installing system dependencies..."
playwright install-deps chromium

echo ""
echo "✓ Playwright setup complete!"
echo ""
echo "Make sure Odoo is running first:"
echo "  docker-compose -f devel.yaml up"
echo ""
echo "Then run UI tests with:"
echo "  pytest tests/ui/"
echo ""
echo "For more options, see: tests/ui/README.md"
