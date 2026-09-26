"""
ETL Base Classes — Abstract interfaces for all ETL components.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple
import pandas as pd


@dataclass
class PipelineResult:
    """Dataclass to hold the result of an ETL pipeline stage."""

    success: bool
    records_in: int
    records_out: int
    records_rejected: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    stage: str = ""


class BaseExtractor(ABC):
    """Abstract base class for data extraction."""

    @abstractmethod
    def extract(self, source_path: str, **kwargs: Any) -> pd.DataFrame:
        """Extract data from a source and return as a DataFrame."""
        pass


class BaseValidator(ABC):
    """Abstract base class for data validation."""

    @abstractmethod
    def validate(
        self, df: pd.DataFrame, dataset_name: str
    ) -> Tuple[pd.DataFrame, PipelineResult]:
        """Validate data and return valid DataFrame and execution result."""
        pass


class BaseCleaner(ABC):
    """Abstract base class for data cleaning."""

    @abstractmethod
    def clean(
        self, df: pd.DataFrame, dataset_name: str
    ) -> Tuple[pd.DataFrame, PipelineResult]:
        """Clean data and return the cleaned DataFrame and execution result."""
        pass


class BaseTransformer(ABC):
    """Abstract base class for data transformation."""

    @abstractmethod
    def transform(
        self, df: pd.DataFrame, dataset_name: str, **context: Any
    ) -> Tuple[pd.DataFrame, PipelineResult]:
        """Transform data and return the transformed DataFrame and execution result."""
        pass


class BaseLoader(ABC):
    """Abstract base class for data loading."""

    @abstractmethod
    def load(self, df: pd.DataFrame, dest_path: str, layer: str) -> PipelineResult:
        """Load data to the destination and return execution result."""
        pass


class BaseQualityChecker(ABC):
    """Abstract base class for data quality checks."""

    @abstractmethod
    def check(self, df: pd.DataFrame, dataset_name: str, layer: str) -> Dict[str, Any]:
        """Run quality checks and return a dictionary of check results."""
        pass
