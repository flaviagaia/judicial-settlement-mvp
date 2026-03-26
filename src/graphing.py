from __future__ import annotations

import math

import networkx as nx
import pandas as pd
import plotly.graph_objects as go

from .extraction import ExtractedCase


def _build_similarity_reasons(case: ExtractedCase, row: pd.Series) -> list[str]:
    reasons: list[str] = []
    if row["defendant"] == case.defendant:
        reasons.append("mesmo réu")
    if row["subject"] == case.subject:
        reasons.append("mesmo assunto")
    if row["case_class"] == case.case_class:
        reasons.append("mesma classe")
    if row["court"] == case.court:
        reasons.append("mesmo tribunal")
    if row["phase"] == case.phase:
        reasons.append("mesma fase")
    return reasons


def build_case_graph(case: ExtractedCase, similar_cases: pd.DataFrame) -> nx.Graph:
    graph = nx.Graph()
    case_node = f"processo:{case.process_number}"
    graph.add_node(
        case_node,
        label="Processo atual",
        kind="process",
        hover=(
            f"<b>Processo atual</b><br>"
            f"CNJ: {case.process_number}<br>"
            f"Classe: {case.case_class}<br>"
            f"Assunto: {case.subject}<br>"
            f"Fase: {case.phase}<br>"
            f"Réu: {case.defendant}<br>"
            f"Valor da causa: R$ {case.claim_value:,.2f}"
        ).replace(",", "X").replace(".", ",").replace("X", "."),
    )
    graph.add_node(
        f"autor:{case.plaintiff}",
        label=case.plaintiff,
        kind="party",
        hover=f"<b>Parte autora</b><br>{case.plaintiff}",
    )
    graph.add_node(
        f"reu:{case.defendant}",
        label=case.defendant,
        kind="party",
        hover=f"<b>Parte ré</b><br>{case.defendant}",
    )
    graph.add_node(
        f"classe:{case.case_class}",
        label=case.case_class,
        kind="class",
        hover=f"<b>Classe processual</b><br>{case.case_class}",
    )
    graph.add_node(
        f"assunto:{case.subject}",
        label=case.subject,
        kind="subject",
        hover=f"<b>Assunto</b><br>{case.subject}",
    )
    graph.add_node(
        f"tribunal:{case.court}",
        label=case.court,
        kind="court",
        hover=f"<b>Tribunal</b><br>{case.court}",
    )

    graph.add_edge(case_node, f"autor:{case.plaintiff}", relation="tem_autor")
    graph.add_edge(case_node, f"reu:{case.defendant}", relation="tem_reu")
    graph.add_edge(case_node, f"classe:{case.case_class}", relation="tem_classe")
    graph.add_edge(case_node, f"assunto:{case.subject}", relation="tem_assunto")
    graph.add_edge(case_node, f"tribunal:{case.court}", relation="tramita_em")

    for _, row in similar_cases.head(4).iterrows():
        similar_node = f"similar:{row['case_id']}"
        reasons = _build_similarity_reasons(case, row)
        reasons_text = ", ".join(reasons) if reasons else "similaridade textual"
        graph.add_node(
            similar_node,
            label=f"{row['case_id']} | {'acordo' if row['agreement_accepted'] else 'sem acordo'}",
            kind="similar_case",
            hover=(
                f"<b>Caso semelhante {row['case_id']}</b><br>"
                f"Processo: {row['process_number']}<br>"
                f"Classe: {row['case_class']}<br>"
                f"Assunto: {row['subject']}<br>"
                f"Fase: {row['phase']}<br>"
                f"Réu: {row['defendant']}<br>"
                f"Similaridade textual: {row['similarity']:.2f}<br>"
                f"Base da relação: {reasons_text}<br>"
                f"Outcome histórico: {'acordo aceito' if row['agreement_accepted'] else 'sem acordo'}<br>"
                f"Valor negociado: R$ {row['settlement_value']:,.2f}"
            ).replace(",", "X").replace(".", ",").replace("X", "."),
        )
        graph.add_edge(
            case_node,
            similar_node,
            relation=f"similaridade textual {row['similarity']:.2f}",
        )
        if row["defendant"] == case.defendant:
            graph.add_edge(similar_node, f"reu:{row['defendant']}", relation="mesmo réu")
        if row["subject"] == case.subject:
            graph.add_edge(similar_node, f"assunto:{row['subject']}", relation="mesmo assunto")
        if row["case_class"] == case.case_class:
            graph.add_edge(similar_node, f"classe:{row['case_class']}", relation="mesma classe")
        if row["court"] == case.court:
            graph.add_edge(similar_node, f"tribunal:{row['court']}", relation="mesmo tribunal")
    return graph


def graph_to_plotly(graph: nx.Graph) -> go.Figure:
    if not graph.nodes:
        return go.Figure()

    positions = nx.spring_layout(graph, seed=42, k=1.4 / math.sqrt(max(len(graph.nodes), 1)))
    edge_x: list[float] = []
    edge_y: list[float] = []
    edge_hover_x: list[float] = []
    edge_hover_y: list[float] = []
    edge_hover_texts: list[str] = []
    for source, target in graph.edges():
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_hover_x.append((x0 + x1) / 2)
        edge_hover_y.append((y0 + y1) / 2)
        source_label = graph.nodes[source].get("label", source)
        target_label = graph.nodes[target].get("label", target)
        relation = graph.edges[source, target].get("relation", "relacionado")
        edge_hover_texts.append(
            f"<b>Conexão</b><br>{source_label} → {target_label}<br>Base: {relation}"
        )

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line={"width": 1, "color": "#6b7280"},
        hoverinfo="none",
    )
    edge_hover_trace = go.Scatter(
        x=edge_hover_x,
        y=edge_hover_y,
        mode="markers",
        marker={"size": 10, "color": "rgba(0,0,0,0)"},
        hovertemplate="%{text}<extra></extra>",
        text=edge_hover_texts,
        showlegend=False,
    )

    node_x: list[float] = []
    node_y: list[float] = []
    labels: list[str] = []
    colors: list[str] = []
    hover_texts: list[str] = []
    palette = {
        "process": "#f97316",
        "party": "#38bdf8",
        "class": "#a78bfa",
        "subject": "#34d399",
        "court": "#facc15",
        "similar_case": "#fb7185",
    }
    for node, attrs in graph.nodes(data=True):
        x, y = positions[node]
        node_x.append(x)
        node_y.append(y)
        labels.append(attrs.get("label", node))
        colors.append(palette.get(attrs.get("kind", "process"), "#e5e7eb"))
        hover_texts.append(attrs.get("hover", attrs.get("label", node)))

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=labels,
        textposition="top center",
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_texts,
        marker={"size": 18, "color": colors, "line": {"width": 1, "color": "#111827"}},
    )

    return go.Figure(
        data=[edge_trace, edge_hover_trace, node_trace],
        layout=go.Layout(
            paper_bgcolor="#0b1220",
            plot_bgcolor="#0b1220",
            font={"color": "#e5e7eb"},
            margin={"l": 20, "r": 20, "t": 20, "b": 20},
            xaxis={"showgrid": False, "zeroline": False, "visible": False},
            yaxis={"showgrid": False, "zeroline": False, "visible": False},
            showlegend=False,
        ),
    )
