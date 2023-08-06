from .set_type_predictor import SetTypePredictor
from .string_type import StringType
from ..datasets import load_biological_sex


class BiologicalSexType(StringType):

    def __init__(self):
        super().__init__()
        self._predictor = SetTypePredictor(
            load_biological_sex(), normalize_values=True)

    def convert(self, candidate):
        return {
            'generico': "G",
            'maschio': "M",
            'uomo': "M",
            'femmina': "F",
            'donna': "F"
        }.get(candidate.lower(), candidate)

    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate is a valid biological sex."""
        return super().validate(candidate, **kwargs) and self._predictor.validate(candidate)
