from .single_type_column import IntegerType
from typing import List, Dict


class NumericIdType(IntegerType):

    def __init__(self, density: float = 0.95):
        """Create new NumericId Predictor based on data within column.

        Parameters
        --------------------------
        density: float = 0.95,
            Minimal density from minimum integer to maximum integer.
        """
        super().__init__()
        self._density = density

    def validate(self, values: List, **kwargs: Dict) -> List[bool]:
        """Return list of booleans representing, for each value, if are indices."""
        predictions = super().validate(values, **kwargs)

        if not any(predictions):
            return [False]*len(values)

        integer_values = [
            self._main.convert(value)
            for value, prediction in zip(values, predictions)
            if prediction
        ]

        _min, _max = min(integer_values), max(integer_values)

        if _min == _max:
            return False

        unique_values = len(set(integer_values))

        are_indices = unique_values / (_max - _min) >= self._density

        return [
            are_indices and prediction
            for prediction in predictions
        ]
