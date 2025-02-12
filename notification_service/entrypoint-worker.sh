#!/usr/bin/env bash

WORKER_TYPE=$1

case $WORKER_TYPE in
    scheduler)
        SETTINGS_MODULE="src.workers.SchedulerWorkerSettings"
        ;;
    former)
        SETTINGS_MODULE="src.workers.FormerWorkerSettings"
        ;;
    repeater)
        SETTINGS_MODULE="src.workers.RepeaterWorkerSettings"
        ;;
    *)
        echo "Unknown worker type: $WORKER_TYPE"
        exit 1
        ;;
esac

echo "Starting $WORKER_TYPE worker..."
uv run python -m src.workers.main scheduler
