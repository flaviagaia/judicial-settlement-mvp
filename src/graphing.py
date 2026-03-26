from __future__ import annotations

import math

import networkx as nx
import pandas as pd
import plotly.graph_objects as go

from .extraction import ExtractedCase


def build_case_graph(case: ExtractedCase, similar_cases: pd.DataFrame) -> nx.Graph:
    graph = nx.Graph()
    case_node = f"processo:{case.process_number}"
    graph.add_node(case_node, label="Processo atual", kind="process")
    graph.add_node(f"autor:{case.plaintiff}", label=case.plaintiff, kind="party")
    graph.add_node(f"reu:{case.defendant}", label=case.defendant, kind="party")
    graph.add_node(f"classe:{case.case_class}", label=case.case_class, kind="class")
    graph.add_node(f"assunto:{case.subject}", label=case.subject, kind="subject")
    graph.add_node(f"tribunal:{case.court}", label=case.court, kind="court")

    graph.add_edge(case_node, f"autor:{case.plaintiff}", relation="tem_autor")
    graph.add_edge(case_node, f"reu:{case.defendant}", relation="tem_reu")
    graph.add_edge(case_node, f"classe:{case.case_class}", relation="tem_classe")
    graph.add_edge(case_node, f"assunto:{case.subject}", relation="tem_assunto")
    graph.add_edge(case_node, f"tribunal:{case.court}", relation="tramita_em")

    for _, row in similar_cases.head(4).iterrows():
        similar_node = f"similar:{row['case_id']}"
        graph.add_node(
            similar_node,
            label=f"{row['case_id']} | {'acordo' if row['agreement_accepted'] else 'sem acordo'}",
            kind="similar_case",
        )
        graph.add_edge(case_node, similar_node, relation=f"similaridade {row['similarity']:.2f}")
        graph.add_edge(similar_node, f"reu:{row['defendant']}", relation="mesmo_reu")
        graph.add_edge(similar_node, f"assunto:{row['subject']}", relation="mesmo_assunto")
    return graph


def graph_to_plotly(graph: nx.Graph) -> go.Figure:
    if not graph.nodes:
        return go.Figure()

    positions = nx.spring_layout(graph, seed=42, k=1.4 / math.sqrt(max(len(graph.nodes), 1)))
    edge_x: list[float] = []
    edge_y: list[float] = []
    for source, target in graph.edges():
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line={"width": 1, "color": "#6b7280"},
        hoverinfo="none",
    )

    node_x: list[float] = []
    node_y: list[float] = []
    labels: list[str] = []
    colors: list[str] = []
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

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=labels,
        textposition="top center",
        hoverinfo="text",
        marker={"size": 18, "color": colors, "line": {"width": 1, "color": "#111827"}},
    )

    return go.Figure(
        data=[edge_trace, node_trace],
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

