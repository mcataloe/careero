from app.constants import SourceType
from app.models import Company
from app.schemas.roles import RoleCreate
from app.seed import seed_local_data
from app.services.roles import RoleService


def test_role_service_creates_and_reads_role_for_user(db_session) -> None:
    user, sources = seed_local_data(db_session)
    company = Company(
        user=user,
        name="Example Company",
        website_url="https://example.com",
    )
    source = next(source for source in sources if source.source_type == SourceType.MANUAL.value)
    db_session.add(company)
    db_session.commit()

    service = RoleService(db_session)
    role = service.create_role(
        RoleCreate(
            title="Software Engineer",
            company={"id": str(company.id)},
            source={"id": str(source.id)},
            job_url="https://example.com/jobs/software-engineer",
            location="Remote",
            remote_type="remote",
        )
    )

    found_role = service.get_role(role.id)

    assert found_role is not None
    assert found_role.id == role.id
    assert found_role.title == "Software Engineer"
