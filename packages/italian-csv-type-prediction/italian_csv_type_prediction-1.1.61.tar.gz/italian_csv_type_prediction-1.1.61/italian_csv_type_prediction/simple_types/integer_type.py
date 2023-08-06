from .float_type import FloatType


class IntegerType(FloatType):

    def convert(self, candidate) -> int:
        """Cast given candidate to integer."""
        return int(super().convert(candidate))

    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate can be considered integer."""
        if not super().validate(candidate, **kwargs):
            return False
        if isinstance(candidate, int):
            return True
        try:
            converted = super().convert(candidate)
            int(converted)
        except OverflowError:
            return False
        return converted.is_integer()
