from .set_regex_type_predictor import SetRegexTypePredictor
from ..datasets import load_document_types


class DocumentType(SetRegexTypePredictor):

    def __init__(self):
        super().__init__(load_document_types())

    @property
    def fuzzy(self) -> bool:
        return True
