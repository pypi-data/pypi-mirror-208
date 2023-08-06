from ..utils import normalize
from .regex_type_predictor import RegexTypePredictor
from .string_type import StringType


class PlateType(StringType):

    def __init__(self):
        """Create new Plate type predictor based on regex."""
        super().__init__()
        self._predictor = RegexTypePredictor([
            r"^[a-z]{2}\s?[0-9]{3}\s?[a-z]{1}$",
            r"^[a-z]{2}\s?[0-9]{3}\s?[a-z]{2}$",
            r"^[a-z]{2}\s?[0-9]{4}\s?[a-z]{1}$",
            r"^[a-z]{2}\s?[0-9]{4}\s?[a-z]{2}$",
            r"^[a-z]{2}\s?[0-9]{2}\s?[a-z]{3}$",
            r"^[a-z]{2}\s?[0-9]{5}\s?[a-z]{1}$",
            r"^[a-z]{3}\s?[0-9]{2}\s?[a-z]{1}$",
            r"^[a-z]{3}\s?[0-9]{3}\s?[a-z]{1}$",
            r"^[a-z]{3}\s?[0-9]{4}\s?[a-z]{1}$",
            r"^[a-z]{3}\s?[0-9]{1}\s?[a-z]{3}$",
            r"^[a-z]{1}\s?[0-9]{1}\s?[a-z]{4}$",
            r"^[a-z]{1}\s?[0-9]{2}\s?[a-z]{3}$",
            r"^[a-z]{1}\s?[0-9]{4}\s?[a-z]{2}$",
            r"^[a-z]{1}\s?[0-9]{4,5}\s?[a-z]{1}$",
            r"^[a-z]{1}\s?[0-9]{3}\s?[a-z]{1,3}$",
            r"^[a-z]{1}\s?[0-9]{4,6}$",
            r"^[a-z]{2}\s?[0-9]{3,6}$",
            r"^[a-z]{3}\s?[0-9]{2,5}$",
            r"^[a-z]{4}\s?[0-9]{1,4}$",
            r"^[a-z]{5}\s?[0-9]{1,3}$",
            r"^[0-9]{2}\s?[a-z]{4}$",
            r"^[0-9]{4}\s?[a-z]{2,3}$",
            r"^[0-9]{1}\s?[a-z]{1}\s?[0-9]{5}$",
            r"^[0-9]{1}\s?[a-z]{2}\s?[0-9]{4}$",
            r"^[0-9]{1}\s?[a-z]{3}\s?[0-9]{2,3}$",
            r"^[0-9]{3}\s?[a-z]{1}\s?[0-9]{3}$",
            r"^[0-9]{3}\s?[a-z]{3}\s?[0-9]{2}$",
            r"^[0-9]{2}\s?[a-z]{2}\s?[0-9]{2}$",
            r"^[0-9]{2}\s?[a-z]{3}\s?[0-9]{1}$",
        ])

    def convert(self, candidate):
        return str(candidate).upper()

    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate matches regex for ."""
        if not super().validate(candidate, **kwargs):
            return False
        count = len(candidate)
        if count > 8 or count < 5:
            return False
        return self._predictor.validate(candidate)
