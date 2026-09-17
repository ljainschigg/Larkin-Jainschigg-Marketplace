#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${CLAUDE_PLUGIN_DATA}/node"
SERVER_DIR="${CLAUDE_PLUGIN_ROOT}/server"

mkdir -p "${DATA_DIR}"

# Install dependencies if not present, or if package.json has changed
if [ ! -f "${DATA_DIR}/node_modules/.installed" ] || \
   [ "${SERVER_DIR}/package.json" -nt "${DATA_DIR}/node_modules/.installed" ]; then
  cp "${SERVER_DIR}/package.json" "${DATA_DIR}/"
  npm install --prefix "${DATA_DIR}" --ignore-scripts --silent
  touch "${DATA_DIR}/node_modules/.installed"
fi

# Always copy the server script so updates take effect on reinstall
cp "${SERVER_DIR}/index.js" "${DATA_DIR}/"

exec node "${DATA_DIR}/index.js"
