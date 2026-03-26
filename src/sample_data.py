from __future__ import annotations

from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
RUNTIME_DIR = DATA_DIR / "runtime"


HISTORY_ROWS = [
    {
        "case_id": "H001",
        "process_number": "0823456-12.2023.8.19.0001",
        "case_class": "Procedimento Comum Cível",
        "subject": "Cobrança indevida",
        "court": "TJRJ",
        "court_division": "5ª Vara Cível da Capital",
        "plaintiff": "Mariana Souza",
        "defendant": "Energia Leste S.A.",
        "phase": "instrucao",
        "claim_value": 12800.0,
        "has_hearing": 1,
        "days_open": 210,
        "movements_count": 11,
        "prior_settlement_attempt": 1,
        "agreement_accepted": 1,
        "settlement_value": 8400.0,
        "settlement_ratio": 0.656,
        "source_mix": "datajud+publicacoes",
    },
    {
        "case_id": "H002",
        "process_number": "0819191-44.2023.8.19.0001",
        "case_class": "Procedimento Comum Cível",
        "subject": "Cobrança indevida",
        "court": "TJRJ",
        "court_division": "3ª Vara Cível da Capital",
        "plaintiff": "Carlos Ferreira",
        "defendant": "Energia Leste S.A.",
        "phase": "saneamento",
        "claim_value": 9700.0,
        "has_hearing": 1,
        "days_open": 180,
        "movements_count": 9,
        "prior_settlement_attempt": 0,
        "agreement_accepted": 1,
        "settlement_value": 6400.0,
        "settlement_ratio": 0.66,
        "source_mix": "datajud+diario",
    },
    {
        "case_id": "H003",
        "process_number": "0804545-92.2024.8.19.0001",
        "case_class": "Procedimento Comum Cível",
        "subject": "Fatura contestada",
        "court": "TJRJ",
        "court_division": "7ª Vara Cível da Capital",
        "plaintiff": "Renata Costa",
        "defendant": "Energia Leste S.A.",
        "phase": "conhecimento_inicial",
        "claim_value": 5400.0,
        "has_hearing": 0,
        "days_open": 85,
        "movements_count": 5,
        "prior_settlement_attempt": 0,
        "agreement_accepted": 1,
        "settlement_value": 3500.0,
        "settlement_ratio": 0.648,
        "source_mix": "datajud",
    },
    {
        "case_id": "H004",
        "process_number": "0813131-88.2023.8.19.0002",
        "case_class": "Procedimento Comum Cível",
        "subject": "Dano moral por negativacao",
        "court": "TJRJ",
        "court_division": "2ª Vara Cível de Niterói",
        "plaintiff": "Paulo Mendes",
        "defendant": "Financeira Atlântico S.A.",
        "phase": "instrucao",
        "claim_value": 22000.0,
        "has_hearing": 1,
        "days_open": 260,
        "movements_count": 13,
        "prior_settlement_attempt": 1,
        "agreement_accepted": 0,
        "settlement_value": 0.0,
        "settlement_ratio": 0.0,
        "source_mix": "datajud+publicacoes",
    },
    {
        "case_id": "H005",
        "process_number": "0809191-17.2022.8.19.0002",
        "case_class": "Procedimento Comum Cível",
        "subject": "Dano moral por negativacao",
        "court": "TJRJ",
        "court_division": "4ª Vara Cível de Niterói",
        "plaintiff": "Julia Santos",
        "defendant": "Financeira Atlântico S.A.",
        "phase": "execucao",
        "claim_value": 18000.0,
        "has_hearing": 1,
        "days_open": 410,
        "movements_count": 18,
        "prior_settlement_attempt": 1,
        "agreement_accepted": 1,
        "settlement_value": 9800.0,
        "settlement_ratio": 0.544,
        "source_mix": "datajud+diario+publicacoes",
    },
    {
        "case_id": "H006",
        "process_number": "0811010-77.2024.8.19.0003",
        "case_class": "Juizado Especial Cível",
        "subject": "Falha na prestacao de servico",
        "court": "TJRJ",
        "court_division": "1º JEC da Capital",
        "plaintiff": "Aline Ribeiro",
        "defendant": "Conecta Telecom S.A.",
        "phase": "audiencia",
        "claim_value": 6800.0,
        "has_hearing": 1,
        "days_open": 120,
        "movements_count": 7,
        "prior_settlement_attempt": 0,
        "agreement_accepted": 1,
        "settlement_value": 4300.0,
        "settlement_ratio": 0.632,
        "source_mix": "datajud+publicacoes",
    },
    {
        "case_id": "H007",
        "process_number": "0820000-21.2023.8.19.0003",
        "case_class": "Juizado Especial Cível",
        "subject": "Falha na prestacao de servico",
        "court": "TJRJ",
        "court_division": "3º JEC da Capital",
        "plaintiff": "Diego Martins",
        "defendant": "Conecta Telecom S.A.",
        "phase": "conhecimento_inicial",
        "claim_value": 3900.0,
        "has_hearing": 0,
        "days_open": 70,
        "movements_count": 4,
        "prior_settlement_attempt": 0,
        "agreement_accepted": 1,
        "settlement_value": 2100.0,
        "settlement_ratio": 0.538,
        "source_mix": "datajud",
    },
    {
        "case_id": "H008",
        "process_number": "0814141-33.2023.8.19.0004",
        "case_class": "Juizado Especial Cível",
        "subject": "Interrupcao de servico essencial",
        "court": "TJRJ",
        "court_division": "JEC de Duque de Caxias",
        "plaintiff": "Tatiane Lima",
        "defendant": "Energia Leste S.A.",
        "phase": "audiencia",
        "claim_value": 7600.0,
        "has_hearing": 1,
        "days_open": 140,
        "movements_count": 8,
        "prior_settlement_attempt": 1,
        "agreement_accepted": 1,
        "settlement_value": 4700.0,
        "settlement_ratio": 0.618,
        "source_mix": "datajud+diario",
    },
    {
        "case_id": "H009",
        "process_number": "0807070-91.2022.8.19.0004",
        "case_class": "Juizado Especial Cível",
        "subject": "Interrupcao de servico essencial",
        "court": "TJRJ",
        "court_division": "JEC de Nova Iguaçu",
        "plaintiff": "Fabio Gomes",
        "defendant": "Energia Leste S.A.",
        "phase": "execucao",
        "claim_value": 11200.0,
        "has_hearing": 1,
        "days_open": 320,
        "movements_count": 15,
        "prior_settlement_attempt": 1,
        "agreement_accepted": 0,
        "settlement_value": 0.0,
        "settlement_ratio": 0.0,
        "source_mix": "datajud+publicacoes",
    },
    {
        "case_id": "H010",
        "process_number": "0826262-51.2024.8.19.0005",
        "case_class": "Procedimento Comum Cível",
        "subject": "Negativacao indevida",
        "court": "TJRJ",
        "court_division": "1ª Vara Cível de São Gonçalo",
        "plaintiff": "Bruna Nascimento",
        "defendant": "Financeira Atlântico S.A.",
        "phase": "conhecimento_inicial",
        "claim_value": 14500.0,
        "has_hearing": 0,
        "days_open": 95,
        "movements_count": 6,
        "prior_settlement_attempt": 0,
        "agreement_accepted": 0,
        "settlement_value": 0.0,
        "settlement_ratio": 0.0,
        "source_mix": "datajud",
    },
    {
        "case_id": "H011",
        "process_number": "0818181-14.2023.8.19.0005",
        "case_class": "Procedimento Comum Cível",
        "subject": "Negativacao indevida",
        "court": "TJRJ",
        "court_division": "2ª Vara Cível de São Gonçalo",
        "plaintiff": "Marcelo Dias",
        "defendant": "Financeira Atlântico S.A.",
        "phase": "saneamento",
        "claim_value": 16900.0,
        "has_hearing": 1,
        "days_open": 190,
        "movements_count": 10,
        "prior_settlement_attempt": 1,
        "agreement_accepted": 1,
        "settlement_value": 9700.0,
        "settlement_ratio": 0.574,
        "source_mix": "datajud+diario",
    },
    {
        "case_id": "H012",
        "process_number": "0803333-66.2024.8.19.0006",
        "case_class": "Juizado Especial Cível",
        "subject": "Cobranca de servico nao contratado",
        "court": "TJRJ",
        "court_division": "JEC de Campo Grande",
        "plaintiff": "Helena Vieira",
        "defendant": "Conecta Telecom S.A.",
        "phase": "conhecimento_inicial",
        "claim_value": 5100.0,
        "has_hearing": 0,
        "days_open": 60,
        "movements_count": 4,
        "prior_settlement_attempt": 0,
        "agreement_accepted": 1,
        "settlement_value": 2800.0,
        "settlement_ratio": 0.549,
        "source_mix": "datajud",
    },
]


