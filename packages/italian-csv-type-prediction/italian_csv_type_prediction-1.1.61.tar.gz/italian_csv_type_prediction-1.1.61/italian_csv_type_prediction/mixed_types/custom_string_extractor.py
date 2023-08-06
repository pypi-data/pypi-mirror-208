from ..simple_types import SimpleTypePredictor
from .extractor import Extractor
from ..utils import TranslateType


class CustomStringExtractor(SimpleTypePredictor, Extractor):
    """
    Abstract class for user-defined custom string extractors.
    """

    def __init__(self, translator: TranslateType = None):
        SimpleTypePredictor.__init__(self)
        Extractor.__init__(self, translator=translator)
