from .integer_type import IntegerType


class YearType(IntegerType):

    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate can be considered a Year."""
        if super().validate(candidate, **kwargs):
            candidate = self.convert(candidate)
            return any(
                candidate >= _min and candidate <= _max
                for _min, _max in ((1990, 2030),)
            )
        return False
