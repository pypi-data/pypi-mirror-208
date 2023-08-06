from .set_type_predictor import SetTypePredictor
from .string_type import StringType
from ..datasets import load_regions


class RegionType(StringType):

    def __init__(self):
        super().__init__()
        self._predictor = SetTypePredictor(
            load_regions(), normalize_values=True)

    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate is a valid region."""
        return super().validate(candidate, **kwargs) and self._predictor.validate(candidate)
