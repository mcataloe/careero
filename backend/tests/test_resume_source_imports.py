from collections.abc import Generator
from io import BytesIO

import pytest
from docx import Document
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import create_app
from app.models import ResumeSource, ResumeSourceVersion
from app.services.resume_source_imports import (
    MAX_RESUME_SOURCE_IMPORT_BYTES,
    ResumeSourceImportTooLargeError,
    import_resume_source_file,
)


@pytest.fixture
def import_client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def upload(client: TestClient, name: str, content: bytes, content_type: str):
    return client.post(
        "/api/resume-sources/import",
        files={"file": (name, content, content_type)},
    )


def make_docx(text: str) -> bytes:
    document = Document()
    document.add_paragraph(text)
    output = BytesIO()
    document.save(output)
    return output.getvalue()


def make_text_pdf(text: str) -> bytes:
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT\n/F1 12 Tf\n72 720 Td\n({escaped}) Tj\nET\n".encode("ascii")
    return make_pdf_with_stream(stream)


def make_blank_pdf() -> bytes:
    return make_pdf_with_stream(b"")


def make_pdf_with_stream(stream: bytes) -> bytes:
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
            b" >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n"
        + stream
        + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(body)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Root 1 0 R /Size {len(objects) + 1} >>\nstartxref\n{xref_offset}\n%%EOF\n".encode(
            "ascii"
        )
    )
    return bytes(pdf)


def test_import_txt_and_md_files(import_client: TestClient) -> None:
    txt_response = upload(
        import_client,
        "resume.txt",
        b"Python backend engineer",
        "text/plain",
    )
    md_response = upload(
        import_client,
        "profile.md",
        b"# Profile\n\nPostgreSQL and FastAPI.",
        "text/markdown",
    )

    assert txt_response.status_code == 200
    assert txt_response.json()["extracted_text"] == "Python backend engineer"
    assert txt_response.json()["file_type"] == "txt"
    assert txt_response.json()["character_count"] == len("Python backend engineer")

    assert md_response.status_code == 200
    assert "PostgreSQL and FastAPI." in md_response.json()["extracted_text"]
    assert md_response.json()["file_type"] == "md"


def test_import_docx_file(import_client: TestClient) -> None:
    response = upload(
        import_client,
        "resume.docx",
        make_docx("Staff engineer with platform experience."),
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    assert response.status_code == 200
    assert response.json()["file_type"] == "docx"
    assert response.json()["extracted_text"] == "Staff engineer with platform experience."


def test_import_text_based_pdf_file(import_client: TestClient) -> None:
    response = upload(
        import_client,
        "resume.pdf",
        make_text_pdf("Python backend engineer resume text"),
        "application/pdf",
    )

    assert response.status_code == 200
    assert response.json()["file_type"] == "pdf"
    assert response.json()["extracted_text"] == "Python backend engineer resume text"


def test_import_rejects_unsupported_file_types(import_client: TestClient) -> None:
    extension_response = upload(
        import_client,
        "resume.exe",
        b"not allowed",
        "application/octet-stream",
    )
    mime_response = upload(
        import_client,
        "resume.txt",
        b"text",
        "application/octet-stream",
    )

    assert extension_response.status_code == 415
    assert mime_response.status_code == 415


def test_import_rejects_files_larger_than_limit(import_client: TestClient) -> None:
    response = upload(
        import_client,
        "resume.txt",
        b"x" * (MAX_RESUME_SOURCE_IMPORT_BYTES + 1),
        "text/plain",
    )

    assert response.status_code == 413


def test_import_rejects_empty_or_unreadable_files(import_client: TestClient) -> None:
    empty_response = upload(import_client, "resume.txt", b"   ", "text/plain")
    scanned_pdf_response = upload(
        import_client,
        "resume.pdf",
        make_blank_pdf(),
        "application/pdf",
    )

    assert empty_response.status_code == 422
    assert scanned_pdf_response.status_code == 422
    assert "OCR" in scanned_pdf_response.json()["detail"]


def test_import_does_not_persist_resume_source(
    import_client: TestClient,
    db_session: Session,
) -> None:
    response = upload(
        import_client,
        "resume.txt",
        b"Python backend engineer",
        "text/plain",
    )

    assert response.status_code == 200
    assert db_session.scalar(select(func.count()).select_from(ResumeSource)) == 0
    assert db_session.scalar(select(func.count()).select_from(ResumeSourceVersion)) == 0


def test_service_rejects_oversized_content_without_extracting() -> None:
    with pytest.raises(ResumeSourceImportTooLargeError):
        import_resume_source_file(
            file_name="resume.txt",
            content_type="text/plain",
            content=b"x" * (MAX_RESUME_SOURCE_IMPORT_BYTES + 1),
        )
