from .set_regex_type_predictor import SetRegexTypePredictor
from ..datasets import load_tax


class TaxType(SetRegexTypePredictor):

    def __init__(self):
        super().__init__(load_tax())

    @property
    def fuzzy(self) -> bool:
        return True
