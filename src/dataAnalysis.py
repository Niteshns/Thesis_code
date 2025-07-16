import json
from pathlib import Path
import matplotlib.pyplot as plt
from itertools import cycle
from adjustText import adjust_text
import numpy as np

# Constants
TAU     = 0.1
T_FINAL = 25.0
GRAPHNODES = 1000000

def loadRun(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def plotIndividualRuns(runs):
    fig, ax = plt.subplots()
    colourCycle = cycle(plt.rcParams["axes.prop_cycle"].by_key()["color"])
    print(runs)
    for run in runs:
        print()
        I = run["I"]
        t = [i * TAU for i in range(len(I))] 
        colour = next(colourCycle)
        ax.plot(t, I, color=colour, linewidth=1.8, label=f"seed {runs.index(run) + 1}")

    ax.set_xlim(0, T_FINAL)
    ax.set_ylim(0, GRAPHNODES)
    ax.set_xlabel("Time step")
    ax.set_ylabel("Number of infected nodes")
    ax.set_title("Infected trajectories (D-H-Fa)")
    ax.grid(True)
    ax.legend(title="Run")
    plt.tight_layout()
    plt.show()


def plotAverage(runs):
    nSteps = len(runs[0]["I"])
    nRuns  = len(runs)

    meanInfect = [
        sum(run["I"][i] for run in runs) / nRuns
        for i in range(nSteps)
    ]

    t = [i * TAU for i in range(nSteps)]
    fig, ax = plt.subplots()
    ax.plot(t, meanInfect, color="red", linewidth=2.5, label="Mean infected")

    ax.set_xlim(0, T_FINAL)
    ax.set_ylim(0, GRAPHNODES)
    ax.set_xlabel("Time step")
    ax.set_ylabel("Number of infected nodes")
    ax.set_title("Average infected trajectory (D-H-Fa) ")
    ax.grid(True)
    ax.legend()
    plt.tight_layout()
    plt.show()


def plotCategory(category,dir):
    files = sorted(dir.glob(f"average_*{category}.json"))
    fig, (ax_I, ax_R) = plt.subplots(1, 2, figsize=(10, 4), sharex=True)
    colourCycle = cycle(plt.rcParams["axes.prop_cycle"].by_key()["color"])

    for fp in files:
        data = loadRun(fp)
        label = fp.stem.replace("average_", "")
        t = [i * TAU for i in range(len(data["I"]))]
        colour = next(colourCycle)
        ax_I.plot(t, data["I"], color=colour, linewidth=2, label=label)
        ax_R.plot(t, data["R"], color=colour, linewidth=2, label=label)

    for ax, ylab in zip((ax_I, ax_R), ("Number infected", "Number recovered")):
        ax.set_xlim(0, T_FINAL)
        ax.set_ylim(0, GRAPHNODES)
        ax.set_xlabel("Time step")
        ax.set_ylabel(ylab)
        ax.grid(True)

    ax_I.set_title(f"Infected ")
    ax_R.set_title(f"Recovered")
    ax_I.legend(title="File")

    plt.suptitle(f"Average trajectories {'Fast (Fa)' if category=='FA' else 'Slow (Sl)'} epidemics")
    plt.tight_layout()
    plt.show()


def scatterPeak(dir):
    files = sorted(dir.glob("average_*.json"))
    colourCycle = cycle(plt.rcParams["axes.prop_cycle"].by_key()["color"])
    yOffsets = [+6, -8, +6, -8, +10, -10, +6, -8, +6, -8]
    fig, ax = plt.subplots()

    for idx, fp in enumerate(files):
        data = loadRun(fp)
        tag  = fp.stem.replace("average_", "")
        infected    = data["I"]
        peakPrev = max(infected)
        peakIdx  = infected.index(peakPrev)
        peakTime = peakIdx * TAU
        colour = next(colourCycle)
        ax.scatter(peakTime,peakPrev, color=colour, s=60)
        dy = yOffsets[idx % len(yOffsets)]
        va = "bottom" if dy >= 0 else "top"

        ax.annotate(
            tag,
            (peakTime,peakPrev),
            xytext=(0, dy),
            textcoords="offset points",
            ha="center",
            va=va,
            color=colour,
            fontsize=9,
            weight="bold"
        )

    ax.set_xlabel("Peak time (t)")
    ax.set_ylabel("Peak prevalence (I)")
    ax.set_title("Peak-prevalence in epidemics")
    ax.set_ylim(0, GRAPHNODES)
    ax.grid(True)
    plt.tight_layout()
    plt.show()


def plotRt(dir):
    filesFa = sorted(dir.glob("average_*FA.json"))
    filesSl = sorted(dir.glob("average_*SL.json"))

    fig, (ax_fa, ax_sl) = plt.subplots(1, 2, figsize=(11, 4))
    base_cycle = cycle(plt.rcParams["axes.prop_cycle"].by_key()["color"])

    def _plot_group(ax, files, title):
        subcycle = cycle(base_cycle)
        ymax = 1.0
        for fp in files:
            data  = loadRun(fp)
            label = fp.stem.replace("average_", "")
            t     = [i*TAU for i in range(len(data["Re"]))]
            Rt    = np.clip(data["Re"], 0, None)
            ymax = max(ymax, np.max(Rt))
            ax.plot(t, Rt, lw=2, color=next(subcycle), label=label)

        ax.axhline(1, ls="--", color="black", lw=1)
        ax.set_xlim(0, T_FINAL)
        ax.set_ylim(0, 1.1 * ymax)
        ax.set_xlabel("Time step")
        ax.set_title(title)
        ax.grid(True)
        ax.legend(title="Scenario", fontsize="small")

    _plot_group(ax_fa, filesFa, "Fast epidemic (Fa)")
    _plot_group(ax_sl, filesSl, "Slow epidemic (Sl)")
    ax_fa.set_ylabel(r"effective reproduction $R_t$")
    plt.suptitle("Decay of the effective reproduction number $R_t$")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    DATA_DIR = Path(__file__).resolve().parent.parent / "data/json"
    AVG_DIR = Path(__file__).resolve().parent.parent / "data/jsonAverage"
    data = loadRun(DATA_DIR / "simData_DHFA.json")
    scatterPeak(AVG_DIR)
    plotIndividualRuns(data)
    plotAverage(data)
    plotCategory("FA", AVG_DIR)
    plotCategory("SL", AVG_DIR)
    plotRt(AVG_DIR)