SAMPLE_CASES = [
    {
        "filename": "caso_energia_cobranca.pdf",
        "process_number": "0839393-11.2025.8.19.0001",
        "court": "TJRJ",
        "court_division": "6ª Vara Cível da Capital",
        "case_class": "Procedimento Comum Cível",
        "subject": "Cobrança indevida",
        "plaintiff": "Patricia Almeida",
        "defendant": "Energia Leste S.A.",
        "phase": "saneamento",
        "claim_value": 11850.0,
        "document_date": "2025-09-14",
        "document_type": "peticao_inicial",
        "requested_relief": "revisão de fatura, devolução em dobro e dano moral",
        "text_blocks": [
            "Petição inicial com pedido de revisão de cobrança por consumo não reconhecido.",
            "A autora informa tentativas administrativas sem composição amigável.",
            "Há pedido de audiência de conciliação e indicação de documentos anexos.",
        ],
    },
    {
        "filename": "caso_financeira_negativacao.pdf",
        "process_number": "0840404-22.2025.8.19.0002",
        "court": "TJRJ",
        "court_division": "3ª Vara Cível de Niterói",
        "case_class": "Procedimento Comum Cível",
        "subject": "Negativação indevida",
        "plaintiff": "Rafael Pires",
        "defendant": "Financeira Atlântico S.A.",
        "phase": "instrucao",
        "claim_value": 17600.0,
        "document_date": "2025-10-03",
        "document_type": "contestacao",
        "requested_relief": "retirada do apontamento e indenização por dano moral",
        "text_blocks": [
            "Contestação menciona proposta extrajudicial anterior sem aceite das partes.",
            "Há discussão sobre score de crédito e impacto reputacional.",
            "O processo já possui audiência designada para tentativa de conciliação.",
        ],
    },
]


