#!/bin/sh
# Builds Oldrunner with its own configure script and GNUmakefile; the
# levels are built into the binary, so ./oldrunner is all there is.
#
#   asciiverse/build.sh            # Linux (ncursesw) or macOS (system ncurses)
#   STATIC=1 asciiverse/build.sh   # Alpine: static musl binary
set -eu
cd "$(dirname "$0")/.."
make clean >/dev/null 2>&1 || true
./configure
if [ -n "${STATIC:-}" ]; then
  make LDFLAGS="-static -s"
else
  make
fi
echo "built oldrunner"
