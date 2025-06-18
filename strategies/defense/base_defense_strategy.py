class BaseDefenseStrategy:
    def __init__(self, team, field):
        """
        Base class for all defense strategies.
        :param team: Team object representing the blue team
        :param field: Field object for size and margin reference
        """
        self.team = team
        self.field = field

    def apply(self):
        """
        This method should be implemented by all subclasses to apply the strategy
        """
        raise NotImplementedError("Subclasses must implement apply() method")