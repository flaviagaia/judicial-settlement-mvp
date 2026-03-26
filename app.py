from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.graphing import build_case_graph, graph_to_plotly
from src.pipeline import ensure_demo_assets, run_pipeline


st.set_page_config(
    page_title="Judicial Settlement MVP",
    page_icon="⚖️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp { background: #08111f; color: #ecf3ff; }
    [data-testid="stSidebar"] { background: #0d1728; }
    .metric-card { padding: 1rem; border: 1px solid rgba(255,255,255,.08); border-radius: 16px; background: rgba(255,255,255,.03); }
    </style>
    """,
    unsafe_allow_html=True,
)


def _save_upload(uploaded_file) -> Path:
    runtime_uploads = Path("data/runtime/uploads")
    runtime_uploads.mkdir(parents=True, exist_ok=True)
    destination = runtime_uploads / uploaded_file.name
    destination.write_bytes(uploaded_file.getbuffer())
    return destination


history, sample_pdfs = ensure_demo_assets()

st.title("MVP de proposta de acordo judicial")
st.caption(
    "Upload do PDF, enriquecimento de dados, grafo relacional, casos similares e proposta explicável."
)

with st.sidebar:
    st.subheader("Entrada do caso")
    selected_sample = st.selectbox(
        "Ou selecione um PDF demo",
        options=["Nenhum"] + [path.name for path in sample_pdfs],
        index=1,
    )
    uploaded_pdf = st.file_uploader("Enviar PDF do processo", type=["pdf"])

pdf_path: Path | None = None
if uploaded_pdf is not None:
    pdf_path = _save_upload(uploaded_pdf)
elif selected_sample != "Nenhum":
    pdf_path = next(path for path in sample_pdfs if path.name == selected_sample)

if not pdf_path:
    st.info("Envie um PDF ou use um dos casos demo para ver o MVP em funcionamento.")
    st.stop()

artifacts = run_pipeline(pdf_path)
graph = build_case_graph(artifacts.extracted_case, artifacts.enrichment.similar_cases)
graph_figure = graph_to_plotly(graph)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Chance estimada de aceite", f"{artifacts.proposal.acceptance_probability * 100:.1f}%")
col2.metric("Proposta à vista", f"R$ {artifacts.proposal.suggested_cash_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col3.metric("Parcelamento sugerido", f"{artifacts.proposal.installment_count}x de R$ {artifacts.proposal.suggested_installment_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col4.metric("Casos similares", str(len(artifacts.enrichment.similar_cases)))

tab1, tab2, tab3, tab4 = st.tabs(["PDF e extração", "Enriquecimento", "Grafo", "Proposta final"])

with tab1:
    st.subheader("Campos estruturados extraídos do PDF")
    extracted_df = pd.DataFrame([artifacts.extracted_case.model_dump()])
    st.dataframe(extracted_df, use_container_width=True)
    with st.expander("Texto bruto extraído"):
        st.text(artifacts.extracted_case.raw_text)

with tab2:
    st.subheader("Fontes externas e histórico usado para enriquecer a base")
    st.dataframe(artifacts.enrichment.external_snapshot, use_container_width=True)
    st.markdown("**Casos similares recuperados**")
    st.dataframe(
        artifacts.enrichment.similar_cases[
            [
                "case_id",
                "subject",
                "defendant",
                "phase",
                "claim_value",
                "agreement_accepted",
                "settlement_value",
                "similarity",
                "source_mix",
            ]
        ],
        use_container_width=True,
    )

with tab3:
    st.subheader("Relações jurídicas e contexto relacional")
    st.plotly_chart(graph_figure, use_container_width=True)
    st.caption(
        "O grafo mostra o processo atual ligado a partes, classe, assunto, tribunal e casos historicamente semelhantes."
    )

with tab4:
    st.subheader("Proposta sugerida")
    st.markdown(
        f"""
        - **Modelo baseline:** `{artifacts.proposal.model_name}`
        - **Probabilidade estimada de aceite:** `{artifacts.proposal.acceptance_probability * 100:.1f}%`
        - **Faixa sugerida à vista:** `R$ {artifacts.proposal.suggested_cash_value:,.2f}`  
        - **Alternativa parcelada:** `{artifacts.proposal.installment_count}x de R$ {artifacts.proposal.suggested_installment_value:,.2f}`
        """.replace(",", "X").replace(".", ",").replace("X", ".")
    )
    st.markdown("**Principais fatores explicativos**")
    for driver in artifacts.proposal.top_drivers:
        st.write(f"- {driver}")
    st.markdown("**Justificativa técnica**")
    st.write(artifacts.proposal.narrative)
    st.info(
        "Este MVP usa base controlada e enriquecimento simulado para demonstrar a arquitetura proposta. "
        "O próximo passo é trocar os conectores simulados por integrações reais com fontes como DataJud, diários e APIs parceiras."
    )

