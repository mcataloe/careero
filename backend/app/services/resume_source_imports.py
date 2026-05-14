from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
from pathlib import PurePath

from docx import Document
from pypdf import PdfReader

MAX_RESUME_SOURCE_IMPORT_BYTES = 5 * 1024 * 1024

SUPPORTED_CONTENT_TYPES: dict[str, set[str]] = {
    ".txt": {"text/plain"},
    ".md": {"text/markdown", "text/plain"},
    ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    ".pdf": {"application/pdf"},
}


class ResumeSourceImportError(Exception):
    pass


class ResumeSourceImportUnsupportedTypeError(ResumeSourceImportError):
    pass


class ResumeSourceImportTooLargeError(ResumeSourceImportError):
    pass


class ResumeSourceImportUnreadableError(ResumeSourceImportError):
    pass


@dataclass(frozen=True)
class ResumeSourceImportResult:
    file_name: str
    file_type: str
    content_type: str
    size_bytes: int
    character_count: int
    extracted_text: str
    warnings: list[str] = field(default_factory=list)


def import_resume_source_file(
    *,
    file_name: str | None,
    content_type: str | None,
    content: bytes,
) -> ResumeSourceImportResult:
    safe_file_name = PurePath(file_name or "").name
    extension = PurePath(safe_file_name).suffix.lower()
    normalized_content_type = (content_type or "").lower().strip()

    if not safe_file_name or extension not in SUPPORTED_CONTENT_TYPES:
        raise ResumeSourceImportUnsupportedTypeError(
            "Unsupported resume/profile file type. Upload .txt, .md, .docx, or .pdf."
        )

    allowed_content_types = SUPPORTED_CONTENT_TYPES[extension]
    if normalized_content_type not in allowed_content_types:
        raise ResumeSourceImportUnsupportedTypeError(
            "Unsupported resume/profile file content type."
        )

    if len(content) > MAX_RESUME_SOURCE_IMPORT_BYTES:
        raise ResumeSourceImportTooLargeError(
            "Resume/profile file must be 5 MB or smaller."
        )

    if not content:
        raise ResumeSourceImportUnreadableError("Uploaded file is empty.")

    warnings: list[str] = []
    extracted_text = _extract_text(extension, content, warnings)
    normalized_text = _normalize_extracted_text(extracted_text)

    if not normalized_text:
        if extension == ".pdf":
            raise ResumeSourceImportUnreadableError(
                "No readable text could be extracted from this PDF. Scanned or image-based PDFs require OCR, which is not supported yet."
            )
        raise ResumeSourceImportUnreadableError(
            "No readable text could be extracted from this file."
        )

    return ResumeSourceImportResult(
        file_name=safe_file_name,
        file_type=extension.removeprefix("."),
        content_type=normalized_content_type,
        size_bytes=len(content),
        character_count=len(normalized_text),
        warnings=warnings,
        extracted_text=normalized_text,
    )


def _extract_text(extension: str, content: bytes, warnings: list[str]) -> str:
    if extension in {".txt", ".md"}:
        return _extract_text_file(content)
    if extension == ".docx":
        return _extract_docx(content)
    if extension == ".pdf":
        return _extract_pdf(content, warnings)
    raise ResumeSourceImportUnsupportedTypeError("Unsupported resume/profile file type.")


def _extract_text_file(content: bytes) -> str:
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ResumeSourceImportUnreadableError(
            "Text files must be UTF-8 encoded."
        ) from exc


def _extract_docx(content: bytes) -> str:
    try:
        document = Document(BytesIO(content))
    except Exception as exc:
        raise ResumeSourceImportUnreadableError(
            "The .docx file could not be read."
        ) from exc

    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n\n".join(paragraphs)


def _extract_pdf(content: bytes, warnings: list[str]) -> str:
    try:
        reader = PdfReader(BytesIO(content))
    except Exception as exc:
        raise ResumeSourceImportUnreadableError(
            "The PDF file could not be read."
        ) from exc

    if reader.is_encrypted:
        raise ResumeSourceImportUnreadableError(
            "Encrypted PDFs are not supported for local import."
        )

    pages: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append(page_text)

    if len(reader.pages) > 0 and not pages:
        warnings.append("No embedded text was found in the PDF.")

    return "\n\n".join(pages)


def _normalize_extracted_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in normalized.split("\n")]
    return "\n".join(lines).strip()
