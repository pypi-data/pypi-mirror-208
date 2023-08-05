from quoridor import Quoridor
from quoridor.src.exceptions import *
import pytest


def test_get_pgn():
    # create a Quoridor instance and make some moves
    q = Quoridor()
    q.make_move("e2")
    q.make_move("e8")
    q.make_move("e3")

    # get the PGN string representation
    pgn = q.get_pgn()

    # check that the PGN string is correct
    expected_pgn = "e2/e8/e3"
    assert pgn == expected_pgn


def test_init_from_pgn():
    # create a Quoridor instance with some initial moves
    q = Quoridor()
    q.make_move("e2")
    q.make_move("e8")

    # convert the current game to PGN format
    pgn = q.get_pgn()

    # initialize a new Quoridor instance from the PGN string
    q2 = Quoridor.init_from_pgn(pgn)

    # check that the new instance has the same state as the original one
    assert q2.get_pgn() == pgn

    # try initializing with an invalid PGN string
    with pytest.raises(InvalidMoveError):
        Quoridor.init_from_pgn("e2/invalid_move")


def test_create_board():
    # create a Quoridor instance
    q = Quoridor()

    # get the board dictionary
    board = q._create_board()

    # check that all cells have the expected number of connections
    for cell in board:
        connections = board[cell]
        expected_connections = 4
        if cell[0] in ("a", "i") or cell[1] in ("1", "9"):
            expected_connections = 3
        if cell[0] in ("a", "i") and cell[1] in ("1", "9"):
            expected_connections = 2

        assert len(connections) == expected_connections

    # check that adjacent cells are connected to each other
    assert "a1" in board["b1"]
    assert "b1" in board["a1"]
    assert "i9" in board["h9"]
    assert "h9" in board["i9"]
    assert "e5" in board["d5"]
    assert "d5" in board["e5"]
    assert "e5" in board["e4"]
    assert "e4" in board["e5"]


def test_get_legal_pawn_moves():
    # create a Quoridor instance from pgn with normal circumstances
    q = Quoridor.init_from_pgn("e2/e8/e3")

    # get the legal moves for the current player's pawn
    legal_moves = q.get_legal_pawn_moves()

    # check that the legal moves are correct
    expected_moves = {"e9", "e7", "d8", "f8"}
    assert legal_moves == expected_moves

    # check legal moves for in the situation when there is a
    # jump posibble in normal circumstances so not on edge of board or wall

    q = Quoridor.init_from_pgn("e2/e8/e3/e7/e4/e6/e5")
    legal_moves = q.get_legal_pawn_moves()
    expected_moves = {"e4", "e7", "d6", "f6"}
    assert legal_moves == expected_moves

    # check legal moves for in the situation when there is a wall behind or next to the player
    q = Quoridor.init_from_pgn("e8h")
    legal_moves = q.get_legal_pawn_moves()
    expected_moves = {"f9", "d9"}
    assert legal_moves == expected_moves

    # check for legal moves when player can jump over player but wall is behind it
    q = Quoridor.init_from_pgn("e2/e8/e3/e7/e4/e6/e5/e6h")
    legal_moves = q.get_legal_pawn_moves()
    expected_moves = {"d6", "f6", "d5", "f5", "e4"}
    assert legal_moves == expected_moves


def test_validate_wall_move():
    q = Quoridor()
    q.current_player.walls = 0

    with pytest.raises(NoWallToPlaceError):
        q._validate_wall_move("a2h")

    # Test if the function raises IllegalWallPlacementError if the wall is out of bounds
    q.current_player.walls = 10
    with pytest.raises(IllegalWallPlacementError):
        q._validate_wall_move("a9h")

    # # Test if the function raises IllegalWallPlacementError if the wall overlaps with another wall
    q.placed_walls.append("g6h")
    with pytest.raises(IllegalWallPlacementError):
        invalid_pgn = "e2/e8/a5h/c5h/e5h/g5h/h6v/h7h"
        q = Quoridor.init_from_pgn("g6h/g6v")

    # Test if the function raises IllegalWallPlacementError if the wall blocks the current player from reaching their goal
    with pytest.raises(IllegalWallPlacementError):
        invalid_pgn = "e2/e8/a5h/c5h/e5h/g5h/h6v/h7h"
        q = Quoridor.init_from_pgn(invalid_pgn)

    # Test if the function raises IllegalWallPlacementError if the wall blocks the opponent from reaching their goal
    with pytest.raises(IllegalWallPlacementError):
        invalid_pgn = "e2/e8/a5h/c5h/e5h/g5h/h6v/h7h"
        q = Quoridor.init_from_pgn(invalid_pgn)

    # Test if the function returns None if the wall move is legal
    q = Quoridor()
    assert q._validate_wall_move("a2h") == None


def test_undo_move():
    game = Quoridor()

    # Test when there is nothing to undo
    initial_state = game.__dict__
    with pytest.raises(NothingToUndoError):
        game.undo_move()

    # test undoing pawn move
    game.make_move("e2")
    game.undo_move()
    assert initial_state == game.__dict__

    # test undoing wall move
    game.make_move("e3h")
    game.undo_move()
    assert initial_state == game.__dict__


def test_make_move_when_game_completed():
    # create a Quoridor instance and complete the game
    q = Quoridor()
    q.player1.pos = "e8"
    q.player2.pos = "e2"
    q.make_move("e9")
    assert q.is_terminated == True

    # try to make a move after the game is completed
    with pytest.raises(GameCompletedError):
        q.make_move("e1")
