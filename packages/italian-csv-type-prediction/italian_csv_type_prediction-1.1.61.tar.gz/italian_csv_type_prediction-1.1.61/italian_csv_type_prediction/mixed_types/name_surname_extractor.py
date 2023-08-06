from .extractor import Extractor
from ..simple_types import NameSurnameType
from typing import Dict


class NameSurnameExtractor(Extractor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._name_surname = NameSurnameType()

    def extract(self, candidate: str, candidate_type:str, **kwargs) -> Dict:
        name, surname = self._name_surname.convert(candidate, **kwargs)
        return self.build_dictionary(
            candidate=candidate,
            values={
                "Name": [name],
                "Surname": [surname]
            }
        )
