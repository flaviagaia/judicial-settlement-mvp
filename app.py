from __future__ import annotations

import base64
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


def _render_pdf_preview(pdf_path: Path, height: int = 720) -> None:
    pdf_bytes = pdf_path.read_bytes()
    encoded = base64.b64encode(pdf_bytes).decode("utf-8")
    st.markdown(
        f"""
        <iframe
            src="data:application/pdf;base64,{encoded}"
            width="100%"
            height="{height}"
            style="border:1px solid rgba(255,255,255,.12); border-radius:12px; background:white;"
        ></iframe>
        """,
        unsafe_allow_html=True,
    )


history, sample_pdfs = ensure_demo_assets()

st.title("MVP de proposta de acordo judicial")
st.caption(
    "Upload do PDF, enriquecimento de dados, grafo relacional, casos similares e proposta explicável."
)

with st.expander("Visão técnica da arquitetura", expanded=False):
    st.markdown(
        """
        **Pipeline demonstrado neste MVP**
        1. Ingestão do PDF e extração de campos estruturados.
        2. Consolidação do caso em uma representação canônica.
        3. Enriquecimento com histórico comparável e sinais externos simulados.
        4. Recuperação de casos similares por `TF-IDF + cosine similarity`.
        5. Montagem de um grafo relacional com entidades e comparáveis.
        6. Score baseline com `Logistic Regression`.
        7. Geração de proposta à vista e parcelada com justificativa técnica.
        """
    )
    st.markdown("**Ferramentas e técnicas usadas neste MVP**")
    st.markdown(
        """
        - `Streamlit`: interface de demonstração e inspeção técnica.
        - `reportlab`: geração de PDFs demo controlados.
        - `pypdf`: leitura textual dos PDFs.
        - `regex + parsing orientado a schema`: extração dos campos processuais.
        - `pandas`: consolidação do caso, histórico e artefatos.
        - `TF-IDF + cosine similarity`: recuperação de casos similares.
        - `networkx`: modelagem do grafo relacional.
        - `Plotly`: visualização do grafo no app.
        - `scikit-learn`: pipeline baseline com `OneHotEncoder`, `StandardScaler` e `LogisticRegression`.
        """
    )

with st.sidebar:
    st.subheader("Entrada do caso")
    selected_sample = st.selectbox(
        "Ou selecione um PDF demo",
        options=["Nenhum"] + [path.name for path in sample_pdfs],
        index=1,
    )
    uploaded_pdf = st.file_uploader("Enviar PDF do processo", type=["pdf"])
    st.divider()
    st.subheader("Premissas do MVP")
    st.caption("Camada de dados e modelagem usada nesta versão.")
    st.markdown(
        """
        - Base histórica controlada com acordos e não-acordos.
        - Enriquecimento externo simulado, inspirado em conectores reais.
        - Grafo relacional para contexto e explicabilidade.
        - Modelo baseline tabular focado em legibilidade técnica.
        """
    )
    st.markdown("**Evolução planejada da stack**")
    st.markdown(
        """
        - OCR real com `PaddleOCR`, `PyMuPDF` e `pdfplumber`.
        - Conectores para `DataJud`, diários oficiais e APIs parceiras.
        - Busca vetorial com embeddings jurídicos.
        - Baselines mais fortes com `LightGBM` ou `CatBoost`.
        - Camada de agentes para enriquecimento, revisão e justificativa.
        """
    )

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
feature_row = artifacts.enrichment.feature_row.copy()
feature_row_display = feature_row.T.reset_index()
feature_row_display.columns = ["feature", "value"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Chance estimada de aceite", f"{artifacts.proposal.acceptance_probability * 100:.1f}%")
col2.metric("Proposta à vista", f"R$ {artifacts.proposal.suggested_cash_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col3.metric("Parcelamento sugerido", f"{artifacts.proposal.installment_count}x de R$ {artifacts.proposal.suggested_installment_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col4.metric("Casos similares", str(len(artifacts.enrichment.similar_cases)))

tab1, tab2, tab3, tab4 = st.tabs(["PDF e extração", "Enriquecimento", "Grafo", "Proposta final"])

with tab1:
    st.subheader("Revisão manual do PDF e da extração")
    left, right = st.columns([1.15, 1])
    with left:
        st.markdown("**Preview do documento**")
        st.caption("Use esta visualização para comparar manualmente o PDF com a leitura do sistema.")
        _render_pdf_preview(pdf_path)
    with right:
        st.markdown("**Campos estruturados extraídos do PDF**")
        extracted_df = pd.DataFrame([artifacts.extracted_case.model_dump()])
        st.dataframe(extracted_df, use_container_width=True, height=420)
        st.markdown("**Checklist de validação manual**")
        checklist_df = pd.DataFrame(
            [
                {"campo": "Número CNJ", "valor_extraido": artifacts.extracted_case.process_number},
                {"campo": "Classe processual", "valor_extraido": artifacts.extracted_case.case_class},
                {"campo": "Assunto", "valor_extraido": artifacts.extracted_case.subject},
                {"campo": "Autor(a)", "valor_extraido": artifacts.extracted_case.plaintiff},
                {"campo": "Ré(u)", "valor_extraido": artifacts.extracted_case.defendant},
                {"campo": "Valor da causa", "valor_extraido": f"R$ {artifacts.extracted_case.claim_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")},
                {"campo": "Fase", "valor_extraido": artifacts.extracted_case.phase},
                {"campo": "Pedido principal", "valor_extraido": artifacts.extracted_case.requested_relief},
            ]
        )
        st.dataframe(checklist_df, use_container_width=True, height=280)
    st.markdown("**Leitura técnica**")
    st.markdown(
        """
        - Nesta versão, a leitura do documento usa `pypdf` e parsing por padrões.
        - Os campos extraídos representam a **camada canônica mínima** do caso.
        - O preview do PDF permite validação humana antes de confiar na proposta final.
        - Em produção, esta etapa pode ser substituída por OCR real, chunking documental e extração orientada a schema.
        """
    )
    with st.expander("Texto bruto extraído"):
        st.text(artifacts.extracted_case.raw_text)

with tab2:
    st.subheader("Fontes externas e histórico usado para enriquecer a base")
    st.dataframe(artifacts.enrichment.external_snapshot, use_container_width=True)
    left, right = st.columns([1.1, 1])
    with left:
        st.markdown("**Features consolidadas para o score**")
        st.dataframe(feature_row_display, use_container_width=True)
    with right:
        st.markdown("**Resumo técnico da base histórica**")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "historical_cases": len(history),
                        "accepted_cases": int(history["agreement_accepted"].sum()),
                        "non_accepted_cases": int((history["agreement_accepted"] == 0).sum()),
                        "unique_defendants": history["defendant"].nunique(),
                        "unique_subjects": history["subject"].nunique(),
                    }
                ]
            ),
            use_container_width=True,
        )
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
    st.caption(
        "Os sinais acima simulam uma camada de enriquecimento capaz de receber conectores reais como DataJud, diários oficiais e APIs parceiras."
    )
    with st.expander("Técnicas aplicadas nesta camada"):
        st.markdown(
            """
            - `Entity normalization`: normalização de réu, assunto e classe para consolidar comparáveis.
            - `Weak enrichment`: sinais externos simulados para representar futura integração real.
            - `Case-based retrieval`: ranking de comparáveis com base textual compacta.
            - `Feature engineering`: geração de proxies de tramitação, hearing e tentativa prévia de acordo.
            """
        )

