from codicefiscale.codicefiscale import is_valid as is_fiscal_code_valid
from .string_type import StringType


class ItalianFiscalCodeType(StringType):

    def convert(self, candidate):
        return str(candidate).upper()

    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate matches rules for Codice Fiscale values."""
        return super().validate(candidate, **kwargs) and is_fiscal_code_valid(candidate)
