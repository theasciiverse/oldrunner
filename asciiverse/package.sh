#!/bin/sh
# Packs Oldrunner into its archive for av: dist/oldrunner-<target>.tar.gz,
# with the binary, the README, the manual page, the licence and PATCHES.md.
#
#   asciiverse/package.sh x86_64-unknown-linux-musl
set -eu
cd "$(dirname "$0")/.."
target="$1"
stage="stage/oldrunner"
rm -rf "$stage" && mkdir -p "$stage" dist
cp oldrunner README LICENSE oldrunner.6 PATCHES.md "$stage/"
tar --owner=0 --group=0 --numeric-owner -czf "dist/oldrunner-$target.tar.gz" -C "$stage" . 2>/dev/null \
  || tar -czf "dist/oldrunner-$target.tar.gz" -C "$stage" .
ls -l dist
