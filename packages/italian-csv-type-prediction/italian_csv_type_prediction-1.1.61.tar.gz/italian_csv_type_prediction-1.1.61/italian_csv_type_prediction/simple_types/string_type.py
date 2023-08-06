from .simple_type import SimpleTypePredictor
from .float_type import FloatType
from .nan_type import NaNType


class StringType(SimpleTypePredictor):

    def __init__(self):
        self._float_predictor = FloatType()
        self._nan_predictor = NaNType()

    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate is a string"""
        return (
            not self._float_predictor.validate(candidate) and
            not self._nan_predictor.validate(candidate) and
            isinstance(candidate, str)
        )
