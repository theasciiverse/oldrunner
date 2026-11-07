#!/bin/sh
# Writes a level file as C source (oldrunner_lvl and its length), so the
# levels are built into the binary. Plain od and sed, for Linux, macOS and
# busybox alike.
#   sh tools/levels_data.sh levels/oldrunner.lvl > levels_data.c
set -e
echo "/* Made from $1 by tools/levels_data.sh; do not edit. */"
echo "const char oldrunner_lvl[] = {"
od -An -v -tx1 "$1" | sed -e 's/[0-9a-f][0-9a-f]/0x&,/g' -e 's/^ *//' -e 's/ *$//'
echo "0 };"
echo "const unsigned long oldrunner_lvl_len = sizeof oldrunner_lvl - 1;"
