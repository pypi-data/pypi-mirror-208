import phonenumbers
from .string_type import StringType
from .date_type import DateType


class PhoneNumberType(StringType):

    def __init__(self):
        super().__init__()
        self._date = DateType()

    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate matches rules for Codice Fiscale values."""
        if super().validate(candidate, **kwargs) and not self._date.validate(candidate):
            try:
                return phonenumbers.is_valid_number(phonenumbers.parse(candidate, "IT"))
            except phonenumbers.NumberParseException:
                pass
        return False
