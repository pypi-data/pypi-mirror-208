from ..datasets import load_boolean
from .set_type_predictor import SetTypePredictor
from .simple_type import SimpleTypePredictor


class BooleanType(SimpleTypePredictor):

    def __init__(self):
        """Create new float type predictor based on regex."""
        super().__init__()
        self._remapping = {
            "F": [
                False, "falso", "no", "false", "n", "f"
            ],
            "V": [
                True, "si", "true", "vero", "s", "v", "t"
            ]
        }
        self._predictor = SetTypePredictor(
            load_boolean(),
            normalize_values=True
        )

    def convert(self, candidate):
        for key, values in self._remapping.items():
            if candidate.lower() in values:
                return key
        return candidate

    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate is a valid region."""
        return self._predictor.validate(candidate)
