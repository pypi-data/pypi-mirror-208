from .full_name_type import FullNameType
from typing import Tuple


class SurnameNameType(FullNameType):

    def _convert(self, surname: str, name: str) -> Tuple[str, str]:
        return name, surname

    def _validate(self, surname: str, name: str, **kwargs) -> bool:
        return self._name.validate(name, **kwargs) and self._surname.validate(surname, **kwargs)
