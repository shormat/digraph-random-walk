"""Graph rendering for --show (matplotlib is only imported when this module is used)."""
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

import utils

# Palette: one sequential hue for magnitude, one accent for what is highlighted
BACKGROUND = '#FAFAF7'
INK = '#2B2F36'
MUTED = '#8A919C'
EDGE = '#B9C0C9'
ACCENT = '#E8743B'
VISITS = LinearSegmentedColormap.from_list('visits', ['#DCE9F7', '#7FAEDD', '#2F6DB5', '#163E73'])


def stationaryDistribution(graph):
    """Long-run share of time the random walk spends on each node."""
    weight = 'p' if utils.p else None
    transition = nx.to_numpy_array(graph, weight=weight)
    transition /= transition.sum(axis=1, keepdims=True)

    values, vectors = np.linalg.eig(transition.T)
    pi = np.abs(np.real(vectors[:, np.argmin(np.abs(values - 1))]))
    return pi / pi.sum()


def computeLayout(graph):
    if graph.number_of_nodes() <= 200:
        return nx.kamada_kawai_layout(graph)
    return nx.spring_layout(graph, seed=1)


def drawGraph(graph, v, datas):
    """Build the figure.

    Args:
        graph (DiGraph): the graph
        v (int): start node of the walks
        datas (list): ((path), count, frequency) tuples, most frequent first
    """
    n, m = graph.number_of_nodes(), graph.number_of_edges()
    small = n <= 40
    nodeSize = 900 if small else max(120, 9000 // n)

    pos = computeLayout(graph)
    nodes = list(graph.nodes)
    pi = stationaryDistribution(graph)

    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor=BACKGROUND)
    ax.set_facecolor(BACKGROUND)
    ax.axis('off')

    # Arcs: width follows the probability with -p, curved so that u->v and v->u stay apart
    if utils.p:
        widths = [0.4 + 3.2 * graph[a][b]['p'] for a, b in graph.edges]
    else:
        widths = 1.2 if small else 0.5
    nx.draw_networkx_edges(graph, pos, ax=ax, width=widths, edge_color=EDGE,
                           alpha=0.9 if small else 0.35, arrowstyle='-|>',
                           arrowsize=14 if small else 7, node_size=nodeSize,
                           connectionstyle='arc3,rad=0.12')

    # Most frequent cycle found by the agent
    topPath, topCount, topFreq = datas[0]
    cycle = list(topPath) + [topPath[0]]
    cycleEdges = [(a, b) for a, b in zip(cycle, cycle[1:]) if graph.has_edge(a, b)]
    nx.draw_networkx_edges(graph, pos, ax=ax, edgelist=cycleEdges, width=2.8,
                           edge_color=ACCENT, arrowstyle='-|>', arrowsize=16 if small else 9,
                           node_size=nodeSize, connectionstyle='arc3,rad=0.12')

    # Nodes coloured by long-run visit share, with a white ring to separate overlaps
    drawn = nx.draw_networkx_nodes(graph, pos, ax=ax, nodelist=nodes, node_size=nodeSize,
                                   node_color=pi, cmap=VISITS, vmin=0, vmax=pi.max(),
                                   edgecolors='white', linewidths=1.5)
    nx.draw_networkx_nodes(graph, pos, ax=ax, nodelist=[v], node_size=nodeSize * 1.25,
                           node_color='none', edgecolors=ACCENT, linewidths=3)

    if n <= 60:
        # Light text on dark nodes, dark text on light nodes
        for node, share in zip(nodes, pi):
            x, y = pos[node]
            ax.text(x, y, str(node), ha='center', va='center',
                    fontsize=11 if small else 7, fontweight='bold',
                    color='white' if share > 0.55 * pi.max() else INK)

    if utils.p and m <= 30:
        labels = {(a, b): '%.2f' % graph[a][b]['p'] for a, b in graph.edges}
        nx.draw_networkx_edge_labels(graph, pos, ax=ax, edge_labels=labels, font_size=8,
                                     font_color=MUTED, connectionstyle='arc3,rad=0.12',
                                     bbox=dict(boxstyle='round,pad=0.15', fc=BACKGROUND, ec='none'))

    colorbar = fig.colorbar(drawn, ax=ax, fraction=0.03, pad=0.02)
    colorbar.set_label('Long-run share of time spent by the agent (stationary distribution)',
                       color=MUTED, fontsize=9)
    colorbar.outline.set_visible(False)
    colorbar.ax.tick_params(colors=MUTED, labelsize=8)

    ax.legend(handles=[
        Line2D([], [], marker='o', linestyle='none', markersize=11, markerfacecolor='none',
               markeredgecolor=ACCENT, markeredgewidth=2.5, label='Start node (v = %d)' % v),
        Line2D([], [], color=ACCENT, linewidth=2.8,
               label='Most frequent cycle (%d times, %.1f %%)' % (topCount, 100 * topFreq)),
    ], loc='lower left', frameon=False, fontsize=9, labelcolor=INK)

    mode = 'file probabilities' if utils.p else 'uniform choice'
    ax.set_title('Directed graph · %d nodes · %d arcs · %s' % (n, m, mode),
                 loc='left', color=INK, fontsize=14, fontweight='bold', pad=14)
    fig.tight_layout()
    return fig


def showGraph(graph, v, datas):
    drawGraph(graph, v, datas)
    plt.show()
