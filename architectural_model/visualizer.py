import plotly.graph_objects as go
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, Any, List
import json
import base64
from io import BytesIO

class ModelVisualizer:
    @staticmethod
    def visualize_uml(uml_dot: str) -> str:
        """Convert UML DOT to an interactive Plotly figure"""
        # Create a NetworkX graph from the DOT string
        G = nx.DiGraph()
        
        # Parse the DOT string (simplified parsing for this example)
        lines = uml_dot.split('\n')
        for line in lines:
            if '->' in line:
                source, target = line.split('->')
                source = source.strip()
                target = target.split('[')[0].strip()
                G.add_edge(source, target)
            elif '[' in line and 'label' in line:
                node = line.split('[')[0].strip()
                label = line.split('label="')[1].split('"')[0]
                G.add_node(node, label=label)

        # Create Plotly figure
        pos = nx.spring_layout(G)
        
        edge_trace = go.Scatter(
            x=[], y=[],
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += tuple([x0, x1, None])
            edge_trace['y'] += tuple([y0, y1, None])

        node_trace = go.Scatter(
            x=[], y=[],
            mode='markers+text',
            hoverinfo='text',
            text=[],
            textposition="bottom center",
            marker=dict(
                showscale=False,
                color='lightblue',
                size=40,
                line=dict(width=2)
            )
        )

        for node in G.nodes():
            x, y = pos[node]
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_trace['text'] += tuple([G.nodes[node].get('label', node)])

        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                       ))

        # Convert figure to HTML
        return fig.to_html(full_html=False)

    @staticmethod
    def visualize_4plus1(views: Dict[str, Any]) -> str:
        """Create an interactive dashboard for 4+1 views"""
        # Create a figure with subplots for each view
        fig = go.Figure()

        # Add traces for each view
        for view_name, view_data in views.items():
            if view_name == "logical_view":
                # Create a network graph for logical view
                G = nx.DiGraph()
                for component in view_data["components"]:
                    G.add_node(component["name"], type=component["type"])
                for rel in view_data["relationships"]:
                    G.add_edge(rel["source"], rel["target"])

                pos = nx.spring_layout(G)
                for edge in G.edges():
                    fig.add_trace(go.Scatter(
                        x=[pos[edge[0]][0], pos[edge[1]][0]],
                        y=[pos[edge[0]][1], pos[edge[1]][1]],
                        mode='lines',
                        name=f"{edge[0]}-{edge[1]}"
                    ))

                for node in G.nodes():
                    fig.add_trace(go.Scatter(
                        x=[pos[node][0]],
                        y=[pos[node][1]],
                        mode='markers+text',
                        name=node,
                        text=node,
                        textposition="bottom center"
                    ))

        fig.update_layout(
            title="4+1 View Model Visualization",
            showlegend=True,
            hovermode='closest'
        )

        return fig.to_html(full_html=False)

    @staticmethod
    def visualize_adl(adl_text: str) -> str:
        """Create a hierarchical visualization for ADL"""
        # Parse ADL text into a structured format
        components = []
        connectors = []
        
        current_component = None
        for line in adl_text.split('\n'):
            if 'component' in line:
                current_component = line.split('component')[1].split('{')[0].strip()
                components.append(current_component)
            elif 'connector' in line:
                connector = line.split('connector')[1].split('{')[0].strip()
                connectors.append(connector)

        # Create a sunburst chart
        fig = go.Figure(go.Sunburst(
            labels=components + connectors,
            parents=[''] * len(components) + components[:len(connectors)],
            values=[1] * (len(components) + len(connectors))
        ))

        fig.update_layout(
            title="ADL Architecture Visualization",
            margin=dict(t=0, l=0, r=0, b=0)
        )

        return fig.to_html(full_html=False)

    @staticmethod
    def save_plot_to_base64(fig) -> str:
        """Convert a matplotlib figure to base64 string"""
        buf = BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8') 