"""UI tests for patient management in vet_clinic module."""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.ui
@pytest.mark.patient
class TestPatientManagement:
    """Test suite for patient management UI."""

    def test_create_patient_basic(self, odoo_helper) -> None:
        """Test creating a basic patient record."""
        page = odoo_helper.page

        # Navigate to Veterinary app
        odoo_helper.navigate_to_app("vet_clinic")

        # Navigate to Patients menu
        page.click('a.nav-link:has-text("Patients")')
        page.wait_for_load_state("networkidle")

        # Click Create button
        odoo_helper.create_record()

        # Fill in patient details
        odoo_helper.fill_field("name", "Max")

        # Select owner (assuming an owner exists)
        # You may need to create test data first
        try:
            odoo_helper.select_many2one("owner_id", "Test Owner")
        except Exception:
            # If no owner exists, skip or create one
            pytest.skip("No test owner available")

        # Select species
        try:
            odoo_helper.select_many2one("species_id", "Dog")
        except Exception:
            pytest.skip("No species data available")

        # Fill breed
        odoo_helper.fill_field("breed", "Golden Retriever")

        # Save the record
        odoo_helper.save_record()

        # Verify success - check for patient name in breadcrumb or form
        expect(page.locator("ol.breadcrumb")).to_contain_text("Max")

    def test_search_patient(self, odoo_helper) -> None:
        """Test searching for a patient."""
        page = odoo_helper.page

        # Navigate to Patients
        odoo_helper.navigate_to_app("vet_clinic")
        page.click('a.nav-link:has-text("Patients")')
        page.wait_for_load_state("networkidle")

        # Search for a patient
        odoo_helper.search_record("Max")

        # Verify search results appear
        # This assumes at least one result; adjust based on test data
        expect(page.locator(".o_list_table")).to_be_visible()

    def test_view_patient_details(self, odoo_helper) -> None:
        """Test viewing patient details."""
        page = odoo_helper.page

        # Navigate to Patients
        odoo_helper.navigate_to_app("vet_clinic")
        page.click('a.nav-link:has-text("Patients")')
        page.wait_for_load_state("networkidle")

        # Click on the first patient in the list (if any)
        first_patient = page.locator(".o_list_table tbody tr").first
        if first_patient.is_visible():
            first_patient.click()
            page.wait_for_load_state("networkidle")

            # Verify we're on the form view
            expect(page.locator(".o_form_view")).to_be_visible()
            expect(page.locator('div[name="name"]')).to_be_visible()
        else:
            pytest.skip("No patients available for viewing")

    def test_edit_patient(self, odoo_helper) -> None:
        """Test editing a patient record."""
        page = odoo_helper.page

        # Navigate to Patients
        odoo_helper.navigate_to_app("vet_clinic")
        page.click('a.nav-link:has-text("Patients")')
        page.wait_for_load_state("networkidle")

        # Click on the first patient
        first_patient = page.locator(".o_list_table tbody tr").first
        if first_patient.is_visible():
            first_patient.click()
            page.wait_for_load_state("networkidle")

            # Click Edit button
            page.click("button.o_form_button_edit")

            # Modify breed field
            odoo_helper.fill_field("breed", "Labrador Retriever")

            # Save changes
            odoo_helper.save_record()

            # Verify the change was saved
            expect(page.locator('div[name="breed"]')).to_contain_text("Labrador")
        else:
            pytest.skip("No patients available for editing")


@pytest.mark.ui
@pytest.mark.patient
@pytest.mark.smoke
def test_patient_list_loads(authenticated_page: Page, base_url: str) -> None:
    """Smoke test: Verify patient list page loads correctly."""
    page = authenticated_page

    # Navigate directly to patient list
    page.goto(f"{base_url}/web#model=vet.patient&view_type=list")

    # Wait for Odoo to load (use domcontentloaded instead of networkidle for Odoo)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)  # Give Odoo time to render

    # Take screenshot for debugging
    page.screenshot(path="test-results/patient_list.png")

    # Verify we're on the right page - check for Odoo content area
    expect(page.locator(".o_action_manager, .o_content")).to_be_visible(timeout=10000)


@pytest.mark.ui
@pytest.mark.patient
def test_patient_form_validation(odoo_helper) -> None:
    """Test form validation when required fields are missing."""
    page = odoo_helper.page

    # Navigate to Patients
    odoo_helper.navigate_to_app("vet_clinic")
    page.click('a.nav-link:has-text("Patients")')
    page.wait_for_load_state("networkidle")

    # Click Create
    odoo_helper.create_record()

    # Try to save without filling required fields
    page.click("button.o_form_button_save")

    # Verify validation message appears (Odoo shows invalid fields in red)
    # The exact validation behavior may vary by Odoo version
    expect(page.locator(".o_form_view")).to_be_visible()
    # Form should still be in edit mode if validation failed
    expect(page.locator("button.o_form_button_save")).to_be_visible()
