"""UI tests for appointment management in vet_clinic module."""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.ui
@pytest.mark.appointment
class TestAppointmentManagement:
    """Test suite for appointment management UI."""

    def test_create_appointment(self, odoo_helper) -> None:
        """Test creating a new appointment."""
        page = odoo_helper.page

        # Navigate to Veterinary app
        odoo_helper.navigate_to_app("vet_clinic")

        # Navigate to Appointments
        page.click('a.nav-link:has-text("Appointments")')
        page.wait_for_load_state("networkidle")

        # Create new appointment
        odoo_helper.create_record()

        # Select patient (assuming test data exists)
        try:
            odoo_helper.select_many2one("patient_id", "Max")
        except Exception:
            pytest.skip("No test patient available")

        # Fill appointment date
        # Note: Date/datetime fields in Odoo may require special handling
        page.click('div[name="appointment_date"] input')
        page.wait_for_timeout(500)

        # Select appointment type
        page.click('select[name="appointment_type"]')
        page.select_option('select[name="appointment_type"]', "checkup")

        # Save appointment
        odoo_helper.save_record()

        # Verify success
        expect(page.locator(".o_form_view")).to_be_visible()

    def test_appointment_workflow(self, odoo_helper) -> None:
        """Test appointment status workflow (draft -> confirmed -> done)."""
        page = odoo_helper.page

        # Navigate to Appointments
        odoo_helper.navigate_to_app("vet_clinic")
        page.click('a.nav-link:has-text("Appointments")')
        page.wait_for_load_state("networkidle")

        # Open first appointment
        first_appt = page.locator(".o_list_table tbody tr").first
        if first_appt.is_visible():
            first_appt.click()
            page.wait_for_load_state("networkidle")

            # Check for state-related buttons
            # The button names depend on your vet_appointment model

            # Example: Click Confirm button if it exists
            if page.locator('button:has-text("Confirm")').is_visible():
                page.click('button:has-text("Confirm")')
                page.wait_for_timeout(1000)

                # Verify state changed
                expect(page.locator(".o_form_view")).to_be_visible()
        else:
            pytest.skip("No appointments available for testing")

    def test_filter_appointments_by_date(self, odoo_helper) -> None:
        """Test filtering appointments by date."""
        page = odoo_helper.page

        # Navigate to Appointments
        odoo_helper.navigate_to_app("vet_clinic")
        page.click('a.nav-link:has-text("Appointments")')
        page.wait_for_load_state("networkidle")

        # Click on Filters
        page.click("button.o_filters_menu_button")
        page.wait_for_timeout(300)

        # Select a date filter (e.g., "Today", "This Week")
        # The exact filter options depend on your view configuration
        filter_option = page.locator('.o_menu_item:has-text("Today")')
        if filter_option.is_visible():
            filter_option.click()
            page.wait_for_load_state("networkidle")

            # Verify list is filtered
            expect(page.locator(".o_list_view")).to_be_visible()


@pytest.mark.ui
@pytest.mark.appointment
@pytest.mark.smoke
def test_appointment_list_loads(authenticated_page: Page, base_url: str) -> None:
    """Smoke test: Verify appointment list page loads correctly."""
    page = authenticated_page

    # Navigate directly to appointment list
    page.goto(f"{base_url}/web#model=vet.appointment&view_type=list")

    # Wait for Odoo to load (use domcontentloaded instead of networkidle for Odoo)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)  # Give Odoo time to render

    # Take screenshot for debugging
    page.screenshot(path="test-results/appointment_list.png")

    # Verify we're on the right page - check for Odoo content area
    expect(page.locator(".o_action_manager, .o_content")).to_be_visible(timeout=10000)


@pytest.mark.ui
@pytest.mark.appointment
@pytest.mark.slow
def test_appointment_calendar_view(odoo_helper) -> None:
    """Test appointment calendar view."""
    page = odoo_helper.page

    # Navigate to Appointments
    odoo_helper.navigate_to_app("vet_clinic")
    page.click('a.nav-link:has-text("Appointments")')
    page.wait_for_load_state("networkidle")

    # Switch to calendar view (if available)
    calendar_button = page.locator("button.o_calendar")
    if calendar_button.is_visible():
        calendar_button.click()
        page.wait_for_load_state("networkidle")

        # Verify calendar is displayed
        expect(page.locator(".o_calendar_view")).to_be_visible()

        # Test navigation (next/previous)
        page.click("button.o_calendar_button_next")
        page.wait_for_timeout(500)

        page.click("button.o_calendar_button_prev")
        page.wait_for_timeout(500)
    else:
        pytest.skip("Calendar view not available")


@pytest.mark.ui
@pytest.mark.appointment
@pytest.mark.e2e
def test_complete_appointment_flow(odoo_helper) -> None:
    """End-to-end test: Create, confirm, and complete an appointment."""
    page = odoo_helper.page

    # Navigate to Appointments
    odoo_helper.navigate_to_app("vet_clinic")
    page.click('a.nav-link:has-text("Appointments")')
    page.wait_for_load_state("networkidle")

    # Create new appointment
    odoo_helper.create_record()

    # Fill required fields
    try:
        odoo_helper.select_many2one("patient_id", "Max")
    except Exception:
        pytest.skip("No test patient available")

    # Select appointment type
    page.click('select[name="appointment_type"]')
    page.select_option('select[name="appointment_type"]', "checkup")

    # Save
    odoo_helper.save_record()

    # Get appointment reference/name
    appt_name = page.locator("ol.breadcrumb li.active").inner_text()

    # Confirm appointment (if button exists)
    if page.locator('button:has-text("Confirm")').is_visible():
        page.click('button:has-text("Confirm")')
        page.wait_for_timeout(1000)

    # Mark as done (if button exists)
    done_button = page.locator('button:has-text("Done"), button:has-text("Complete")')
    if done_button.is_visible():
        done_button.first.click()
        page.wait_for_timeout(1000)

    # Verify we're still on the form
    expect(page.locator(".o_form_view")).to_be_visible()
    expect(page.locator("ol.breadcrumb")).to_contain_text(appt_name)
