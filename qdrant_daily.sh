#!/bin/bash

# ===== CONFIG =====
PROJECT_DIR="/home/jaka/news-generator"
VENV="$PROJECT_DIR/venv"
PY_SCRIPT="$PROJECT_DIR/qdrant.py"

CONTAINER="qdrant"
CONTAINER_SNAPSHOT_PATH="/qdrant/snapshots"

BACKUP_DIR="$PROJECT_DIR/qdrant_snapshots"
DATE=$(date +"%Y-%m-%d")
DEST="$BACKUP_DIR/$DATE"

LOGFILE="$BACKUP_DIR/qdrant_backup.log"

# ===== START =====
echo "===== Script started: $(date) =====" >> $LOGFILE

# Create destination folder
mkdir -p "$DEST"

# Run Python script
echo "Running Python script..." >> $LOGFILE
$VENV/bin/python "$PY_SCRIPT" >> $LOGFILE 2>&1

# Copy snapshots from Docker container
echo "Copying snapshots from container..." >> $LOGFILE
/usr/bin/docker cp $CONTAINER:$CONTAINER_SNAPSHOT_PATH/. "$DEST" >> $LOGFILE 2>&1

echo "Backup finished: $(date)" >> $LOGFILE
echo "" >> $LOGFILE
