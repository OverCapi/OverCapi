#!/usr/bin/env python3
"""Game of Life seeded by your GitHub contributions -> assets/life.svg

  python3 scripts/life.py            # real data (needs GITHUB_TOKEN)
  python3 scripts/life.py --sample   # fake data, no network
  python3 scripts/life.py --test     # self-check
"""
import json
import os
import random
import sys
import urllib.request
from pathlib import Path

LOGIN = os.environ.get("GH_LOGIN", "OverCapi")
THRESHOLD = 1   # days with >= THRESHOLD commits start alive
GENS = 64
DT = 0.38       # seconds per generation
OUT = Path(__file__).resolve().parent.parent / "assets" / "life.svg"

AMBER, DIM, FG = "#f0b429", "#8b949e", "#c9d1d9"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
weeks{contributionDays{contributionCount weekday}}}}}}"""


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        sys.exit(f"GraphQL error: {body['errors']}")
    weeks = body["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    grid = [[0] * 7 for _ in weeks]  # grid[week][weekday]
    for w, week in enumerate(weeks):
        for day in week["contributionDays"]:
            grid[w][day["weekday"]] = day["contributionCount"]
    return grid


def sample():
    rnd = random.Random(4242)
    return [[rnd.choice([0, 0, 0, 1, 2, 3, 5, 9]) for _ in range(7)] for _ in range(53)]


def step(alive):
    """One Game of Life generation on a torus. alive: list of weeks, each 7 bools."""
    W, H = len(alive), len(alive[0])
    nxt = []
    for w in range(W):
        col = []
        for d in range(H):
            n = sum(alive[(w + dw) % W][(d + dd) % H]
                    for dw in (-1, 0, 1) for dd in (-1, 0, 1) if dw or dd)
            col.append(n == 3 or (alive[w][d] and n == 2))
        nxt.append(col)
    return nxt


def render(counts):
    alive = [[c >= THRESHOLD for c in week] for week in counts]
    frames = [alive]
    while len(frames) < GENS:
        alive = step(alive)
        if sum(map(sum, alive)) == 0 or alive == frames[-1]:
            break
        frames.append(alive)
    total = len(frames) * DT

    def xy(w, d):
        return 20 + w * 14, 44 + d * 14

    bg = "".join(
        f'<rect x="{x}" y="{y}" width="11" height="11" rx="2" fill="{"#1f242c" if c else "#161b22"}"/>'
        for w, week in enumerate(counts) for d, c in enumerate(week) for x, y in [xy(w, d)]
    )
    gens = []
    for i, f in enumerate(frames):
        cells = "".join(
            f'<rect x="{x}" y="{y}" width="11" height="11" rx="2"/>'
            for w, week in enumerate(f) for d, on in enumerate(week) if on for x, y in [xy(w, d)]
        )
        pop = sum(map(sum, f))
        gens.append(
            f'<g class="f" style="animation-delay:{i * DT - total:.2f}s">'
            f'<text x="764" y="26" font-size="12" fill="{DIM}" text-anchor="end">gen {i} · pop {pop}</text>'
            f'<g fill="{AMBER}">{cells}</g></g>'
        )
    pct = 100 / len(frames)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 784 172" width="784" height="172" role="img" aria-label="Game of Life seeded by {LOGIN}'s contributions">
<style>
text{{font-family:{FONT}}}
.f{{visibility:hidden;animation:show {total:.2f}s step-end infinite}}
@keyframes show{{0%{{visibility:visible}}{pct:.4f}%{{visibility:hidden}}100%{{visibility:hidden}}}}
</style>
<rect x=".5" y=".5" width="783" height="171" rx="8" fill="#0a0d12" stroke="#30363d"/>
<text x="20" y="26" font-size="12" fill="{DIM}"><tspan fill="{AMBER}">$</tspan> ./life --seed=contributions --gens={GENS}</text>
{bg}
{"".join(gens)}
<text x="20" y="156" font-size="12" fill="{DIM}">days with ≥ {THRESHOLD} commits start alive · regenerated nightly</text>
</svg>
'''


def selftest():
    # vertical blinker in a 5x7 torus flips to horizontal and back
    g = [[False] * 7 for _ in range(5)]
    for d in (2, 3, 4):
        g[2][d] = True
    h = step(g)
    assert [w for w in range(5) if h[w][3]] == [1, 2, 3] and sum(map(sum, h)) == 3
    assert step(h) == g
    assert "gen 0" in render(sample())
    print("ok")


if __name__ == "__main__":
    if "--test" in sys.argv:
        selftest()
    else:
        data = sample() if "--sample" in sys.argv else fetch(LOGIN, os.environ["GITHUB_TOKEN"])
        OUT.write_text(render(data))
        print("wrote", OUT)