def ensure_directories() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)


def build_history_frame() -> pd.DataFrame:
    ensure_directories()
    df = pd.DataFrame(HISTORY_ROWS)
    df.to_csv(RAW_DIR / "historical_cases.csv", index=False)
    return df


def _write_pdf(path: Path, case: dict) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    cursor = height - 60
    lines = [
        f"Documento: {case['document_type'].replace('_', ' ').title()}",
        f"Processo CNJ: {case['process_number']}",
        f"Tribunal: {case['court']}",
        f"Vara/Unidade: {case['court_division']}",
        f"Classe processual: {case['case_class']}",
        f"Assunto principal: {case['subject']}",
        f"Autor(a): {case['plaintiff']}",
        f"Ré(u): {case['defendant']}",
        f"Fase atual: {case['phase']}",
        f"Valor atribuído à causa: R$ {case['claim_value']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        f"Data do documento: {case['document_date']}",
        f"Pedido principal: {case['requested_relief']}",
        "",
        *case["text_blocks"],
    ]
    c.setFont("Helvetica", 11)
    for line in lines:
        c.drawString(50, cursor, line)
        cursor -= 20
    c.save()


def ensure_sample_pdfs() -> list[Path]:
    ensure_directories()
    paths: list[Path] = []
    for case in SAMPLE_CASES:
        path = RAW_DIR / case["filename"]
        if not path.exists():
            _write_pdf(path, case)
        paths.append(path)
    return paths

