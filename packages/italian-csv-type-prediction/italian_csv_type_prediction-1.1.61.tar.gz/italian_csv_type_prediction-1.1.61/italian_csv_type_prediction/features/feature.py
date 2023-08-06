class Feature:
    """A text related feature."""

    @property
    def name(self):
        """Return type identified by this predictor."""
        return self.__class__.__name__[:-4]

    def score(self, value)->float:
        raise NotImplementedError("This method must be implemented in children classes.")