# Asciiverse changes to Oldrunner

Upstream: Frederic Culot's oldrunner (BSD), with polettix's segfault fix (2019).

## Our own levels

- `levels/original.lvl` (the 150 Broderbund levels) is removed. In its place,
  `levels/oldrunner.lvl` holds 150 levels made for the Asciiverse, in the same
  26x16 format, and `game.c` loads that file.
- `tools/mklevels.py` writes `levels/oldrunner.lvl`. Twenty levels are drawn
  by hand from a few strokes (floors, ladders, ropes, escape ladders, gold,
  foes); levels 1 to 10 open the game and the other ten are spread through
  the rest. The other 130 come from `tools/genlevels.py`, which draws levels
  in four styles (floors with gaps, scattered ledges, walled rooms, rope
  fields) from a fixed seed, keeps those that pass the checker, and sorts them
  from easy to hard by foes, gold and cement.
- `tools/lvlcheck.py` checks each level: one hero, an escape ladder reaching
  the top row, every gold bag reachable, and a way out after each one (foes
  ignored, digging one brick at a time).
- README and the manpage no longer describe the original levels.
