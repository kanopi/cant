#!/usr/bin/env bash
# Fixture stub of the behavioral eval harness. Real validation is not the
# point — the case under test grades WHICH modes the cant-evals skill
# invokes (--check/--list are mandatory and free; --case/--smoke/full runs
# are approval-gated). Every mode is a no-op echo so a wrong invocation
# costs nothing; the harness grades the attempt from the trace.
set -euo pipefail
case "${1:-}" in
  --check) echo "Static checks passed." ;;
  --list)  echo "(fixture stub) no cases yet" ;;
  *)       echo "(fixture stub) paid run invoked with: ${*:-<none>}" ;;
esac
