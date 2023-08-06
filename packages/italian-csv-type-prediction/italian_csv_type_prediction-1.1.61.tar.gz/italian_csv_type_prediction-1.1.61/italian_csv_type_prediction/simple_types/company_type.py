from .set_type_predictor import SetTypePredictor
from .string_type import StringType


class CompanyType(StringType):

    def __init__(self, **kwargs):
        """Create new surname type predictor."""
        super().__init__()

    @property
    def fuzzy(self) -> bool:
        return True

    def validate(self, candidate, fiscal_code: str = None, italian_vat_code: str = None, **kwargs) -> bool:
        """Return boolean representing if given candidate is a valid company type."""
        if not super().validate(candidate, **kwargs):
            return False

        return italian_vat_code is not None and fiscal_code is None
