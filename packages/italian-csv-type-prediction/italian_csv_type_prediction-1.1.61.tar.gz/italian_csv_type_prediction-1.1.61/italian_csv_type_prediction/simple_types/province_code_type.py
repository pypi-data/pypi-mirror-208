from ..datasets import load_provinces_codes
from .set_type_predictor import SetTypePredictor
from .string_type import StringType


class ProvinceCodeType(StringType):

    def __init__(self):
        super().__init__()
        self._predictor = SetTypePredictor(
            load_provinces_codes(), normalize_values=True)

    def convert(self, candidate):
        return str(candidate).upper()

    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate is a valid province code."""
        return super().validate(candidate, **kwargs) and self._predictor.validate(candidate)
