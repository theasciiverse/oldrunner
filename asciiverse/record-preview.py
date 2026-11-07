#!/usr/bin/env python3
"""Records the catalog preview, asciiverse/oldrunner.cast, to
hub/RECORDING.md (100x30): the first levels, played.

asciinema runs in a detached 100x30 tmux pane; the player is this script.
It reads the level from tmux (with attributes, so the guards, drawn in
reverse, are told from the runner), plans the shortest way to the nearest
gold by breadth-first search over where the runner can stand, hang or
climb, keeps a cell's distance from the guards, and once the gold is in,
heads for the top of the escape ladder. The "Press any key" screens
between levels are answered. Plays the packaged build
(dist/oldrunner-<target>.tar.gz) from a throwaway folder.

    asciiverse/package.sh x86_64-unknown-linux-musl && asciiverse/record-preview.py
"""
import collections, os, re, shutil, subprocess, tarfile, tempfile, time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "asciiverse", "oldrunner.cast")
S = "oldrunner-rec"
W, H = 26, 16
OY, OX = 7, 37   # where a 26x16 level sits in a 100x30 terminal
LENGTH = float(os.environ.get("LENGTH", 32))
TICK = 0.085     # the game moves the runner once per 80 ms

BRICK, LADDER, ROPE, ESCAPE, GOLD = "▒~U", "H", "─", "│", "◆"
SGR = re.compile(r"\x1b\[([0-9;]*)m")
# capture-pane -e hands the line-drawing characters over as their VT100
# letters; inside the level these are the only lower-case ones
ACS = {"a": "▒", "`": "◆", "q": "─", "x": "│"}


def tmux(*a):
    return subprocess.run(["tmux", *a], capture_output=True, text=True).stdout


def key(k):
    tmux("send-keys", "-t", S, k)


def screen():
    """The pane as rows of (char, reverse) cells."""
    rows = []
    for line in tmux("capture-pane", "-p", "-e", "-t", S).splitlines():
        cells, rev, i = [], False, 0
        while i < len(line):
            m = SGR.match(line, i)
            if m:
                codes = [c for c in m.group(1).split(";") if c] or ["0"]
                for c in codes:
                    if c in ("0", "27"):
                        rev = False
                    elif c == "7":
                        rev = True
                i = m.end()
                continue
            if line[i] < " ":   # ESC, and SO/SI around line drawing
                i += 1
                continue
            cells.append((line[i], rev))
            i += 1
        rows.append(cells)
    return rows + [[] for _ in range(40)]


# what each cell showed when nothing stood on it, for the cells under the
# runner and the guards; cleared with each new level
memo = {}


def level(rows):
    grid, hero, foes = [], None, set()
    for y in range(H):
        r = rows[OY + y]
        row = ""
        for x in range(W):
            ch, rev = r[OX + x] if OX + x < len(r) else (" ", False)
            ch = ACS.get(ch, ch)
            if ch == "@":
                if rev:
                    foes.add((y, x))
                else:
                    hero = (y, x)
                ch = memo.get((y, x), " ")
                if ch == GOLD:
                    ch = " "
            else:
                if rev and ch == " ":
                    ch = "#"   # cement
                memo[(y, x)] = ch
            row += ch
        grid.append(row)
    return grid, hero, foes


def solid(c):
    return c in BRICK or c == "#"


def climbable(c, escape):
    return c == LADDER or (escape and c == ESCAPE)


def at(g, y, x):
    return g[y][x] if 0 <= y < H and 0 <= x < W else "▒"


def supported(g, y, x, escape):
    here, below = at(g, y, x), at(g, y + 1, x)
    return (y == H - 1 or solid(below) or climbable(below, escape)
            or climbable(here, escape) or here == ROPE)


def fall(g, y, x, escape):
    while not supported(g, y, x, escape):
        y += 1
        if at(g, y, x) == ROPE:
            break
    return y, x


