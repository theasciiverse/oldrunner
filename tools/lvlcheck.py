#!/usr/bin/env python3
"""Check oldrunner level files: sizes, one hero, an escape ladder that reaches
the top row, and that every gold bag and the exit can be reached (foes ignored,
digging one brick at a time allowed)."""
import sys
from collections import deque

SOLID = set('#X')

def parse(path):
    levels, cur = [], None
    for line in open(path):
        line = line.rstrip('\n')
        if line.startswith('level'):
            cur = {'name': line.split('\t', 1)[1].strip('"'), 'rows': []}
            levels.append(cur)
        elif line.startswith('size'):
            w, h = line.split('\t', 1)[1].split('x')
            cur['w'], cur['h'] = int(w), int(h)
        elif line.startswith('['):
            cur['rows'].append(line[1:-1])
    return levels

def reach(g, w, h, starts, escape):
    def at(y, x):
        if y >= h or x < 0 or x >= w:
            return 'OOB'
        c = g[y][x]
        if c == '|':
            return 'H' if escape else ' '
        return c if c in '#XH-' else ' '
    def supported(y, x):
        c = at(y, x)
        if c in 'H-':
            return True
        b = at(y + 1, x)
        return b != ' '
    seen, q = set(starts), deque(starts)
    while q:
        y, x = q.popleft()
        if y == 0 and at(y, x) == 'H' and g[y][x] == '|' and escape:
            seen.add(('WIN',))
        nxt = []
        if not supported(y, x):
            nxt.append((y + 1, x))
        else:
            for dx in (-1, 1):
                if at(y, x + dx) not in SOLID and at(y, x + dx) != 'OOB':
                    nxt.append((y, x + dx))
                    if at(y + 1, x + dx) == '#':
                        nxt.append((y + 1, x + dx))  # dig and drop in
                elif at(y, x + dx) == '#' and at(y + 1, x) in SOLID:
                    pass
            # dig from inside a hole: brick diagonally below
            if at(y, x) == '#':
                pass
            if at(y, x) == 'H' and y > 0 and at(y - 1, x) not in SOLID:
                nxt.append((y - 1, x))
            if y > 0 and at(y - 1, x) == 'H':
                nxt.append((y - 1, x))
            if at(y + 1, x) not in SOLID and at(y + 1, x) != 'OOB':
                nxt.append((y + 1, x))
        for p in nxt:
            if p not in seen:
                seen.add(p)
                q.append(p)
    return seen

def check(lv):
    errs = []
    w, h, rows = lv['w'], lv['h'], lv['rows']
    if len(rows) != h:
        errs.append(f'{len(rows)} rows, expected {h}')
    for i, r in enumerate(rows):
        if len(r) != w:
            errs.append(f'row {i} is {len(r)} wide')
    if errs:
        return errs
    g = [list(r) for r in rows]
    hero = [(y, x) for y in range(h) for x in range(w) if g[y][x] == '@']
    gold = [(y, x) for y in range(h) for x in range(w) if g[y][x] == '$']
    foes = sum(r.count('&') for r in rows)
    if len(hero) != 1:
        return [f'{len(hero)} heroes']
    if not any(g[0][x] == '|' for x in range(w)):
        errs.append('no escape ladder on the top row')
    if not gold:
        errs.append('no gold')
    r = reach(g, w, h, hero, False)
    for p in gold:
        if p not in r:
            errs.append(f'gold at row {p[0]} col {p[1]} unreachable')
        elif ('WIN',) not in reach(g, w, h, [p], True):
            errs.append(f'no way out after gold at row {p[0]} col {p[1]}')
    return errs, len(gold), foes

ok = True
for n, lv in enumerate(parse(sys.argv[1])):
    if lv.get('w') == 0:
        continue
    res = check(lv)
    if isinstance(res, list):
        errs, ng, nf = res, 0, 0
    else:
        errs, ng, nf = res
    print(f"{n:3} {lv['name']:<28} gold {ng:2} foes {nf}  " + ('ok' if not errs else '; '.join(errs)))
    ok &= not errs
sys.exit(0 if ok else 1)
