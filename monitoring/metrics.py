"""System metrics collection and recording."""

from typing import Dict


class MetricsCollector:
    """Collects and records system metrics."""

    def record_api_latency(self, endpoint: str, latency_ms: float) -> None:
        """Record API request latency."""
        raise NotImplementedError("Implemented in Phase N")

    def record_pipeline_duration(self, pipeline_name: str, duration_s: float) -> None:
        """Record ML pipeline execution duration."""
        raise NotImplementedError("Implemented in Phase N")

    def record_model_prediction(self, model_name: str, status: str) -> None:
        """Record model prediction event."""
        raise NotImplementedError("Implemented in Phase N")

    def get_dashboard_metrics(self) -> Dict[str, float]:
        """Get aggregated metrics for dashboards."""
        raise NotImplementedError("Implemented in Phase N")
