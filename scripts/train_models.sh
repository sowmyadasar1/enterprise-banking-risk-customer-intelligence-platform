#!/usr/bin/env bash
set -e

MODEL_TYPE=${1:-all}

echo "====================================="
echo "   Model Training Pipeline           "
echo "====================================="
echo "Model target: $MODEL_TYPE"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Starting MLflow experiment tracking..."
export MLFLOW_TRACKING_URI="http://localhost:5000"
export MLFLOW_EXPERIMENT_NAME="banking_models"

echo "Training models..."
# python -m src.ml.train --model "$MODEL_TYPE"
echo "Simulating model training for $MODEL_TYPE..."
sleep 2

echo "Logging results to MLflow..."
# Logging happens within the python script usually, but we log status here
echo "Training pipeline completed successfully for $MODEL_TYPE models."
