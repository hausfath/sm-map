#!/usr/bin/env bash
# Serve the viewer locally (needs HTTP, not file://, for the data fetches).
cd "$(dirname "$0")/.."
echo "http://localhost:${1:-8010}/index.html"
exec /opt/homebrew/bin/python3.13 -m http.server "${1:-8010}" --directory src
