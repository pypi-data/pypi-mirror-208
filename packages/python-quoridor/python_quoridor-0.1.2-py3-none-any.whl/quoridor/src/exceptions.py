"""Module for all quoridor exceptions
"""


class InvalidMoveError(Exception):
    """
    Exception raised when a move is given in an invalid form.

    Parameters
    ----------
    message : str, optional
        The error message to display. Defaults to "Move is given in an invalid form".
    """

    def __init__(self, message="Move is given in an invalid form"):
        self.message = message
        super().__init__(self.message)


class IllegalPawnMoveError(Exception):
    """
    Exception raised when a pawn is moved illegally.

    Parameters
    ----------
    message : str, optional
        The error message to display. Defaults to "Illegal pawn move.".
    """

    def __init__(self, message="Illegal pawn move."):
        self.message = message
        super().__init__(self.message)


class IllegalWallPlacementError(Exception):
    """
    Exception raised when a wall is placed illegally.

    Parameters
    ----------
    message : str, optional
        The error message to display. Defaults to "Illegal wall placement.".
    """

    def __init__(self, message="Illegal wall placement."):
        self.message = message
        super().__init__(self.message)


class NoWallToPlaceError(Exception):
    """
    Exception raised when there are no walls left to place.

    Parameters
    ----------
    message : str, optional
        The error message to display. Defaults to "You have no walls to place".
    """

    def __init__(self, message="You have no walls to place"):
        self.message = message
        super().__init__(self.message)


class GameCompletedError(Exception):
    """
    Exception raised when a move is attempted but the game has already been completed.

    Parameters
    ----------
    message : str, optional
        The error message to display.
        Defaults to "You cant't make a move since the game is over.".
    """

    def __init__(self, message="You cant't make a move since the game is over."):
        self.message = message
        super().__init__(self.message)


class NothingToUndoError(Exception):
    """
    Exception raised when a undo action has been nothing when there is nothing to undo.

    Parameters
    ----------
    message : str, optional
        The error message to display.
        Defaults to ""There is nothing to undo"".
    """

    def __init__(self, message="There is nothing to undo"):
        self.message = message
        super().__init__(self.message)
