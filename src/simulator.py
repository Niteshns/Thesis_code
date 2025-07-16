import random,math,json
import networkx as nx
from src import graphGenerator as gen
from pathlib import Path

# S = Susceptible, I = Infected, R = Recovered

#CONSTANTS
β  = 0.4
γ = 0.5

def infect(G,n,infectionRate):
    neighbours = list(G.adj[n].keys())
    susceptibles = []
    infected = 0
    for neighbour in neighbours:
        if G.nodes[neighbour]['Status'] == "Susceptible":
            susceptibles.append(neighbour)
    for node in susceptibles:
        numb = random.random()
        if numb < β:
            G.nodes[node]['Status'] = "Infected"
            G.nodes[node]['TimeInfected'] = 0
            infected += 1
    infectionRate[0] = infectionRate[0] + infected
    infectionRate[1] = infectionRate[1] + len(susceptibles)


def recover(G):
    infected = [n for n, status in G.nodes(data="Status") if status == "Infected"]
    for n in infected:
        numb = random.random()
        probRec = 1 - math.exp(-γ * G.nodes[n]['TimeInfected'])
        if numb < probRec:
            G.nodes[n]['Status'] = "Recovered"
        else:
            G.nodes[n]['TimeInfected'] = G.nodes[n]['TimeInfected'] + 0.2


def printGraph():
    pos = nx.spring_layout(G,seed=10)
    nx.draw(G, pos, with_labels=True)
    plt.show()


def printStatus():
    for n in G.nodes():
        print(f"Node ",n," Status: ",G.nodes[n]["Status"])
    print("\n")


def haveInfections(G):
    isInfected = any(status == "Infected"
                       for _, status in G.nodes(data="Status"))
    return isInfected


def discreteSim(G,data):
    while haveInfections(G):
        infectionRate = [0,0]
        infected = [n for n, status in G.nodes(data="Status") if status == "Infected"]
        data["I"].append(len(infected))
        recovered = [n for n, status in G.nodes(data="Status") if status == "Recovered"]
        data["R"].append(len(recovered))
        susceptible = [n for n, status in G.nodes(data="Status") if status == "Susceptible"]
        data["S"].append(len(susceptible))
        print(f"INFECTED: ", infected, " RECOVERED: ", recovered, " Susceptible: ", susceptible, "\n")

        if len(infected) > 0:
            for i in infected:
                infect(G,i,infectionRate)
                if checkInfections(G) is False:
                    break
            recovered = [n for n, status in G.nodes(data="Status") if status == "Recovered"]
            recover(G)

        print(infectionRate)
        if infectionRate[0] > 0:
            rate = infectionRate[0] / infectionRate[1]
            data["S-I"].append(rate)
        else:
                data["S-I"].append(0)

def tauLeapSim(G,data):
    tau = 0.1
    tFinal = 25
    pInfect  = 1.0 - math.exp(-β  * tau)
    print(pInfect)
    pRecover = 1.0 - math.exp(-γ * tau)
    t = 0.0
    makeSnapshot(G, t, data,0,0)
    while t < tFinal and haveInfections(G):
        toRecover, toInfect = set(), set()
        for n in G.nodes():
            if G.nodes[n]["Status"] == "Infected":
                randomNumb = random.random()
                if randomNumb < pRecover:
                    toRecover.add(n)

                for v in G.neighbors(n):
                    if G.nodes[v]["Status"] == "Susceptible":
                        randomNumb = random.random()
                        if randomNumb < pInfect:
                            toInfect.add(v)

        for u in toRecover:
            G.nodes[u]["Status"] = "Recovered"
        for v in toInfect:
            G.nodes[v]["Status"] = "Infected"

        t += tau
        makeSnapshot(G, t, data,len(toRecover),len(toInfect))


def makeSnapshot(G,t,data,nRec,nInf):
    infected = [n for n, status in G.nodes(data="Status") if status == "Infected"]
    recovered = [n for n, status in G.nodes(data="Status") if status == "Recovered"]
    susceptible = [n for n, status in G.nodes(data="Status") if status == "Susceptible"]
    data["T"].append(t)
    data["I"].append(len(infected))
    data["R"].append(len(recovered))
    data["S"].append(len(susceptible))
    ReproductNumb = -1
    if nInf > 0 and nRec > 0:
        ReproductNumb = nInf / nRec
    data["Re"].append(ReproductNumb)

    print(f"time={t:5.2f}  INFECTED: {len(infected)}  " f"RECOVERED: {len(recovered)}  SUSCEPTIBLE: {len(susceptible)}")


def storeData(data):
    DATA_DIR = Path(__file__).resolve().parent.parent / "data"
    out_file = DATA_DIR / "simData_DLFA.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"✓ data written to {out_file}")


if __name__ == "__main__":
    seeds = [1,5,10,100,200]
    simRunsData = []
    for seed in seeds:
        print(f"SIM: ", seed)
        G, allPairs = gen.buildGraph(1000000, seed)
        data = {"I": [], "R": [], "S": [], "Re": [], "T": []}
        tauLeapSim(G, data)
        simRunsData.append(data)
    storeData(simRunsData)


