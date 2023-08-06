from typing import Dict
from ..utils import TranslateType
from ..simple_types import AnyTypePredictor


class Extractor:

    def __init__(self, translator: TranslateType = None, fail_on_collision: bool = False):
        """Abstract class for Extractor object.

        Parameters
        ------------------------
        translator: TranslateType = None,
            Optional translator type.
        fail_on_collision: bool = False,
            Whether to fail when a collision is detected.
        """
        self._translator = translator
        self._fail_on_collision = fail_on_collision
        self._converter = AnyTypePredictor()

    def extract(self, candidate: str, candidate_type: str, **kwargs) -> Dict:
        raise NotImplementedError(
            "This method must be implemented in the child classes.")

    @property
    def name(self):
        """Return type identified by this predictor."""
        return self.__class__.__name__[:-9]

    def _build_placeholder(self, candidate: str, values: Dict) -> str:
        if len(values) == 1:
            return "{{{0}}}".format(list(values.keys())[0])
        for key, values in values.items():
            for value in values:
                candidate = candidate.replace(value, "{{{0}}}".format(key), 1)
        return candidate

    def build_dictionary(self, candidate: str, values: Dict) -> str:
        values = {
            (
                self._translator.translate(key)
                if self._translator is not None else key
            ): [
                self._converter.convert(
                    key, value) if self._converter.supports(key) else value
                for value in values_list
            ]
            for key, values_list in values.items()
        }
        return {
            "placeholder": self._build_placeholder(candidate, values),
            "values": values
        }
