from .integer_type import IntegerType
from .set_type_predictor import SetTypePredictor
from ..datasets import load_caps
from typing import List


class ItalianZIPCodeType(SetTypePredictor):

    def __init__(self, zip_codes: List[str] = None):
        """Create new Italian ZIP Code type predictor based on regex.

        Parameters
        ---------------------
        zip_codes: List[str] = None,
            List of zip codes to consider.
            By default, all the valid italian Zip Codes.
        """
        self._integer = IntegerType()
        if zip_codes is None:
            zip_codes = load_caps()
        super().__init__(zip_codes)

    def hard_convert(self, candidate) -> str:
        """Convert given candidate to CAP."""
        if self._integer.validate(candidate):
            candidate = self._integer.convert(candidate)
        return str(candidate)

    def convert(self, candidate) -> str:
        """Convert given candidate to CAP."""
        return self.hard_convert(candidate).zfill(5)

    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate matches regex for CAP values."""
        return super().validate(self.hard_convert(candidate))
