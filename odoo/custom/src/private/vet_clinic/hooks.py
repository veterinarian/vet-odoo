import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Initialize resources for existing rooms and providers"""
    _logger.info("Starting post-init hook for vet_clinic module")

    # Create resources for existing rooms
    rooms_without_resource = env["vet.room"].search([("resource_id", "=", False)])
    _logger.info(f"Found {len(rooms_without_resource)} rooms without resources")

    for room in rooms_without_resource:
        resource = env["resource.resource"].create(
            {
                "name": room.name,
                "resource_type": "material",
                "active": room.active,
            }
        )
        room.resource_id = resource
        _logger.info(f"Created resource for room: {room.name}")

    # Create resources for existing providers
    providers_without_resource = env["res.users"].search(
        [("is_provider", "=", True), ("provider_resource_id", "=", False)]
    )
    _logger.info(f"Found {len(providers_without_resource)} providers without resources")

    for provider in providers_without_resource:
        resource = env["resource.resource"].create(
            {
                "name": provider.name,
                "resource_type": "user",
                "user_id": provider.id,
                "active": provider.active,
            }
        )
        provider.provider_resource_id = resource
        _logger.info(f"Created resource for provider: {provider.name}")

    # Create partners for existing owners
    owners_without_partner = env["vet.owner"].search([("partner_id", "=", False)])
    _logger.info(f"Found {len(owners_without_partner)} owners without partners")

    for owner in owners_without_partner:
        partner = env["res.partner"].create(
            {
                "name": owner.name,
                "email": owner.email,
                "phone": owner.phone,
                "mobile": owner.mobile,
                "street": owner.street,
                "street2": owner.street2,
                "city": owner.city,
                "state_id": owner.state_id.id if owner.state_id else False,
                "zip": owner.zip,
                "country_id": owner.country_id.id if owner.country_id else False,
                "comment": f"Pet Owner - {owner.name}",
            }
        )
        owner.partner_id = partner
        _logger.info(f"Created partner for owner: {owner.name}")

    _logger.info("Post-init hook completed successfully")
