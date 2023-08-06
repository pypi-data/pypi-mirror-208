from .set_regex_type_predictor import SetRegexTypePredictor
from ..datasets import load_address_starters


class FuzzyAddressType(SetRegexTypePredictor):

    def __init__(self):
        super().__init__(load_address_starters())

    @property
    def fuzzy(self) -> bool:
        return True
