from .italian_zip_code_type import ItalianZIPCodeType
from ..datasets import load_generic_caps


class GenericItalianZIPCodeType(ItalianZIPCodeType):

    def __init__(self):
        """Create new object for predicting generic Italian Zip Codes."""
        super().__init__(load_generic_caps())
