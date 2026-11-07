"""Generated oldrunner levels.

Levels are drawn from a fixed seed in a few styles (floors with gaps,
scattered ledges, walled rooms, rope fields), kept only when lvlcheck finds
them finishable, and sorted from easy to hard."""
import random

from lvlcheck import check, reach

W, H = 26, 16

ADJ = """Amber Ashen Bitter Blind Brass Broken Busy Cellar Chalk Cinder Cold Copper
Crooked Damp Deep Dusty Empty Far Flint Foggy Golden Granite Grey Hidden Hollow
Iron Lazy Leaden Little Lone Long Loose Low Lucky Marble Midnight Misty Narrow
Night Old Pale Patient Quiet Restless Rusty Salt Silent Silver Slate Sleepy
Slow Steep Still Stone Sunken Tangled Tin Twisted Upper Velvet Winding Windy
Wooden""".split()
NOUN = """Alley Arches Attic Bank Barrow Bell Bridge Burrow Cage Canal Cave Cellar
Chimney Cistern Cliffs Cloister Court Crossing Crypt Dam Den Ditch Docks Drift
Furnace Gallery Gate Hall Harbour Hive Keep Kiln Ladders Larder Ledge Lift Loft
Market Mill Mine Nest Orchard Pantry Pass Pier Pit Quarry Ramparts Rigging
Ropes Scaffold Shaft Shelves Sluice Stacks Stairs Steps Store Terraces Tower
Tunnels Vault Walls Warren Well Wharf Works Yard""".split()


class Grid:
    def __init__(self):
        self.g = [[' '] * W for _ in range(H)]
        for x in range(W):
            self.g[H - 1][x] = '#'

    def get(self, y, x):
        return self.g[y][x]

    def set(self, y, x, c):
        if 0 <= y < H and 0 <= x < W:
            self.g[y][x] = c

    def standing_cells(self):
        """Empty cells with solid ground under them."""
        out = []
        for y in range(1, H - 1):
            for x in range(W):
                if self.g[y][x] == ' ' and self.g[y + 1][x] in '#X':
                    out.append((y, x))
        return out


def floors_style(r, diff):
    """Horizontal floors with gaps, ladders between them, ropes over gaps."""
    g = Grid()
    ys, y = [], H - 1
    while True:
        y -= r.choice((3, 3, 4, 4, 5))
        if y < 3:
            break
        ys.append(y)
    cement = 0.05 + 0.25 * diff
    for fy in ys:
        x = 0
        while x < W:
            seg = r.randint(4, 12)
            c = 'X' if r.random() < cement else '#'
            for i in range(x, min(W, x + seg)):
                g.set(fy, i, c)
            x += seg
            if r.random() < 0.55:
                gap = r.randint(2, 4)
                if r.random() < 0.5:
                    for i in range(x, min(W, x + gap)):
                        g.set(fy - 1, i, '-')
                x += gap
    levels = [H - 1] + ys
    for lo, hi in zip(levels, levels[1:]):
        used = []
        for _ in range(r.choice((1, 2, 2, 3))):
            x = r.randrange(W)
            if any(abs(x - u) < 4 for u in used):
                continue
            used.append(x)
            for yy in range(hi, lo):
                g.set(yy, x, 'H')
    return g, ys[-1]


def ledges_style(r, diff):
    """Short ledges scattered over open space, each hung from a ladder."""
    g = Grid()
    top = None
    for _ in range(r.randint(14, 24)):
        y = r.randrange(3, H - 2)
        x0 = r.randrange(0, W - 3)
        n = r.randint(3, 9)
        c = 'X' if r.random() < 0.2 * diff else '#'
        x1 = min(W, x0 + n)
        if any(g.get(yy, i) != ' ' for yy in (y - 1, y, y + 1)
               for i in range(max(0, x0 - 1), min(W, x1 + 1))):
            continue
        for i in range(x0, x1):
            g.set(y, i, c)
        lx = r.randrange(x0, x1)
        if any(g.get(yy, i) == 'H' for yy in range(y, H - 1)
               for i in (lx - 1, lx + 1) if 0 <= i < W):
            continue
        down = y
        while down + 1 < H and g.get(down + 1, lx) not in '#X':
            down += 1
        for yy in range(y, down + 1):
            g.set(yy, lx, 'H')
        if r.random() < 0.4:
            ry = y - 1
            rx = min(W - 1, x0 + n)
            for i in range(rx, min(W, rx + r.randint(2, 6))):
                if g.get(ry, i) == ' ':
                    g.set(ry, i, '-')
        top = y if top is None else min(top, y)
    return g, top


