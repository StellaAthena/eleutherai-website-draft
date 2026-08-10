#!/bin/bash
cd "$(dirname "$0")"
echo "=== Building EleutherAI site (offline mode) ==="
make build-offline
echo ""
echo "=== Serving on http://127.0.0.1:8068/ ==="
make serve-offline PORT=8068
