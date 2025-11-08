#!/usr/bin/env bash
# Control script for generator container lifecycle management

set -e

CONTAINER_NAME="generator"

function show_usage() {
    cat << EOF
Usage: $0 {pause|resume|status}

Commands:
    pause   - Pause generation (send SIGUSR1)
    resume  - Resume generation (send SIGUSR2)
    status  - Show current generation status

Examples:
    $0 pause
    $0 resume
    $0 status
EOF
}

function check_container() {
    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "ERROR: Container '${CONTAINER_NAME}' is not running"
        echo "Start it with: cd docker && docker compose up -d"
        exit 1
    fi
}

function pause_generator() {
    check_container
    echo "Pausing generator..."
    docker exec "${CONTAINER_NAME}" kill -SIGUSR1 1
    echo "✓ Pause signal sent (SIGUSR1)"
    echo "Generation will pause after completing current batch"
}

function resume_generator() {
    check_container
    echo "Resuming generator..."
    docker exec "${CONTAINER_NAME}" kill -SIGUSR2 1
    echo "✓ Resume signal sent (SIGUSR2)"
    echo "Generation will resume from next scheduled interval"
}

function show_status() {
    check_container
    echo "Generator container status:"
    echo "----------------------------------------"
    docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "Recent logs:"
    echo "----------------------------------------"
    docker logs --tail 10 "${CONTAINER_NAME}" 2>&1 | grep -E "(PAUSE|RESUME|batch generated|Starting)" || echo "No recent activity"
    echo ""
    echo "State file (if exists):"
    echo "----------------------------------------"
    docker exec "${CONTAINER_NAME}" cat /data/manifests/generator_state.json 2>/dev/null | python -m json.tool || echo "No state file yet"
}

# Main
case "${1:-}" in
    pause)
        pause_generator
        ;;
    resume)
        resume_generator
        ;;
    status)
        show_status
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
