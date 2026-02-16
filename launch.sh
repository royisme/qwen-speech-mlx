#!/bin/bash

SKILL_DIR="$(dirname "$0")"
cd "$SKILL_DIR"

# Service type: tts (default) or asr
SERVICE_TYPE="${2:-tts}"

if [ "$SERVICE_TYPE" = "asr" ]; then
    PORT=9956
    SERVICE_CMD="qwen-asr"
    LOG_FILE="service_asr.log"
    PID_FILE="service_asr.pid"
    SERVICE_LABEL="Qwen3-ASR MLX"
else
    PORT=9955
    SERVICE_CMD="qwen-tts"
    LOG_FILE="service_tts.log"
    PID_FILE="service_tts.pid"
    SERVICE_LABEL="Qwen3-TTS MLX"
fi

HOST="127.0.0.1"

function start() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "Service is already running (PID: $PID)"
            exit 0
        else
            echo "Found stale PID file. Removing..."
            rm "$PID_FILE"
        fi
    fi

    echo "Starting $SERVICE_LABEL Service on port $PORT..."
    nohup uv run "$SERVICE_CMD" --host "$HOST" --port "$PORT" > "$LOG_FILE" 2>&1 &

    PID=$!
    echo "$PID" > "$PID_FILE"
    echo "Service started with PID $PID"
    echo "Logs: $LOG_FILE"
}

function stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Service is not running (PID file not found)"
        return
    fi

    PID=$(cat "$PID_FILE")

    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping $SERVICE_LABEL service (PID $PID)..."
        kill "$PID"

        TIMEOUT=10
        COUNT=0
        while kill -0 "$PID" 2>/dev/null; do
            sleep 1
            COUNT=$((COUNT+1))
            if [ "$COUNT" -ge "$TIMEOUT" ]; then
                echo "Service did not stop gracefully. Forcing kill..."
                kill -9 "$PID"
                break
            fi
        done

        echo "Service stopped."
        rm "$PID_FILE"
    else
        echo "Service process $PID not found. Cleaning up PID file..."
        rm "$PID_FILE"
    fi
}

function status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "$SERVICE_LABEL is running (PID: $PID, port: $PORT)"
            return 0
        else
            echo "$SERVICE_LABEL is not running (stale PID file)"
            return 1
        fi
    else
        echo "$SERVICE_LABEL is not running"
        return 3
    fi
}

# Command dispatch
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 1
        start
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status} [tts|asr]"
        exit 1
        ;;
esac
