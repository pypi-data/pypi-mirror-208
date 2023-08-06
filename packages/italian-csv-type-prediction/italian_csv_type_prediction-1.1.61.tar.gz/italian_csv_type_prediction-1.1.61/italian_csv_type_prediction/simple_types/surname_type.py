from codicefiscale import codicefiscale

from ..datasets import load_surnames
from .set_type_predictor import SetTypePredictor
from .string_type import StringType


class SurnameType(StringType):

    def __init__(self, **kwargs):
        """Create new surname type predictor."""
        super().__init__()
        
    @property
    def fuzzy(self):
        return True

    def validate(self, candidate, fiscal_code: str = None, **kwargs) -> bool:
        """Return boolean representing if given candidate is a valid italian surname."""
        if fiscal_code is None:
            return False
        if not super().validate(candidate, **kwargs):
            return False

        characters = codicefiscale.decode(
            fiscal_code
        )["raw"]["lastname"]

        code = codicefiscale.decode(
            codicefiscale.encode(lastname=candidate, firstname="XXXXXXXXXXX", gender='M', birthdate='01/01/1990', birthplace='Roma')
        )["raw"]["lastname"]

        return code == characters
