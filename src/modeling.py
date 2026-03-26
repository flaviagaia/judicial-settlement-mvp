from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .extraction import ExtractedCase


@dataclass
class ProposalArtifacts:
    acceptance_probability: float
    suggested_cash_value: float
    suggested_installment_value: float
    installment_count: int
    model_name: str
    top_drivers: list[str]
    narrative: str


MODEL_FEATURE_COLUMNS = [
    "case_class",
    "subject",
    "phase",
    "defendant",
    "claim_value",
    "movements_count_proxy",
    "days_open_proxy",
    "has_hearing_proxy",
    "prior_attempt_proxy",
]


def train_acceptance_model(history: pd.DataFrame) -> Pipeline:
    features = history[
        [
            "case_class",
            "subject",
            "phase",
            "defendant",
            "claim_value",
            "movements_count",
            "days_open",
            "has_hearing",
            "prior_settlement_attempt",
            "agreement_accepted",
        ]
    ].copy()
    features.rename(
        columns={
            "movements_count": "movements_count_proxy",
            "days_open": "days_open_proxy",
            "has_hearing": "has_hearing_proxy",
            "prior_settlement_attempt": "prior_attempt_proxy",
        },
        inplace=True,
    )

    X = features[MODEL_FEATURE_COLUMNS]
    y = history["agreement_accepted"]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                ["case_class", "subject", "phase", "defendant"],
            ),
            (
                "numeric",
                StandardScaler(),
                [
                    "claim_value",
                    "movements_count_proxy",
                    "days_open_proxy",
                    "has_hearing_proxy",
                    "prior_attempt_proxy",
                ],
            ),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=2000, class_weight="balanced")),
        ]
    )
    model.fit(X, y)
    return model


def build_proposal(case: ExtractedCase, feature_row: pd.DataFrame, history: pd.DataFrame) -> ProposalArtifacts:
    model = train_acceptance_model(history)
    probability = float(model.predict_proba(feature_row[MODEL_FEATURE_COLUMNS])[0, 1])

    median_ratio = float(feature_row["median_settlement_ratio"].iloc[0] or 0.55)
    acceptance_anchor = float(feature_row["similar_cases_acceptance_rate"].iloc[0] or 0.5)
    blended_ratio = min(0.85, max(0.35, (median_ratio * 0.7) + (acceptance_anchor * 0.15) + 0.15))
    cash_value = round(case.claim_value * blended_ratio, 2)
    installment_count = 6 if case.claim_value > 10000 else 4
    installment_value = round((cash_value * 1.08) / installment_count, 2)

    top_drivers = [
        f"Taxa histórica de acordo do réu: {feature_row['defendant_acceptance_rate'].iloc[0] * 100:.1f}%",
        f"Taxa histórica do assunto: {feature_row['subject_acceptance_rate'].iloc[0] * 100:.1f}%",
        f"Mediana de acordo em casos similares: {median_ratio * 100:.1f}% do valor da causa",
    ]

    narrative = (
        f"A proposta parte de um score de conciliabilidade de {probability * 100:.1f}% "
        f"e foi ancorada em casos semelhantes envolvendo {case.defendant}, no assunto "
        f"'{case.subject}', com fase processual '{case.phase}'. O valor à vista prioriza "
        f"fechamento rápido, enquanto o parcelamento preserva competitividade negocial "
        f"com pequeno prêmio financeiro."
    )

    return ProposalArtifacts(
        acceptance_probability=probability,
        suggested_cash_value=cash_value,
        suggested_installment_value=installment_value,
        installment_count=installment_count,
        model_name="logistic_regression_baseline",
        top_drivers=top_drivers,
        narrative=narrative,
    )
