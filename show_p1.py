import json
d = json.load(open('puzzles.json'))
p = d['puzzles'][0]
print(p['id'], p['n'], p['solution'])
for row in p['regions']:
    print(row)
sizes = {}
for r in p['regions']:
    for v in r:
        sizes[v] = sizes.get(v, 0) + 1
print('sizes', sizes)
# print solution positions and region ids
for r, c in enumerate(p['solution']):
    print('row', r, 'col', c, 'region', p['regions'][r][c])
