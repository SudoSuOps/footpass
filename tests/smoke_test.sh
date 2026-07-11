#!/usr/bin/env bash
# End-to-end smoke test against a RUNNING FootPass stack.
# Usage: bash tests/smoke_test.sh [base_url]   (default http://localhost)
set -euo pipefail
BASE="${1:-http://localhost}"
fail=0

check() {
  local name="$1" url="$2" expect="${3:-200}"
  code="$(curl -s -o /dev/null -w '%{http_code}' "$url" || echo 000)"
  if [ "$code" = "$expect" ]; then
    echo "  [ok]   $name ($code)"
  else
    echo "  [FAIL] $name -> $code (expected $expect)  $url"
    fail=1
  fi
}

echo "== FootPass smoke test against $BASE =="
check "UI root"          "$BASE/"                 200
check "API health"       "$BASE/api/health"       200
check "API system"       "$BASE/api/system"       200
check "API settings"     "$BASE/api/settings"     200
check "Camera status"    "$BASE/api/camera/status" 200
check "Backup status"    "$BASE/api/backup/status" 200
check "OpenAPI schema"   "$BASE/openapi.json"     200

# health payload should say healthy + db ok
if curl -s "$BASE/api/health" | grep -q '"database":"ok"'; then
  echo "  [ok]   database reports ok"
else
  echo "  [FAIL] database not ok in /api/health"
  fail=1
fi

echo ""
[ "$fail" = "0" ] && echo "ALL SMOKE CHECKS PASSED ✅" || { echo "SMOKE TEST FAILED ❌"; exit 1; }
