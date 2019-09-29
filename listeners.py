"""
A few listeners/widgets
"""

from bear_hug.widgets import Label, Listener


class ScoreLabel(Label):
    """
    Scores for the destroyed enemy tanks
    """
    pass


class SpawnerListener(Listener):
    """
    Spawns enemy tanks on cooldown, until there are enough of them
    """
    pass