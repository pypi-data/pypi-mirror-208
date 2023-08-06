from .generic_italian_zip_code_type import GenericItalianZIPCodeType
from .fuzzy_italian_zip_code_type import FuzzyItalianZIPCodeType
from ..datasets import load_generic_caps


class FuzzyGenericItalianZIPCodeType(FuzzyItalianZIPCodeType, GenericItalianZIPCodeType):

    def __init__(self):
        """Create new object for predicting generic Italian Zip Codes."""
        super().__init__()
