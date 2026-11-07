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

## Playing here

- **Line drawing in UTF-8 terminals** (`gfx.c`): the game now calls
  `setlocale` and links ncursesw, so the frame, bricks, ropes, ladders and
  gold come out as line-drawing characters instead of `q`, `x`, `a` and
  `` ` `` in UTF-8 terminals.
- **No busy loop** (`gfx.c`): the game window waited for keys with
  `nodelay`, so the main loop spun and used a whole CPU core; it now waits
  up to 10 ms for a key (`wtimeout`), and the game runs at the same speed.
- **Arrow keys** move and **z** and **x** dig, beside upstream's h, j, k,
  l, s and d; **q** quits as well as Ctrl+D (`cfg.h`, `usr.c`).
- **Follows a resize** (`gfx_resize`): the game window is put back in the
  middle of the terminal and drawn again.
- **Levels built in** (`io.c`, `game.c`, `tools/levels_data.sh`): the
  binary carries `levels/oldrunner.lvl` (read with `fmemopen`), so it runs
  from any folder; upstream looked for `./levels/` in the current
  directory. Defining `LEVELS_PATH` still reads them from a file.
- **Build**: the binary is always called `oldrunner` (the makefile named it
  after its folder), configure knows macOS, and the format-security
  warnings in `gfx_update_info` are gone.

## Packaging

- `asciiverse/build.sh` (`STATIC=1` in Alpine for the static musl binary)
  and `asciiverse/package.sh <target>` make the av archive;
  `.github/workflows/release.yml` builds Linux x86_64 and aarch64 and
  macOS on a `v*-av.*` tag, with .deb, .rpm, .apk and Arch packages
  (`asciiverse/nfpm.yaml`). No Windows build.
- `LICENSE` holds the BSD licence from the sources' headers.
- Preview: `asciiverse/record-preview.py` plays the first levels
  (breadth-first search to the gold, digging when a guard comes along the
  floor) while asciinema records `asciiverse/oldrunner.cast`.
