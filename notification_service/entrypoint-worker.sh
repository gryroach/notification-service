#!/usr/bin/env bash

WORKER_TYPE=$1

case $WORKER_TYPE in
    scheduler)
        WORKER_MODULE="src.workers.scheduler"
        ;;
    repeater)
        WORKER_MODULE="src.workers.repeater"
        ;;
    *)
        echo "Unknown worker type: $WORKER_TYPE"
        exit 1
        ;;
esac

echo "Starting $WORKER_TYPE worker..."
uv run arq $WORKER_MODULE.scheduler_settings
