#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
GOAL="${GOAL:-Analyze the UK EV charging market and produce a 2-page investment brief.}"

echo "Waiting for API at ${API_URL}/healthz ..."
for _ in $(seq 1 60); do
  if curl -fsS "${API_URL}/healthz" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
curl -fsS "${API_URL}/healthz" >/dev/null

echo "Creating job..."
CREATE_RESPONSE="$(curl -fsS -X POST "${API_URL}/jobs" \
  -H 'Content-Type: application/json' \
  -d "$(python3 -c "import json,sys; print(json.dumps({'goal': sys.argv[1]}))" "${GOAL}")")"

JOB_ID="$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['id'])" "${CREATE_RESPONSE}")"
echo "Job id: ${JOB_ID}"

for _ in $(seq 1 60); do
  JOB="$(curl -fsS "${API_URL}/jobs/${JOB_ID}")"
  STATUS="$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['status'])" "${JOB}")"
  echo "status=${STATUS}"
  if [[ "${STATUS}" == "completed" ]]; then
    REPORT="$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('final_report') or '')" "${JOB}")"
    if [[ -z "${REPORT}" ]]; then
      echo "Job completed without a final report" >&2
      exit 1
    fi
    echo "E2E smoke passed"
    exit 0
  fi
  if [[ "${STATUS}" == "failed" ]]; then
    echo "${JOB}" >&2
    echo "Job failed" >&2
    exit 1
  fi
  sleep 2
done

echo "Timed out waiting for job ${JOB_ID}" >&2
exit 1
