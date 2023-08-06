from .extractor import Extractor
from typing import Dict


class DefaultExtractor(Extractor):
    def extract(self, candidate: str, candidate_type: str, **kwargs) -> Dict:
        return self.build_dictionary(
            candidate=candidate,
            values={
                candidate_type: [candidate]
            }
        )
