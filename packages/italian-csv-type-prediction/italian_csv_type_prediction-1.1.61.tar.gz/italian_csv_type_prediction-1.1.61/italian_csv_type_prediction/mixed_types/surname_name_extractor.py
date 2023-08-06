from .extractor import Extractor
from ..simple_types import SurnameNameType
from typing import Dict


class SurnameNameExtractor(Extractor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._name_surname = SurnameNameType()

    def extract(self, candidate: str, candidate_type:str, **kwargs) -> Dict:
        name, surname = self._name_surname.convert(candidate, **kwargs)
        return self.build_dictionary(
            candidate=candidate,
            values={
                "Name": [name],
                "Surname": [surname]
            }
        )
