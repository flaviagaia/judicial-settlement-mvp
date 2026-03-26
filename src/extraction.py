from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel
from pypdf import PdfReader


PROCESS_RE = re.compile(r"Processo CNJ:\s*([0-9.\-]+)")
COURT_RE = re.compile(r"Tribunal:\s*(.+)")
DIVISION_RE = re.compile(r"Vara/Unidade:\s*(.+)")
CLASS_RE = re.compile(r"Classe processual:\s*(.+)")
SUBJECT_RE = re.compile(r"Assunto principal:\s*(.+)")
PLAINTIFF_RE = re.compile(r"Autor\(a\):\s*(.+)")
DEFENDANT_RE = re.compile(r"Ré\(u\):\s*(.+)")
PHASE_RE = re.compile(r"Fase atual:\s*(.+)")
VALUE_RE = re.compile(r"Valor atribuído à causa:\s*R\$\s*([0-9\.,]+)")
DATE_RE = re.compile(r"Data do documento:\s*(.+)")
DOC_RE = re.compile(r"Documento:\s*(.+)")
RELIEF_RE = re.compile(r"Pedido principal:\s*(.+)")


class ExtractedCase(BaseModel):
    document_name: str
    process_number: str
    court: str
    court_division: str
    case_class: str
    subject: str
    plaintiff: str
    defendant: str
    phase: str
    claim_value: float
    document_date: str
    document_type: str
    requested_relief: str
    raw_text: str


def extract_text_from_pdf(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    chunks = [(page.extract_text() or "").strip() for page in reader.pages]
    return "\n".join(chunk for chunk in chunks if chunk)


def _extract_required(pattern: re.Pattern[str], text: str, default: str = "") -> str:
    match = pattern.search(text)
    return match.group(1).strip() if match else default


def _parse_brl(value: str) -> float:
    cleaned = value.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def extract_case_fields(pdf_path: Path) -> ExtractedCase:
    text = extract_text_from_pdf(pdf_path)
    return ExtractedCase(
        document_name=pdf_path.name,
        process_number=_extract_required(PROCESS_RE, text, "não identificado"),
        court=_extract_required(COURT_RE, text, "não identificado"),
        court_division=_extract_required(DIVISION_RE, text, "não identificado"),
        case_class=_extract_required(CLASS_RE, text, "não identificado"),
        subject=_extract_required(SUBJECT_RE, text, "não identificado"),
        plaintiff=_extract_required(PLAINTIFF_RE, text, "não identificado"),
        defendant=_extract_required(DEFENDANT_RE, text, "não identificado"),
        phase=_extract_required(PHASE_RE, text, "não identificado"),
        claim_value=_parse_brl(_extract_required(VALUE_RE, text, "0")),
        document_date=_extract_required(DATE_RE, text, "não identificado"),
        document_type=_extract_required(DOC_RE, text, "documento"),
        requested_relief=_extract_required(RELIEF_RE, text, "não identificado"),
        raw_text=text,
    )

