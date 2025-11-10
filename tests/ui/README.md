# UI Tests with Playwright

This directory contains UI/E2E tests for the vet_clinic Odoo module using Playwright.

## Setup

### 1. Install Playwright Browsers

After rebuilding the Docker container with Playwright dependencies, install the
browsers:

```bash
# Inside Docker container
docker-compose -f devel.yaml run --rm odoo bash
playwright install chromium

# Or for all browsers
playwright install
```

For local development (outside Docker):

```bash
pip install playwright pytest-playwright
playwright install
```

### 2. Configure Test Environment

Set environment variables for your test environment:

```bash
# .env file or export in shell
export ODOO_URL=http://localhost:17069
export ODOO_DB=devel
export ODOO_USER=admin
export ODOO_PASSWORD=admin
```

## Running Tests

### Run All UI Tests

```bash
# From project root
pytest tests/ui/

# Or with more verbose output
pytest tests/ui/ -v
```

### Run Specific Test File

```bash
pytest tests/ui/test_patient_management.py
pytest tests/ui/test_appointments.py
```

### Run Tests by Marker

```bash
# Run only smoke tests (quick)
pytest tests/ui/ -m smoke

# Run patient management tests
pytest tests/ui/ -m patient

# Run appointment tests
pytest tests/ui/ -m appointment

# Run end-to-end tests
pytest tests/ui/ -m e2e

# Exclude slow tests
pytest tests/ui/ -m "not slow"
```

### Run with Different Browsers

```bash
# Chromium (default)
pytest tests/ui/ --browser=chromium

# Firefox
pytest tests/ui/ --browser=firefox

# WebKit (Safari)
pytest tests/ui/ --browser=webkit

# Multiple browsers
pytest tests/ui/ --browser=chromium --browser=firefox
```

### Run in Headed Mode (See Browser)

```bash
# Show browser window while tests run
pytest tests/ui/ --headed

# Slow down actions for debugging (milliseconds)
pytest tests/ui/ --headed --slowmo=1000
```

### Run with Video Recording

```bash
pytest tests/ui/ --video=on

# Videos saved to test-results/ directory
```

### Run with Screenshots on Failure

```bash
pytest tests/ui/ --screenshot=only-on-failure

# Or always take screenshots
pytest tests/ui/ --screenshot=on
```

## Test Structure

### Fixtures (conftest.py)

- **authenticated_page**: Provides a Playwright page logged into Odoo
- **odoo_page**: Provides a page at Odoo URL (not logged in)
- **odoo_helper**: Provides OdooPage helper class with common operations
- **base_url**: Odoo base URL
- **odoo_credentials**: Login credentials

### Helper Class (OdooPage)

The `OdooPage` class in `conftest.py` provides common Odoo operations:

```python
def test_example(odoo_helper: OdooPage):
    # Navigate to app
    odoo_helper.navigate_to_app("vet_clinic")

    # Create new record
    odoo_helper.create_record()

    # Fill fields
    odoo_helper.fill_field("name", "Max")
    odoo_helper.select_many2one("owner_id", "John Doe")

    # Save
    odoo_helper.save_record()

    # Search
    odoo_helper.search_record("Max")
```

### Test Markers

Tests are organized with pytest markers:

- `@pytest.mark.ui`: All UI tests
- `@pytest.mark.patient`: Patient management tests
- `@pytest.mark.appointment`: Appointment tests
- `@pytest.mark.smoke`: Quick smoke tests
- `@pytest.mark.e2e`: End-to-end workflow tests
- `@pytest.mark.slow`: Tests that take longer

## Writing New Tests

### Basic Test Template

```python
import pytest
from playwright.sync_api import Page, expect
from conftest import OdooPage

@pytest.mark.ui
@pytest.mark.patient
def test_my_feature(odoo_helper: OdooPage):
    """Test description."""
    page = odoo_helper.page

    # Navigate
    odoo_helper.navigate_to_app("vet_clinic")
    page.click('a.nav-link:has-text("Patients")')

    # Perform actions
    odoo_helper.create_record()
    odoo_helper.fill_field("name", "Test")

    # Assertions
    expect(page.locator('.o_form_view')).to_be_visible()
```

### Test Data

For reliable tests, consider:

1. **Creating test data in setup**: Use `@pytest.fixture` to create required records
2. **Using hooks.py**: Add test data to post_init_hook
3. **Demo data**: Enable demo data in test environment
4. **Cleanup**: Remove test data in teardown

## Debugging Tests

### Interactive Mode

```bash
# Open browser and pause on first test
pytest tests/ui/ --headed --slowmo=1000 -x

# Use page.pause() in test code for debugging
def test_debug(odoo_helper: OdooPage):
    page = odoo_helper.page
    page.pause()  # Opens Playwright Inspector
    # ... rest of test
```

### Debug Logs

```bash
# Enable debug logs
DEBUG=pw:api pytest tests/ui/test_patient_management.py

# Or in code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Screenshots on Failure

Screenshots are automatically saved when tests fail (if configured). Check the
`test-results/` directory.

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Install Playwright
  run: |
    pip install playwright pytest-playwright
    playwright install --with-deps chromium

- name: Run UI Tests
  env:
    ODOO_URL: http://localhost:17069
    ODOO_DB: test
    ODOO_USER: admin
    ODOO_PASSWORD: admin
  run: |
    pytest tests/ui/ --browser=chromium
```

## Tips

1. **Use explicit waits**: `page.wait_for_load_state("networkidle")`
2. **Prefer data attributes**: Use `data-*` attributes for stable selectors
3. **Isolate tests**: Each test should be independent
4. **Mock external services**: Don't depend on external APIs
5. **Keep tests fast**: Use smoke tests for quick feedback
6. **Page Object Pattern**: Consider creating page objects for complex workflows

## Troubleshooting

### "No tests ran"

- Check test discovery: `pytest --collect-only tests/ui/`
- Verify file naming: `test_*.py` or `*_test.py`

### "Timeout waiting for element"

- Increase timeout: `page.click(selector, timeout=10000)`
- Check selector: Use Playwright Inspector
- Wait for network: `page.wait_for_load_state("networkidle")`

### "Element not clickable"

- Wait for element: `page.wait_for_selector(selector)`
- Scroll into view: `page.locator(selector).scroll_into_view_if_needed()`
- Check visibility: `expect(page.locator(selector)).to_be_visible()`

## Resources

- [Playwright Python Docs](https://playwright.dev/python/)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-pytest)
- [Odoo Documentation](https://www.odoo.com/documentation/17.0/)
