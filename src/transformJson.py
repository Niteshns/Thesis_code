import json
from pathlib import Path

def loadRuns(path: Path):
    with path.open(encoding="utf-8") as fh:
        obj = json.load(fh)
    return obj


def averageRuns(runs):
    nRuns  = len(runs)
    nSteps = len(runs[0]["I"])
    sums = {}

    for k in COMPARTMENTS:
        sums[k] = []
        for _ in range(nSteps):
            sums[k].append(0.0)

    for run in runs:
        for k in COMPARTMENTS:
            for i in range(nSteps):
                sums[k][i] += run[k][i]

    avg = {}
    for k in COMPARTMENTS:
        avg[k] = []
        for value in sums[k]:
            avg[k].append(value / nRuns)
    avg["T"] = runs[0]["T"][:]
    return avg


if __name__ == "__main__":
    DATA_DIR = Path(__file__).resolve().parent.parent / "data/json"
    OUT_DIR = Path(__file__).resolve().parent.parent / "data/jsonAverage"
    COMPARTMENTS = ["I", "R", "S", "Re"]
    numb = 0
    for fp in DATA_DIR.glob("simData_*.json"):

        runs = loadRuns(fp)
        avg = averageRuns(runs)
        suffix = fp.stem.replace("simData_", "")
        if suffix[-1] in ("A", "L"):
            suffix = suffix[:-1] + suffix[-1].lower()
        outFp = OUT_DIR / f"average_{suffix}.json"

        with outFp.open("w", encoding="utf-8") as out:
            json.dump(avg, out, indent=2)
