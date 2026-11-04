import json, re

txt = open('puzzles.js').read()
data = json.loads(re.search(r'window\.MEOW_PUZZLES=(\{.*\});', txt, re.S).group(1))

def count_solutions(n, owner, limit=3):
    sols = 0
    col_used = [False]*n
    reg_used = [False]*n
    p = [-1]*n
    def bt(r):
        nonlocal sols
        if r == n:
            sols += 1
            return sols >= limit
        for c in range(n):
            if col_used[c] or reg_used[owner[r][c]]:
                continue
            if r > 0 and abs(c - p[r-1]) <= 1:
                continue
            col_used[c] = True; reg_used[owner[r][c]] = True; p[r] = c
            stop = bt(r+1)
            col_used[c] = False; reg_used[owner[r][c]] = False; p[r] = -1
            if stop: return True
        return False
    bt(0)
    return sols

def connected(owner, n, rid):
    cells = [(r,c) for r in range(n) for c in range(n) if owner[r][c]==rid]
    if not cells: return False
    cellset=set(cells); seen={cells[0]}; stack=[cells[0]]
    while stack:
        r,c=stack.pop()
        for nb in ((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
            if nb in cellset and nb not in seen:
                seen.add(nb); stack.append(nb)
    return len(seen)==len(cells)

ok = True
for pz in data['puzzles']:
    n = pz['n']; owner = pz['regions']; sol = pz['solution']
    sizes = {}
    for row in owner:
        for v in row: sizes[v] = sizes.get(v,0)+1
    conn = all(connected(owner, n, r) for r in range(n))
    # solution validity
    perm = len(sol)==n and len(set(sol))==n and all(0<=c<n for c in sol)
    nonadj = all(abs(sol[i]-sol[i+1])>1 for i in range(n-1))
    region_ok = all(owner[r][sol[r]] == r for r in range(n))
    cnt = count_solutions(n, owner, 3)
    good = conn and perm and nonadj and region_ok and cnt == 1
    ok = ok and good
    print(pz['id'], 'n=%d'%n, 'unique=%d'%cnt, 'conn=%s'%conn, 'sizes=%s'%sorted(sizes.values()), 'OK' if good else 'FAIL')
print('ALL OK' if ok else 'PROBLEMS')
