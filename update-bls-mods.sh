#!/bin/sh
# The script Blocky Survival uses is more complicated than this one because
# the bot runs as a different user and has to `su` into the correct user and
# fix file permissions.

set -e

cd /path/to/mods/dir
git pull
git submodule sync --recursive
git submodule update --recursive --init
