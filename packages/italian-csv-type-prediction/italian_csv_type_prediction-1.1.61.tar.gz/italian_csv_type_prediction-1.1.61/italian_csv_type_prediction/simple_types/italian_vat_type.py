from stdnum.it.iva import is_valid as is_vat_valid, compact as compact_vat
from .simple_type import SimpleTypePredictor
from .integer_type import IntegerType
from .float_type import FloatType
from .date_type import DateType
from ..features import Symbols

class ItalianVATType(SimpleTypePredictor):
    def __init__(self):
        """Create new IVA type predictor based on rules."""
        super().__init__()
        self._integer = IntegerType()
        self._float = FloatType()
        self._date = DateType()
        self._symbols = Symbols()

    def convert(self, candidate):
        candidate = compact_vat(str(candidate))
        if self._integer.validate(candidate):
            candidate = self._integer.convert(candidate)
        candidate = str(candidate)
        candidate = candidate.replace(" ", "")
        return candidate.zfill(11)

    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate is an IVA."""
        if self._float.validate(candidate):
            if not self._integer.validate(candidate):
                # If it is an float but not an integer it is not a valid VAT.
                return False
        elif self._symbols.score(candidate) > 0:
            return False

        if len(str(candidate)) < 8:
            return False

        converted = self.convert(candidate)

        return is_vat_valid(converted)