def rooms_style(r, diff):
    """Two or three storeys of rooms with cement walls; dig to get between them."""
    g = Grid()
    storeys = r.choice(((11, 7, 3), (10, 5), (12, 8, 4)))
    for fy in storeys:
        for x in range(W):
            g.set(fy, x, '#')
    levels = [H - 1] + list(storeys)
    for lo, hi in zip(levels, levels[1:]):
        for _ in range(r.randint(1, 3)):
            wx = r.randrange(2, W - 2)
            for yy in range(hi + 1, lo):
                g.set(yy, wx, 'X')
        for _ in range(r.randint(1, 2)):
            x = r.randrange(W)
            if all(g.get(yy, x) != 'X' for yy in range(hi, lo)):
                for yy in range(hi, lo):
                    g.set(yy, x, 'H')
    for fy in storeys:
        for x in range(W):
            if g.get(fy, x) == '#' and r.random() < 0.12 + 0.3 * diff:
                g.set(fy, x, 'X')
    return g, storeys[-1]


def ropes_style(r, diff):
    """Long ropes between ladder columns, a floor here and there."""
    g = Grid()
    cols = sorted(r.sample(range(W), r.randint(2, 4)))
    rows = list(range(r.choice((3, 4)), H - 2, r.choice((3, 4))))
    for y in rows:
        if r.random() < 0.35:
            x0 = r.randrange(0, W - 8)
            for i in range(x0, x0 + r.randint(5, 10)):
                g.set(y, i, '#' if r.random() > 0.2 * diff else 'X')
        else:
            x0 = r.randrange(0, 6)
            for i in range(x0, W - r.randrange(0, 6)):
                g.set(y, i, '-')
    for x in cols:
        y0 = r.choice(rows)
        for yy in range(y0, H - 1):
            g.set(yy, x, 'H')
    return g, min(rows)


STYLES = (floors_style, floors_style, ledges_style, rooms_style, ropes_style)


def place(r, g, top, diff):
    """Hero, escape ladder, gold and foes on a drawn grid."""
    # escape ladder from the top row down onto the highest walkable ground
    cells = [(y, x) for (y, x) in g.standing_cells() if y <= top + 1]
    if not cells:
        cells = [(y, x) for y in range(1, H - 1) for x in range(W) if g.get(y, x) == 'H']
    if not cells:
        return None
    cells = [c for c in cells if c[0] <= 4]
    if not cells:
        return None
    ey, ex = r.choice(cells)
    for yy in range(0, ey + 1):
        if g.get(yy, ex) in '#X':
            return None
        g.set(yy, ex, '|')
    floor = [(H - 2, x) for x in range(W) if g.get(H - 2, x) == ' ']
    if not floor:
        return None
    hy, hx = r.choice(floor)
    g.set(hy, hx, '@')
    spots = [c for c in g.standing_cells()]
    r.shuffle(spots)
    ngold = r.randint(6, 9 + int(5 * diff))
    gold, rest = [], []
    for c in spots:
        if (len(gold) < ngold
                and all(max(abs(c[0] - y), abs(c[1] - x)) > 2 for y, x in gold)
                and sum(1 for y, _ in gold if y == c[0]) < 3):
            gold.append(c)
        else:
            rest.append(c)
    if len(gold) < 6:
        return None
    for y, x in gold:
        g.set(y, x, '$')
    nfoes = min(6, 1 + int(diff * 4.5) + (r.random() < 0.3))
    foes = []
    for c in rest:
        if (len(foes) < nfoes and abs(c[1] - hx) + abs(c[0] - hy) > 8
                and all(abs(c[0] - y) + abs(c[1] - x) > 4 for y, x in foes)):
            foes.append(c)
    for y, x in foes:
        g.set(y, x, '&')
    return g


def score(g):
    """Rough difficulty: foes, gold, buried gold, cement, how far apart it all is."""
    rows = [''.join(r) for r in g.g]
    foes = sum(r.count('&') for r in rows)
    gold = sum(r.count('$') for r in rows)
    cement = sum(r.count('X') for r in rows)
    ropes = sum(r.count('-') for r in rows)
    return foes * 4 + gold * 0.8 + cement * 0.08 + ropes * 0.03


def generate(count, seed=1982, taken=()):
    r = random.Random(seed)
    names = set(taken)
    out, seen = [], set()
    tries = 0
    while len(out) < count * 3 and tries < 200000:
        tries += 1
        diff = r.random()
        style = r.choice(STYLES)
        g, top = style(r, diff)
        if top is None:
            continue
        g = place(r, g, top, diff)
        if g is None:
            continue
        rows = [''.join(x) for x in g.g]
        key = '\n'.join(rows)
        if key in seen:
            continue
        lv = {'name': '', 'w': W, 'h': H, 'rows': rows}
        res = check(lv)
        if isinstance(res, list) or res[0]:
            continue
        # most of the map should be reachable, or it is mostly decoration
        hero = [(y, x) for y in range(H) for x in range(W) if rows[y][x] == '@']
        if len(reach(g.g, W, H, hero, True)) < 90:
            continue
        seen.add(key)
        out.append((score(g), style.__name__, rows))
    # keep an even spread of difficulty, then sort easy to hard
    out.sort(key=lambda t: t[0])
    step = len(out) / count
    picked = [out[int(i * step)] for i in range(count)]
    levels = []
    for _, style, rows in picked:
        while True:
            n = f'{r.choice(ADJ)} {r.choice(NOUN)}'
            if n not in names:
                names.add(n)
                break
        levels.append((n, rows))
    return levels