with tab3:
    st.subheader("Relações jurídicas e contexto relacional")
    st.plotly_chart(graph_figure, use_container_width=True)
    st.caption(
        "O grafo mostra o processo atual ligado a partes, classe, assunto, tribunal e casos historicamente semelhantes."
    )
    st.markdown("**Leitura técnica do grafo**")
    st.markdown(
        """
        - O nó central representa o processo recebido.
        - Nós auxiliares representam entidades canônicas e processos semelhantes.
        - As arestas explicitam relações úteis para explicabilidade e navegação do histórico.
        - Em uma fase seguinte, esta camada pode migrar para `Neo4j` ou outra base orientada a grafo.
        """
    )
    st.markdown("**Ferramentas desta camada**")
    st.markdown(
        """
        - `networkx` para construção do grafo.
        - `Plotly` para layout e visualização interativa.
        - abordagem atual: grafo explicativo, não transacional.
        """
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
    st.markdown("**Racional do score**")
    st.markdown(
        """
        O score atual é um baseline supervisionado sobre uma base controlada. Ele não substitui decisão jurídica,
        mas organiza sinais de conciliabilidade em uma saída única para apoiar priorização e composição da proposta.
        """
    )
    st.markdown("**Técnicas do motor de decisão**")
    st.markdown(
        """
        - `Logistic Regression` como baseline de classificação binária.
        - `OneHotEncoder` para variáveis categóricas.
        - `StandardScaler` para variáveis numéricas.
        - heurística de proposta baseada em `median settlement ratio` dos comparáveis.
        - separação entre sinais usados no treino e sinais usados apenas na explicação.
        """
    )
    st.markdown("**Principais fatores explicativos**")
    for driver in artifacts.proposal.top_drivers:
        st.write(f"- {driver}")
    st.markdown("**Justificativa técnica**")
    st.write(artifacts.proposal.narrative)
    with st.expander("Lineagem da proposta e próximos passos"):
        st.markdown(
            """
            **Como a proposta foi montada**
            - o PDF define o contexto inicial do caso;
            - o enriquecimento adiciona taxas históricas e comparáveis;
            - o baseline estima chance de aceite;
            - a proposta usa score + mediana de acordos semelhantes + valor da causa.

            **Como evoluir**
            - integrações reais com DataJud e diários;
            - embeddings jurídicos para retrieval mais forte;
            - features de grafo incorporadas ao modelo;
            - agente explicador com output estruturado.
            """
        )
    st.info(
        "Este MVP usa base controlada e enriquecimento simulado para demonstrar a arquitetura proposta. "
        "O próximo passo é trocar os conectores simulados por integrações reais com fontes como DataJud, diários e APIs parceiras."
    )
