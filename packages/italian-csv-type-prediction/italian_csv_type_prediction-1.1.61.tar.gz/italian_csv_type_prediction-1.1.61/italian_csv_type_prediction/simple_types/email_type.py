from validate_email import validate_email
from .string_type import StringType


class EMailType(StringType):
    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate matches rules for emails."""
        return super().validate(candidate, **kwargs) and validate_email(candidate)
