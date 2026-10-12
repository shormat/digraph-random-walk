import json
import random
import sys
from collections import Counter

import networkx as nx
import numpy as np

import utils


def loadGraph(name):
    """Load a directed graph from a JSON file.

    Returns:
        (DiGraph, int): the graph and the declared number of nodes (nodeCount)
    """
    try:
        with open(name, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        sys.exit("The file you provided does not exist.")

    nodesNbr = data['nodeCount']
    graph = nx.DiGraph()
    if nodesNbr >= 1:
        graph.add_nodes_from(range(nodesNbr))
    else:
        graph.add_node(nodesNbr)

    for i in range(nodesNbr):
        node = data['nodes'][i]
        for target, prob in zip(node['arcs'], node['p']):
            graph.add_edge(i, target, p=prob)

    if utils.debug:
        print("Number of nodes [nodeCount] = %d" % (nodesNbr + 1))
        print("Number of nodes [iterations] = %d" % (nodesNbr + 1))
        print("Number of nodes [entries in the list] = %d" % len(data['nodes']))
        print("-----")
        for j in range(nodesNbr):
            print(graph.nodes[j])
        print("-----")
        print(graph)

    return graph, nodesNbr


def getAdjMatrix(graph):
    """Adjacency matrix of the graph (int64, nodes in insertion order)."""
    matrix = nx.to_numpy_array(graph, dtype=np.int64, weight=None)

    if utils.debug:
        print(matrix)

    return matrix


def mulMatrix(matrix, n):
    """Matrix raised to the power n."""
    result = np.linalg.matrix_power(matrix, n)

    if utils.debug:
        print("Matrix to the power %d" % n)
        print(result)

    return result


def exactLength(matrixExp, v, size):
    """Share of the length-n walks (A^n) that are closed walks on v."""
    matrixExp = matrixExp.astype(np.float64)  # avoid overflow
    return matrixExp[v, v] / matrixExp[:size, :size].sum()


def atMostLength(matrix, v, n, size):
    """Sum over k = 1..n of A^k[v,v] divided by the running total of all A^1..A^k entries.

    Powers are computed incrementally (A^k = A^(k-1) @ A) instead of from scratch.
    """
    matrix = matrix.astype(np.float64)  # avoid overflow
    value = 0.0
    total = 0.0
    power = np.identity(matrix.shape[0])

    for k in range(1, n + 1):
        power = power @ matrix
        if utils.debug:
            print("Matrix to the power %d" % k)
            print(power)
        total += power[:size, :size].sum()
        value += power[v, v] / total

    return value


def buildSuccessors(graph):
    """Pre-compute, for each node with successors, its successor list and
    (with -p) the cumulative edge probabilities used to draw one of them."""
    successors = {}
    for node in graph.nodes:
        succ = list(graph.successors(node))
        if succ:
            cumulative = np.cumsum([graph[node][s]['p'] for s in succ]).tolist() if utils.p else None
            successors[node] = (succ, cumulative)
    return successors


def paths(graph, v):
    """Random walks from v: 100 runs, each one collects distinct cycles back to v
    until a cycle repeats (or the walk dead-ends).

    Returns:
        Counter: number of runs in which each cycle (tuple of nodes) was found
    """
    successors = buildSuccessors(graph)

    def step(node):
        succ, cumulative = successors[node]
        return random.choices(succ, cum_weights=cumulative)[0]

    # Nodes where a walk stops: no path back to v, or no successor
    reachesV = nx.ancestors(graph, v) | {v}
    dead = {n for n in graph.nodes if n not in reachesV or n not in successors}

    occurrences = Counter()
    for _ in range(100):
        seen = set()  # cycles already found in this run

        while True:
            tmpV = step(v)
            if tmpV not in successors:
                break

            tmpPath = [v, tmpV]
            ok = True
            while True:
                tmpV = step(tmpV)
                if tmpV in dead:
                    ok = False
                    break
                if tmpV == v:
                    break
                tmpPath.append(tmpV)

            cycle = tuple(tmpPath)
            if not ok or cycle in seen:
                break
            seen.add(cycle)
            occurrences[cycle] += 1

    return occurrences


def main(name):
    graph, size = loadGraph(name)

    if not nx.is_strongly_connected(graph):
        sys.exit("The graph is not strongly connected.")

    if graph.number_of_nodes() <= 1:
        sys.exit("The graph only has one node.")

    N = int(input("Enter the path length: "))
    if N <= 0:
        sys.exit("The number must be greater than 0.")

    print("Enter a node number between 0 and %d" % (size - 1))
    v = int(input())
    if v < 0 or v >= size:
        sys.exit("Invalid node number.")

    matrix = getAdjMatrix(graph)
    matrixExp = mulMatrix(matrix, N)

    print("[WARNING] A negative number of walks means the value is VERY large (integer overflow)")
    print("Number of closed walks of length N on v:", matrixExp[v, v])

    print("Probability of returning to v with a walk of length exactly N:",
          exactLength(matrixExp, v, size))
    print("Probability of returning to v with a walk of length at most N:",
          atMostLength(matrix, v, N, size))

    if utils.p:
        print("Arc probabilities are taken from the file (not uniform 1/t)")

    print("[WARNING] This may take a while")

    occ = paths(graph, v)
    if not occ:
        sys.exit("No cycle found: the path list is empty.")

    smallPath = min(map(len, occ))
    print("Shortest cycle length: %d" % smallPath)
    bigPath = max(map(len, occ))
    print("Longest cycle length: %d" % bigPath)

    tot = sum(occ.values())
    print("Total count: %d" % tot)

    # ((path), count, frequency), most frequent first
    datas = [(path, count, count / tot) for path, count in occ.most_common()]

    meanLen = sum(len(path) * count for path, count, _ in datas) / tot
    print("Mean cycle length = %f" % meanLen)

    # Same formula as the original project (kept for identical output)
    varianceLen = sum((len(path) * count) ** 2 - meanLen ** 2 for path, count, _ in datas) / tot
    print("Cycle length variance = %f" % varianceLen)

    utils.writeStat(tot, datas, smallPath, bigPath, meanLen, varianceLen)

    if utils.show:
        from view import showGraph  # imports matplotlib only when needed
        showGraph(graph, v, datas)
