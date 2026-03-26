from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .extraction import ExtractedCase


@dataclass
class EnrichmentArtifacts:
    history: pd.DataFrame
    similar_cases: pd.DataFrame
    external_snapshot: pd.DataFrame
    feature_row: pd.DataFrame


def _compose_case_text(df: pd.DataFrame) -> pd.Series:
    return (
        df["case_class"].fillna("")
        + " "
        + df["subject"].fillna("")
        + " "
        + df["phase"].fillna("")
        + " "
        + df["defendant"].fillna("")
    )


def build_enrichment(case: ExtractedCase, history: pd.DataFrame, top_k: int = 5) -> EnrichmentArtifacts:
    enriched = history.copy()
    enriched["case_text"] = _compose_case_text(enriched)

    target_text = f"{case.case_class} {case.subject} {case.phase} {case.defendant}"
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(list(enriched["case_text"]) + [target_text])
    similarities = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    enriched["similarity"] = similarities

    similar_cases = enriched.sort_values(
        by=["similarity", "agreement_accepted", "claim_value"],
        ascending=[False, False, True],
    ).head(top_k).reset_index(drop=True)
    accepted_similar = similar_cases.loc[similar_cases["agreement_accepted"] == 1, "settlement_ratio"]

    defendant_history = enriched[enriched["defendant"] == case.defendant]
    subject_history = enriched[enriched["subject"] == case.subject]
    class_history = enriched[enriched["case_class"] == case.case_class]

    external_snapshot = pd.DataFrame(
        [
            {
                "source": "DataJud (simulado)",
                "signal": "movimentacoes_historicas",
                "value": int(similar_cases["movements_count"].mean()) if not similar_cases.empty else 0,
                "description": "Média de movimentações de casos historicamente semelhantes.",
            },
            {
                "source": "Consulta processual complementar (simulada)",
                "signal": "taxa_acordo_reu",
                "value": round(defendant_history["agreement_accepted"].mean() * 100, 2)
                if not defendant_history.empty
                else 0.0,
                "description": "Taxa histórica de acordo para o mesmo réu na base de apoio.",
            },
            {
                "source": "Publicações/diários (simulados)",
                "signal": "taxa_acordo_assunto",
                "value": round(subject_history["agreement_accepted"].mean() * 100, 2)
                if not subject_history.empty
                else 0.0,
                "description": "Percentual de acordos em casos do mesmo assunto.",
            },
            {
                "source": "Base relacional consolidada",
                "signal": "taxa_acordo_classe",
                "value": round(class_history["agreement_accepted"].mean() * 100, 2)
                if not class_history.empty
                else 0.0,
                "description": "Percentual de acordos em casos da mesma classe processual.",
            },
        ]
    )

    feature_row = pd.DataFrame(
        [
            {
                "case_class": case.case_class,
                "subject": case.subject,
                "phase": case.phase,
                "defendant": case.defendant,
                "claim_value": case.claim_value,
                "movements_count_proxy": int(similar_cases["movements_count"].mean()) if not similar_cases.empty else 0,
                "days_open_proxy": int(similar_cases["days_open"].mean()) if not similar_cases.empty else 0,
                "has_hearing_proxy": int(round(similar_cases["has_hearing"].mean())) if not similar_cases.empty else 0,
                "prior_attempt_proxy": int(round(similar_cases["prior_settlement_attempt"].mean()))
                if not similar_cases.empty
                else 0,
                "defendant_acceptance_rate": defendant_history["agreement_accepted"].mean()
                if not defendant_history.empty
                else 0.0,
                "subject_acceptance_rate": subject_history["agreement_accepted"].mean()
                if not subject_history.empty
                else 0.0,
                "class_acceptance_rate": class_history["agreement_accepted"].mean()
                if not class_history.empty
                else 0.0,
                "similar_cases_acceptance_rate": similar_cases["agreement_accepted"].mean()
                if not similar_cases.empty
                else 0.0,
                "median_settlement_ratio": float(accepted_similar.median()) if not accepted_similar.empty else 0.55,
            }
        ]
    )

    return EnrichmentArtifacts(
        history=enriched,
        similar_cases=similar_cases,
        external_snapshot=external_snapshot,
        feature_row=feature_row,
    )
