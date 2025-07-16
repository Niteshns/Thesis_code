import random
import networkx as nx
import matplotlib.pyplot as plt

def createPairList(inputList,edgeCount):
    pairList = []
    counter = 0

    if edgeCount == 1:
        count = int(len(inputList) / 2)
    else:
        count = int(len(inputList) / 3)

    for i in range(count):
            if(edgeCount == 1):
                firstNode = 2 * i
                secondNode = 2 * i + 1
                if inputList[firstNode] != inputList[secondNode]:
                    pairList.append(((inputList[firstNode]),(inputList[secondNode])))
            else:
                firstNode = counter
                secondNode = counter + 1
                thirdNode = counter + 2
                pairList.append(((inputList[firstNode]), (inputList[secondNode]), (inputList[thirdNode])))
                counter = counter + 3
    return set(pairList)


def assignDegree(n):
    singleEdgeList = []
    triangleEdgeList = []

    for i in range(n):
        sDegree = random.randrange(10,14)
        tDegree = random.randrange(0,2)
        singleEdgeList.append(sDegree)
        triangleEdgeList.append(tDegree)
    return singleEdgeList,triangleEdgeList


def createStubList(list):
    finalList = []
    counter = 0

    for i in range(len(list)):
        for j in range(list[i]):
            finalList.append(i)
    random.shuffle(finalList)
    return finalList


def transformTriangles(trianglePairs):
    pairList = []
    for i in range(len(trianglePairs)):
        pairList.append((trianglePairs[i][0],trianglePairs[i][1]))
        pairList.append((trianglePairs[i][0],trianglePairs[i][2]))
        pairList.append((trianglePairs[i][1],trianglePairs[i][2]))

    return set(pairList)


def buildGraph(n,seed):
    random.seed(seed)
    degreeLists = assignDegree(n)
    singleStubList = createStubList(degreeLists[0])
    triangleStubList = createStubList(degreeLists[1])

    singlePairs = createPairList(singleStubList,1)
    trianglePairs = createPairList(triangleStubList,3)
    extraPairs = transformTriangles(list(trianglePairs))
    allPairs = singlePairs.union(extraPairs)

    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(allPairs)
    setFlags(G)
    return G,allPairs


def setFlags(G):
    for n in G.nodes():
        if n == 0 or n == 1:
            G.nodes[n]["Status"] = "Infected"
        else:
            G.nodes[n]["Status"] = "Susceptible"

        G.nodes[n]["TimeInfected"] = 0


if __name__ == "__main__":
    G,allPairs = buildGraph(10,10)
