from .set_type_predictor import SetTypePredictor
from .string_type import StringType
from ..datasets import load_municipalities


class MunicipalityType(StringType):

    def __init__(self):
        super().__init__()
        self._predictor = SetTypePredictor(
            load_municipalities(), normalize_values=True)

    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate is a valid municipality."""
        return super().validate(candidate, **kwargs) and self._predictor.validate(candidate)
