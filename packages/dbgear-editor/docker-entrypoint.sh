#!/bin/bash
set -e

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [DBGear-Editor] $1"
}

log "Starting DBGear Editor container..."

# Create necessary directories
mkdir -p /home/dbgear/.dbgear
mkdir -p /app/data

# Check if projects directory exists and has content
if [ -d "/app/data/projects" ] && [ "$(ls -A /app/data/projects)" ]; then
    log "Found project directories in /app/data/projects:"
    ls -la /app/data/projects/
fi

# Set default project if PROJECT_PATH is provided
if [ -n "$PROJECT_PATH" ]; then
    log "Default project path set to: $PROJECT_PATH"
    exec dbgear-editor --host 0.0.0.0 --port 8000 --project "$PROJECT_PATH" "$@"
else
    log "No default project specified. Starting editor for project management."
    exec dbgear-editor --host 0.0.0.0 --port 8000 "$@"
fi