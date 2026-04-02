#!/usr/bin/env bash
set -euo pipefail

cat <<'EOF'
Submitty E2E setup container

This container provides a prepared environment but does NOT start external
services (e.g. PostgreSQL, PHP-FPM). Start required services separately
before running integration tests.

To open an interactive shell in this image (after building):
  docker run --rm -it submitty/e2e-setup:latest /bin/bash

For CI usage, run the container where required services are available.
EOF

exec "$@"
