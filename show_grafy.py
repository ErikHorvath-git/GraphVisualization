import networkx as nx

def get_sample_graph_1():
    G = nx.Graph()
    positions = {
        1: (7.25, -7.75), 2: (-7.25, -7.5), 3: (-5.25, -3.25),
        4: (4.25, 8.0), 5: (-9.5, 3.5), 6: (-2.5, 4.0),
        7: (2.25, -3.75), 8: (8.5, -2.25), 9: (-0.75, 9.5)
    }
    edges = [
        (1, 2, 4), (1, 3, 2), (2, 3, 5), (2, 4, 10),
        (3, 5, 3), (5, 4, 1), (4, 6, 7), (5, 6, 8), (2, 9, 15)
    ]
    G.add_weighted_edges_from(edges)
    return G, positions

def get_sample_graph_2():
    G = nx.Graph()
    positions = {
        1: (7.0, -7.5), 2: (-7.0, -7.25), 3: (-5.0, -3.0),
        4: (4.0, 7.5), 5: (-9.0, 3.25), 6: (-2.25, 3.75)
    }
    edges = [
        (1, 2, 6), (1, 3, 1), (2, 3, 2), (2, 4, 3),
        (3, 5, 4), (4, 5, 5), (4, 6, 6), (5, 6, 7)
    ]
    G.add_weighted_edges_from(edges)
    return G, positions

def get_directed_graph():
    G = nx.DiGraph()
    positions = {
        1: (6.75, -7.25), 2: (-6.75, -7.0), 3: (-4.75, -2.75),
        4: (3.75, 7.0), 5: (-8.5, 3.0), 6: (-2.0, 3.5)
    }
    edges = [
        (1, 2, 2), (1, 3, 3), (2, 4, 1), (3, 4, 4),
        (4, 5, 5), (2, 5, 8), (5, 6, 2)
    ]
    G.add_weighted_edges_from(edges)
    return G, positions

def get_complex_graph():
    G = nx.Graph()
    positions = {
        1: (7.5, -8.0), 2: (-7.5, -7.75), 3: (-5.5, -3.5),
        4: (4.5, 8.25), 5: (-9.75, 3.75), 6: (-2.75, 4.25),
        7: (2.5, -4.0), 8: (8.75, -2.5), 9: (-1.0, 9.75), 10: (0.5, -8.5)
    }
    edges = [
        (1, 2, 1), (1, 3, 2), (2, 4, 3), (3, 4, 4),
        (4, 5, 5), (5, 6, 6), (6, 7, 7), (7, 8, 8),
        (8, 9, 9), (9, 10, 10), (10, 1, 11)
    ]
    G.add_weighted_edges_from(edges)
    return G, positions