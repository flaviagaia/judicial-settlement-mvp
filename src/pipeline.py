from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .enrichment import EnrichmentArtifacts, build_enrichment
from .extraction import ExtractedCase, extract_case_fields
from .graphing import build_case_graph, graph_to_plotly
from .modeling import ProposalArtifacts, build_proposal
from .sample_data import RAW_DIR, RUNTIME_DIR, build_history_frame, ensure_sample_pdfs


@dataclass
class PipelineArtifacts:
    extracted_case: ExtractedCase
    enrichment: EnrichmentArtifacts
    proposal: ProposalArtifacts
    graph_html_path: Path
    summary: dict


def ensure_demo_assets() -> tuple[pd.DataFrame, list[Path]]:
    history = build_history_frame()
    pdfs = ensure_sample_pdfs()
    return history, pdfs


def run_pipeline(pdf_path: Path) -> PipelineArtifacts:
    history, _ = ensure_demo_assets()
    extracted = extract_case_fields(pdf_path)
    enrichment = build_enrichment(extracted, history)
    proposal = build_proposal(extracted, enrichment.feature_row, history)

    graph = build_case_graph(extracted, enrichment.similar_cases)
    graph_figure = graph_to_plotly(graph)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    graph_html_path = RUNTIME_DIR / "case_graph.html"
    graph_figure.write_html(graph_html_path)

    summary = {
        "process_number": extracted.process_number,
        "defendant": extracted.defendant,
        "similar_cases_found": int(len(enrichment.similar_cases)),
        "acceptance_probability": round(proposal.acceptance_probability, 4),
        "suggested_cash_value": proposal.suggested_cash_value,
        "installment_count": proposal.installment_count,
        "suggested_installment_value": proposal.suggested_installment_value,
        "sources_used": enrichment.external_snapshot["source"].nunique(),
        "graph_nodes": graph.number_of_nodes(),
        "graph_edges": graph.number_of_edges(),
    }

    (RUNTIME_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    enrichment.similar_cases.to_csv(RUNTIME_DIR / "similar_cases.csv", index=False)
    enrichment.external_snapshot.to_csv(RUNTIME_DIR / "external_snapshot.csv", index=False)
    pd.DataFrame([extracted.model_dump()]).to_csv(RUNTIME_DIR / "extracted_case.csv", index=False)

    return PipelineArtifacts(
        extracted_case=extracted,
        enrichment=enrichment,
        proposal=proposal,
        graph_html_path=graph_html_path,
        summary=summary,
    )
