.PHONY: help build up down test lint register-models

help:
	@echo "Enterprise MLOps Commands:"
	@echo "  make build           - Build Docker images"
	@echo "  make up              - Start the platform (API, MLflow, DB)"
	@echo "  make down            - Stop the platform"
	@echo "  make test            - Run API tests"
	@echo "  make lint            - Run flake8"
	@echo "  make register-models - Register trained models into MLflow"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

test:
	python3 -m pytest src/api/tests/test_api.py -v --tb=short

lint:
	python3 -m flake8 src/

register-models:
	python3 src/mlops/mlflow_tracker.py
