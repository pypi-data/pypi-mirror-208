from .italian_zip_code_type import ItalianZIPCodeType


class FuzzyItalianZIPCodeType(ItalianZIPCodeType):

    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate matches regex for CAP values."""
        return super().validate(self.convert(candidate))