def moves(g, y, x, escape):
    here = at(g, y, x)
    out = []
    for k, dx in (("Left", -1), ("Right", 1)):
        c = at(g, y, x + dx)
        if not solid(c):
            out.append((k, fall(g, y, x + dx, escape)))
    if climbable(here, escape) and not solid(at(g, y - 1, x)) and y > 0:
        out.append(("Up", fall(g, y - 1, x, escape)))
    below = at(g, y + 1, x)
    if not solid(below) and y < H - 1:
        out.append(("Down", fall(g, y + 1, x, escape)))
    return out


def plan(g, hero, foes, escape):
    """First key on the shortest safe way to the nearest goal."""
    danger = {(fy, fx + d) for fy, fx in foes for d in (-1, 0, 1)}
    danger |= {(fy + d, fx) for fy, fx in foes for d in (-1, 1)}
    goals = ({(y, x) for y in range(H) for x in range(W) if g[y][x] == GOLD}
             or ({(0, x) for x in range(W) if g[0][x] == ESCAPE} if escape else set()))
    if not goals:
        return None
    seen, q = {hero: None}, collections.deque([hero])
    while q:
        p = q.popleft()
        if p in goals:
            while seen[p] and seen[p][0] != hero:
                p = seen[p][0]
            return seen[p][1] if seen[p] else None
        for k, n in moves(g, *p, escape):
            if n not in seen and (n not in danger or n in goals):
                seen[n] = (p, k)
                q.append(n)
    return None


def dig(g, hero, foes):
    """A guard coming along the runner's floor: dig the brick in front of
    him, so he drops into the hole (z digs left, x digs right)."""
    y, x = hero
    for fy, fx in foes:
        if fy != y or not 2 <= abs(fx - x) <= 4:
            continue
        d = 1 if fx > x else -1
        if (at(g, y, x + d) == " " and at(g, y + 1, x + d) in BRICK
                and supported(g, y, x, False) and not climbable(at(g, y, x), True)):
            return "x" if d > 0 else "z"
    return None


def play(start):
    while time.time() - start < LENGTH:
        rows = screen()
        text = "".join(c for r in rows for c, _ in r)
        if "Press any key" in text or "GAME OVER" in text:
            memo.clear()
            time.sleep(1.6)
            key("Space")
            time.sleep(0.4)
            continue
        g, hero, foes = level(rows)
        if os.environ.get("DEBUG"):
            bar = "".join(c for c, _ in rows[OY + 19])
            print(f"{time.time() - start:5.1f} hero={hero} foes={sorted(foes)} {bar.strip()[:80]}", flush=True)
            if not hero and os.environ.get("DEBUG") == "2":
                print("\n".join(g)); print(tmux("capture-pane", "-p", "-e", "-t", S)[-3000:]); return
        if hero:
            escape = not any(GOLD in r for r in g)
            k = dig(g, hero, foes) or plan(g, hero, foes, escape)
            if os.environ.get("DEBUG"):
                print("   key", k, "escape", escape, flush=True)
            if k:
                key(k)
        time.sleep(TICK)


def main():
    tmp = tempfile.mkdtemp()
    try:
        game = os.path.join(tmp, "game")
        os.makedirs(game)
        os.makedirs(os.path.join(tmp, "home"))
        with tarfile.open(os.path.join(HERE, "dist", "oldrunner-x86_64-unknown-linux-musl.tar.gz")) as t:
            t.extractall(game, filter="data")
        if os.path.exists(OUT):
            os.remove(OUT)
        cmd = (f"env -i PATH=/usr/bin:/bin HOME={tmp}/home USER=player LOGNAME=player "
               "TERM=xterm-256color COLORTERM=truecolor LANG=C.UTF-8 "
               "asciinema rec --window-size 100x30 --idle-time-limit 2 "
               f"--capture-env TERM,COLORTERM,LANG --command ./oldrunner {OUT}")
        tmux("new-session", "-d", "-s", S, "-x", "100", "-y", "30", "-c", game, cmd)
        time.sleep(3)          # the first level's card
        start = time.time()
        play(start)
        key("q")
        time.sleep(1.5)
    finally:
        tmux("kill-session", "-t", S)
        shutil.rmtree(tmp, ignore_errors=True)
    print(OUT, os.path.getsize(OUT) if os.path.exists(OUT) else "missing")


if __name__ == "__main__":
    main()
