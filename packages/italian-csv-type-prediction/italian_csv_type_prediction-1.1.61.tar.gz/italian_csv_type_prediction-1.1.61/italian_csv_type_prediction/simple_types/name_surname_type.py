from .full_name_type import FullNameType
from typing import Tuple


class NameSurnameType(FullNameType):

    def _convert(self, name: str, surname: str) -> Tuple[str, str]:
        return name, surname

    def _validate(self, name: str, surname: str, **kwargs) -> bool:
        return self._name.validate(name, **kwargs) and self._surname.validate(surname, **kwargs)
