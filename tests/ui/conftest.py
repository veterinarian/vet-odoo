"""Pytest configuration and fixtures for Playwright UI tests."""
import os
from collections.abc import Generator

import pytest
from playwright.sync_api import Page

# Odoo configuration
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:17069")
ODOO_DB = os.getenv("ODOO_DB", "devel")
ODOO_USER = os.getenv("ODOO_USER", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL for the Odoo instance."""
    return ODOO_URL


@pytest.fixture(scope="session")
def odoo_credentials() -> dict:
    """Odoo login credentials."""
    return {
        "database": ODOO_DB,
        "username": ODOO_USER,
        "password": ODOO_PASSWORD,
    }


@pytest.fixture(scope="function")
def authenticated_page(
    page: Page, base_url: str, odoo_credentials: dict
) -> Generator[Page, None, None]:
    """
    Provide an authenticated Odoo page.

    This fixture logs into Odoo and provides a page ready for testing.
    """
    # Navigate to Odoo with database parameter
    page.goto(f"{base_url}/web?db={odoo_credentials['database']}")
    page.wait_for_load_state("networkidle")

    # Check if we need to select database
    if "database/selector" in page.url:
        # Click on the database
        db_link = page.locator(f'a:has-text("{odoo_credentials["database"]}")')
        if db_link.is_visible(timeout=2000):
            db_link.click()
            page.wait_for_load_state("networkidle")

    # Check if we need to log in (login form visible)
    try:
        if page.locator('input[name="login"]').is_visible(timeout=2000):
            # Fill login form
            page.fill('input[name="login"]', odoo_credentials["username"])
            page.fill('input[name="password"]', odoo_credentials["password"])

            # Submit login
            page.click('button[type="submit"]')

            # Wait for redirect after login
            page.wait_for_load_state("networkidle")
    except Exception:  # noqa: S110
        # Already logged in or login not required
        pass

    yield page

    # Cleanup: logout (optional)
    # Note: You might want to skip logout to speed up tests
    # page.goto(f"{base_url}/web/session/logout")


@pytest.fixture(scope="function")
def odoo_page(page: Page, base_url: str) -> Generator[Page, None, None]:
    """
    Provide a page navigated to Odoo (not necessarily authenticated).

    Use this for testing login flows or public pages.
    """
    page.goto(base_url)
    yield page


class OdooPage:
    """Helper class for common Odoo UI interactions."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def navigate_to_app(self, app_name: str) -> None:
        """Navigate to a specific Odoo app."""
        # Open apps menu
        self.page.click('button[title="Home menu"]', timeout=5000)

        # Click on the app
        self.page.click(f'a.o_app[data-menu-xmlid*="{app_name}"]')
        self.page.wait_for_load_state("networkidle")

    def navigate_to_menu(self, menu_path: str) -> None:
        """
        Navigate to a menu item.

        Args:
            menu_path: Menu path like "Veterinary/Patients" or "Veterinary/Appointments"
        """
        parts = menu_path.split("/")

        for part in parts:
            # Click menu item
            self.page.click(f'a.dropdown-item:has-text("{part.strip()}")')
            self.page.wait_for_timeout(500)

    def create_record(self) -> None:
        """Click the Create button to start creating a new record."""
        self.page.click("button.o_form_button_create")
        self.page.wait_for_load_state("networkidle")

    def save_record(self) -> None:
        """Save the current form."""
        self.page.click("button.o_form_button_save")
        self.page.wait_for_load_state("networkidle")

    def discard_record(self) -> None:
        """Discard changes to the current form."""
        self.page.click("button.o_form_button_cancel")
        self.page.wait_for_load_state("networkidle")

    def search_record(self, search_text: str) -> None:
        """Search for records in list view."""
        self.page.fill("input.o_searchview_input", search_text)
        self.page.press("input.o_searchview_input", "Enter")
        self.page.wait_for_load_state("networkidle")

    def fill_field(self, field_name: str, value: str) -> None:
        """
        Fill a form field by name.

        Args:
            field_name: The name attribute of the field
            value: Value to fill
        """
        selector = f'input[name="{field_name}"], textarea[name="{field_name}"]'
        self.page.fill(selector, value)

    def select_many2one(self, field_name: str, value: str) -> None:
        """
        Select a value in a Many2one field.

        Args:
            field_name: The name attribute of the field
            value: Text to select from dropdown
        """
        # Click to open dropdown
        self.page.click(f'div[name="{field_name}"] input')

        # Wait for dropdown and select value
        self.page.click(f'li.ui-menu-item a:has-text("{value}")')
        self.page.wait_for_timeout(300)

    def get_notification_message(self) -> str:
        """Get the text of the notification message."""
        return self.page.locator(".o_notification_content").inner_text()

    def wait_for_notification(self, timeout: int = 5000) -> None:
        """Wait for a notification to appear."""
        self.page.wait_for_selector(".o_notification", timeout=timeout)


@pytest.fixture(scope="function")
def odoo_helper(authenticated_page: Page, base_url: str) -> OdooPage:
    """Provide an OdooPage helper instance."""
    return OdooPage(authenticated_page, base_url)
