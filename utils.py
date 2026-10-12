import random

# Global flags set from the command line
debug = False
p = False
show = False


def debugOn():
    global debug
    debug = True


def pOn():
    global p
    p = True


def showOn():
    global show
    show = True


def randomProb(arcs):
    """Random probability distribution over the arcs (sums to 1, precision 1e-6)."""
    precision = 1000000
    probs = []
    total = 0
    remaining = precision

    # Random values for the first N-1 arcs...
    for _ in range(len(arcs) - 1):
        val = random.randrange(remaining)
        total += val
        probs.append(val / precision)
        remaining -= val

    # ...and the remainder for the last one so the total is exactly 1
    probs.append((precision - total) / precision)
    return probs


def randomization(index, last):
    """Random arc list for node `index` (always includes index+1, or 0 for the last node)."""
    arcs = [0 if index == last else index + 1]
    excluded = {index, index + 1, arcs[0]}  # set for O(1) membership tests

    for _ in range(1, random.randint(2, max(last, 2))):
        val = random.randint(0, last)
        if val not in excluded:
            excluded.add(val)
            arcs.append(val)

    return arcs


def writeStat(total, datas, smallestPath, biggestPath, meanLen, varianceLen):
    """Write the statistics to stats.txt."""
    with open("stats.txt", "w") as file:
        file.write("Longest cycle: " + str(biggestPath) + '\n')
        file.write("Shortest cycle: " + str(smallestPath) + '\n')
        file.write("Total count: " + str(total) + '\n')
        file.write("Mean cycle length: " + str(meanLen) + '\n')
        file.write("Cycle length variance: " + str(varianceLen) + '\n')
        file.write("((cycle), count, frequency)" + '\n')
        file.writelines(str(d) + '\n' for d in datas)
