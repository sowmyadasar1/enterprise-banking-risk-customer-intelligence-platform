"""Data preprocessor for loan default prediction."""
from typing import Any

class LoanPreprocessor:
    """Handles data preprocessing for loan defaults."""
    
    def fit(self, df: Any) -> 'LoanPreprocessor':
        """Fit the preprocessor to the data."""
        raise NotImplementedError("Implemented in Phase N")
        
    def transform(self, df: Any) -> Any:
        """Transform the data."""
        raise NotImplementedError("Implemented in Phase N")
        
    def fit_transform(self, df: Any) -> Any:
        """Fit and transform the data in one step."""
        raise NotImplementedError("Implemented in Phase N")
