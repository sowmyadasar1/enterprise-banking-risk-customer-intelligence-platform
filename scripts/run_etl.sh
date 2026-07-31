#!/usr/bin/env bash
set -e

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
echo "[$TIMESTAMP] Starting ETL Pipeline..."

# Run the ETL pipeline module
python -m src.etl.pipeline

END_TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
echo "[$END_TIMESTAMP] ETL Pipeline completed successfully."
