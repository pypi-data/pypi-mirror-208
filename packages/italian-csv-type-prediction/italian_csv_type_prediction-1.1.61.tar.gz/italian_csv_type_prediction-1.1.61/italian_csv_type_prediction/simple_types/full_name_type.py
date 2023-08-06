from .string_type import StringType
from .name_type import NameType
from .surname_type import SurnameType
from typing import Tuple
from ..exceptions import IllegalStateError

class FullNameType(StringType):

    def __init__(self, separators: Tuple[str] = (",", ";", " ")):
        super().__init__()
        self._name = NameType()
        self._surname = SurnameType()
        self._separators = separators

    def _validate(self, first:str, second:str, fiscal_code: str = None, **kwargs) -> bool:
        raise NotImplementedError("This method must be implemented in child classes.")

    def _convert(self, first:str, second:str):
        raise NotImplementedError("This method must be implemented in child classes.")

    def convert(self, candidate, **kwargs):
        for separator in self._separators:
            if candidate.count(separator) == 1:
                full_names = (candidate.split(separator),)
            elif not any(sep in candidate for sep in self._separators[:-1]) and candidate.count(separator)>0:
                words = candidate.split(" ")
                full_names = [
                    (" ".join(words[:i]), " ".join(words[i:]))
                    for i in range(1, len(words))
                ]
            else:
                continue
            for first, second in full_names:
                if self._validate(first, second, **kwargs):
                    return self._convert(first, second)
        raise IllegalStateError("Illegal state reached.")

    def validate(self, candidate, **kwargs) -> bool:
        if not super().validate(candidate):
            return False

        try:
            self.convert(candidate, **kwargs)
            return True
        except IllegalStateError:
            return False