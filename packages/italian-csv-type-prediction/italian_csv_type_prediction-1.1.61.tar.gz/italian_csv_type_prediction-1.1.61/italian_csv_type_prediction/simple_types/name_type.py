from .string_type import StringType
from .set_type_predictor import SetTypePredictor
from ..datasets import load_names
from codicefiscale import codicefiscale


class NameType(StringType):

    def __init__(self, **kwargs):
        """Create new surname type predictor."""
        super().__init__()

    @property
    def fuzzy(self) -> bool:
        return True

    def validate(self, candidate, fiscal_code: str = None, **kwargs) -> bool:

        """Return boolean representing if given candidate is a valid italian name."""
        if fiscal_code is None:
            return False
        if not super().validate(candidate, **kwargs):
            return False

        characters = codicefiscale.decode(
            fiscal_code
        )["raw"]["firstname"]

        code = codicefiscale.decode(
            codicefiscale.encode(lastname="XXXXXXXXXXXXXXX", firstname=candidate, gender='M', birthdate='01/01/1990', birthplace='Roma')
        )["raw"]["firstname"]

        return code == characters
