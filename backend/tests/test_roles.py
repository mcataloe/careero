import uuid

from app.models import Company, User
from app.services.roles import RoleService


def test_role_service_creates_and_reads_role_for_user(db_session) -> None:
    user = User(
        email="role-test@careero.local",
        display_name="Role Test User",
    )
    company = Company(
        user=user,
        name="Example Company",
        website_url="https://example.com",
    )
    db_session.add_all([user, company])
    db_session.commit()

    service = RoleService(db_session)
    role = service.create_role(
        user_id=user.id,
        company_id=company.id,
        title="Software Engineer",
        location="Remote",
        employment_type="Full-time",
        source_url="https://example.com/jobs/software-engineer",
    )
    db_session.commit()

    found_role = service.get_role_for_user(role_id=role.id, user_id=user.id)
    missing_for_other_user = service.get_role_for_user(
        role_id=role.id,
        user_id=uuid.uuid4(),
    )

    assert found_role is not None
    assert found_role.id == role.id
    assert found_role.title == "Software Engineer"
    assert missing_for_other_user is None
