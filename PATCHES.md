# Asciiverse changes to Oldrunner

Upstream: Frederic Culot's oldrunner (BSD), with polettix's segfault fix (2019).

## Our own levels

- `levels/original.lvl` (the 150 Broderbund levels) is removed. In its place,
  `levels/oldrunner.lvl` holds 20 levels made for the Asciiverse, in the same
  26x16 format, and `game.c` loads that file.
- `tools/mklevels.py` draws the levels from a few strokes (floors, ladders,
  ropes, escape ladders, gold, foes) and writes `levels/oldrunner.lvl`.
- `tools/lvlcheck.py` checks each level: one hero, an escape ladder reaching
  the top row, every gold bag reachable, and a way out after each one (foes
  ignored, digging one brick at a time).
- README and the manpage no longer describe the original levels.
