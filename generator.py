import json
import sys

import utils

nodeCount = int(input("Enter the number of nodes: "))

if nodeCount <= 0:
    print("The number of nodes must be at least 1.")
    sys.exit()

if nodeCount > 1:
    nodes = []
    for i in range(nodeCount):
        arcs = utils.randomization(i, nodeCount - 1)
        nodes.append({'id': i, 'arcs': arcs, 'p': utils.randomProb(arcs)})
else:
    nodes = [{'id': 0, 'arcs': [], 'p': [1]}]

with open('graph.json', 'w') as out:
    json.dump({'nodeCount': nodeCount, 'nodes': nodes}, out, indent=2)
