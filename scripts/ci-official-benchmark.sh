#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OFFICIAL_REPO="${OFFICIAL_REPO:-https://github.com/zanfranceschi/rinha-de-backend-2026.git}"
OFFICIAL_REF="${OFFICIAL_REF:-main}"
RESULTS_DIR="${RESULTS_DIR:-benchmark-results}"
K6_IMAGE="${K6_IMAGE:-grafana/k6:latest}"
BENCHMARK_PULL_IMAGE="${BENCHMARK_PULL_IMAGE:-false}"
BENCHMARK_NO_BUILD="${BENCHMARK_NO_BUILD:-false}"
BENCHMARK_REPETITIONS="${BENCHMARK_REPETITIONS:-1}"

cd "$ROOT_DIR"
mkdir -p "$RESULTS_DIR"
rm -rf "$RESULTS_DIR/official"

compose_args=(--compatibility -f docker-compose.yml)

capture_docker_state() {
    local phase="$1"
    local output="$RESULTS_DIR/docker-state-$phase.txt"
    {
        printf 'phase=%s\n' "$phase"
        printf 'host_uname=%s\n' "$(uname -a)"
        docker compose "${compose_args[@]}" ps || true
        for container in $(docker compose "${compose_args[@]}" ps -q); do
            docker inspect --format 'name={{.Name}} image={{.Config.Image}} nano_cpus={{.HostConfig.NanoCpus}} memory={{.HostConfig.Memory}}' "$container" || true
        done
    } > "$output" 2>&1 || true
}

git clone --depth 1 --branch "$OFFICIAL_REF" "$OFFICIAL_REPO" "$RESULTS_DIR/official"

cleanup() {
    docker compose "${compose_args[@]}" logs --no-color > "$RESULTS_DIR/docker-compose.log" 2>&1 || true
    capture_docker_state cleanup
    docker compose "${compose_args[@]}" down --volumes --remove-orphans > /dev/null 2>&1 || true
}
trap cleanup EXIT

if [[ -n "${WEBAPI_IMAGE:-}" ]]; then
    printf 'Using WEBAPI_IMAGE=%s\n' "$WEBAPI_IMAGE"
fi

if [[ "$BENCHMARK_PULL_IMAGE" == "true" ]]; then
    docker compose "${compose_args[@]}" pull api1 api2 lb
fi

up_args=(up -d)
if [[ "$BENCHMARK_NO_BUILD" == "true" ]]; then
    up_args+=(--no-build)
else
    up_args+=(--build)
fi
docker compose "${compose_args[@]}" "${up_args[@]}"
capture_docker_state before

for attempt in {1..20}; do
    if curl -fsS http://localhost:9999/ready > /dev/null 2>&1; then
        break
    fi
    if [[ "$attempt" == "20" ]]; then
        printf 'Service did not become ready\n' >&2
        exit 1
    fi
    sleep 3
done

repeat_files=()
for repetition in $(seq 1 "$BENCHMARK_REPETITIONS"); do
    rm -f "$RESULTS_DIR/official/test/results.json" "$RESULTS_DIR/official/test/k6-report.html"
    docker run --rm \
        --network host \
        --user "$(id -u):$(id -g)" \
        -e K6_NO_USAGE_REPORT=true \
        -e K6_WEB_DASHBOARD=true \
        -e K6_WEB_DASHBOARD_PORT=-1 \
        -e K6_WEB_DASHBOARD_EXPORT=test/k6-report.html \
        -v "$ROOT_DIR/$RESULTS_DIR/official:/official" \
        -w /official \
        "$K6_IMAGE" run test/test.js
    capture_docker_state "after-$repetition"
    result_file="$RESULTS_DIR/results-repetition-$repetition.json"
    cp "$RESULTS_DIR/official/test/results.json" "$result_file"
    repeat_files+=("$result_file")
    if [[ -f "$RESULTS_DIR/official/test/k6-report.html" ]]; then
        cp "$RESULTS_DIR/official/test/k6-report.html" "$RESULTS_DIR/k6-report-repetition-$repetition.html"
    fi
done

cp "${repeat_files[0]}" "$RESULTS_DIR/results.json"
if [[ -f "$RESULTS_DIR/k6-report-repetition-1.html" ]]; then
    cp "$RESULTS_DIR/k6-report-repetition-1.html" "$RESULTS_DIR/k6-report.html"
fi
jq . "$RESULTS_DIR/results.json"
