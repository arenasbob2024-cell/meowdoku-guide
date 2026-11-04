# -*- coding: utf-8 -*-
"""Generate original Cat Territory puzzles for the Meowdoku fan guide.

Rules implemented (the same public rules Meowdoku uses):
  * one cat per coloured region
  * one cat per row and per column
  * no two cats touch, not even diagonally

Puzzles are generated here, checked for a unique solution, and written to
puzzles.js. No level, layout or artwork from Oakever Games is used.
"""
import json, random, time

SIZES = [(6, 6), (7, 6), (8, 6), (9, 5)]
MAX_TRIES = 60000


def valid_perm(n, p):
    return all(abs(p[i] - p[i + 1]) > 1 for i in range(n - 1))


def random_solution(n, rng):
    p = list(range(n))
    for _ in range(200):
        rng.shuffle(p)
        if valid_perm(n, p):
            return p
    return None


def grow_regions(n, sol, rng, cap_factor):
    """Grow n connected regions from the solution cells, with a size cap."""
    cap = max(2, int(round(n * cap_factor)))
    owner = [[-1] * n for _ in range(n)]
    sizes = [0] * n
    frontier = []
    for r, c in enumerate(sol):
        owner[r][c] = r
        sizes[r] = 1
        frontier.append((r, c, r))
    unassigned = n * n - n
    guard = 0
    while unassigned > 0 and guard < 400000:
        guard += 1
        cand = [i for i, (r, c, rid) in enumerate(frontier) if sizes[rid] < cap]
        if not cand:
            break
        i = rng.choice(cand)
        r, c, rid = frontier.pop(i)
        neigh = [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]
        rng.shuffle(neigh)
        for nr, nc in neigh:
            if 0 <= nr < n and 0 <= nc < n and owner[nr][nc] == -1:
                owner[nr][nc] = rid
                sizes[rid] += 1
                frontier.append((nr, nc, rid))
                unassigned -= 1
                break
    # Any leftovers (rare) join an adjacent region; this keeps connectivity.
    while unassigned > 0:
        progressed = False
        for r in range(n):
            for c in range(n):
                if owner[r][c] == -1:
                    for nr, nc in [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]:
                        if 0 <= nr < n and 0 <= nc < n and owner[nr][nc] >= 0:
                            owner[r][c] = owner[nr][nc]
                            sizes[owner[nr][nc]] += 1
                            unassigned -= 1
                            progressed = True
                            break
            if progressed:
                break
        if not progressed:
            return None
    return owner


def connected(owner, n):
    for rid in range(n):
        cells = [(r, c) for r in range(n) for c in range(n) if owner[r][c] == rid]
        if not cells:
            return False
        seen = {cells[0]}
        stack = [cells[0]]
        cellset = set(cells)
        while stack:
            r, c = stack.pop()
            for nb in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if nb in cellset and nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
        if len(seen) != len(cells):
            return False
    return True


def count_solutions(n, owner, limit=2):
    sols = 0
    col_used = [False] * n
    reg_used = [False] * n
    p = [-1] * n

    def bt(r):
        nonlocal sols
        if r == n:
            sols += 1
            return sols >= limit
        for c in range(n):
            if col_used[c] or reg_used[owner[r][c]]:
                continue
            if r > 0 and abs(c - p[r - 1]) <= 1:
                continue
            col_used[c] = True
            reg_used[owner[r][c]] = True
            p[r] = c
            stop = bt(r + 1)
            col_used[c] = False
            reg_used[owner[r][c]] = False
            p[r] = -1
            if stop:
                return True
        return False

    bt(0)
    return sols


def make_one(n, rng, cap_factor):
    for _ in range(MAX_TRIES):
        sol = random_solution(n, rng)
        if not sol:
            continue
        owner = grow_regions(n, sol, rng, cap_factor)
        if owner is None:
            continue
        if not connected(owner, n):
            continue
        if count_solutions(n, owner) == 1:
            return owner, sol
    return None


def main():
    rng = random.Random(20261104)
    puzzles = []
    pid = 0
    for n, count in SIZES:
        made = 0
        t0 = time.time()
        attempts = 0
        cap = 1.9
        while made < count and time.time() - t0 < 90:
            attempts += 1
            got = make_one(n, rng, cap)
            if not got:
                cap = 1.9 if cap > 2.3 else cap + 0.2
                continue
            owner, sol = got
            pid += 1
            puzzles.append({
                "id": "p%d" % pid,
                "n": n,
                "regions": owner,
                "solution": sol,
            })
            made += 1
        print("size %d: %d puzzles in %.1fs (%d attempts, cap %.1f)" % (n, made, time.time() - t0, attempts, cap))
    data = {"puzzles": puzzles}
    with open("puzzles.js", "w", encoding="utf-8") as f:
        f.write("window.MEOW_PUZZLES=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    with open("puzzles.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("total", len(puzzles))


if __name__ == "__main__":
    main()
