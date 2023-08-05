"""Module for playing quoridor
"""

import string
import re
from enum import Enum
from copy import deepcopy
from typing import Optional, Dict, List, Set, Pattern
from dataclasses import dataclass, field
from .exceptions import (
    InvalidMoveError,
    IllegalPawnMoveError,
    IllegalWallPlacementError,
    NoWallToPlaceError,
    GameCompletedError,
    NothingToUndoError,
)


ALL_QUORIDOR_MOVES_REGEX: Pattern = re.compile(r"[a-i][1-9](?:[hv])?")
START_POS_P1: str = "e1"
GOAL_P1: str = "9"
START_POS_P2: str = "e9"
GOAL_P2: str = "1"
START_WALLS: str = 10
POSSIBLE_WALLS: List[str] = [
    string.ascii_letters[i] + str(j) + c
    for i in range(8)
    for j in range(1, 9)
    for c in ["h", "v"]
]


@dataclass
class Player:
    """
    Represents a player in the Quoridor game.

    Attributes
    ----------
    id : int
        The player's ID.
    pos : str
        The player's current position on the board.
    goal : str
        The player's goal on the board.
    walls : int, optional
        The number of walls the player has, by default `START_WALLS`.
    position_history : list of str, optional
        A list of postions the player has been ordered by turn, by default `[]`
    placed_walls : list of str, optional
        A list of walls the player has placed, by default `[]`.
    """

    id: int
    pos: str
    goal: str
    walls: int = START_WALLS
    position_history: List[str] = field(default_factory=lambda: [])
    placed_walls: List[str] = field(default_factory=lambda: [])


class GameStatus(Enum):
    """
    Represents the possible statuses of a Quoridor game.
    """

    COMPLETED: str = "Completed"
    CANCELLED: str = "Canceled"
    ONGOING: str = "Ongoing"


@dataclass
class GameResult:
    """
    Represents the result of a Quoridor game.

    Attributes
    ----------
    status : str
        The status of the game.
    total_moves : int
        The total number of moves played.
    placed_walls : list of str
        A list of walls placed in the game.
    pgn : str
        The Portable Game Notation (PGN) of the game.
    winner : Player, optional
        The winning player, by default `None`.
    loser : Player, optional
        The losing player, by default `None`.
    """

    status: str
    total_moves: int
    placed_walls: List[str]
    pgn: str
    winner: Optional[Player] = None
    loser: Optional[Player] = None


class Quoridor:
    """
    Represents a game of Quoridor.

    Attributes
    ----------
    board : dict of str and list of str
        The game board, represented as a
        dictionary of coordinates and
        the coordinates of the adjacent cells.
    player1 : Player
        The first player.
    player2 : Player
        The second player.
    current_player : Player
        The player who is currently making a move.
    waiting_player : Player
        The player who is waiting for their turn.
    placed_walls : list of str
        A list of walls placed in the game.
    moves : list of str
        A list of moves played in the game.
    status : GameStatus
        The current status of the game.
    is_terminated : bool
        Whether or not the game is terminated.
    """

    def __init__(self) -> None:
        self.board: Dict[str, List[str]] = self._create_board()
        self.player1 = Player(
            id=1, pos=START_POS_P1, goal=GOAL_P1, position_history=[START_POS_P1]
        )
        self.player2 = Player(
            id=2, pos=START_POS_P2, goal=GOAL_P2, position_history=[START_POS_P2]
        )
        self.current_player = self.player1
        self.waiting_player = self.player2
        self.placed_walls = []
        self.moves = []
        self.status = GameStatus.ONGOING
        self.is_terminated = False

    @classmethod
    def init_from_pgn(cls, pgn: str) -> "Quoridor":
        """
        Initializes and returns a new Quoridor instance from the given PGN string.

        Parameters:
        -----------
        pgn: str
            The PGN string to be used to initialize the Quoridor instance.

        Returns:
        --------
        quoridor: Quoridor
            A new Quoridor instance initialized from the given PGN string.

        Raises:
        -------
        InvalidMoveError:
            If the given PGN string is invalid.
        """
        quoridor = cls()
        if pgn == "":
            return quoridor
        moves = pgn.split("/")
        for move in moves:
            quoridor.make_move(move)
        return quoridor

    def __repr__(self) -> str:
        return f"board: {self.board}"

    def __str__(self) -> str:
        return f"board: {self.board}"

    def reset(self) -> None:
        """
        Reset quoridor game to its initial state.

        This method reinitializes the instance by calling its `__init__` method. All
        instance variables are reset to their default values.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.__init__()

    def _create_board(self) -> Dict[str, List[str]]:
        """
        Creates and returns a dictionary representing the Quoridor board,
        with each key representing a cell and its value being a list of connected cells.

        Returns:
        --------
        board: Dict[str, List[str]]
            A dictionary representing the Quoridor board, with each key representing a
            cell and its value being a list of connected cells.
        """
        board: Dict[str, List[str]] = {}
        for i in range(9):
            for j in range(1, 10):
                connected_cells = []
                if i != 0:
                    connected_cells.append(string.ascii_letters[i - 1] + str(j))
                if i != 8:
                    connected_cells.append(string.ascii_letters[i + 1] + str(j))
                if j != 1:
                    connected_cells.append(string.ascii_letters[i] + str(j - 1))
                if j != 9:
                    connected_cells.append(string.ascii_letters[i] + str(j + 1))

                board[string.ascii_letters[i] + str(j)] = connected_cells

        return board

    def validate_move(self, move: str):
        """
        Validates the given move string and raises an InvalidMoveError if it is invalid.

        Parameters:
        -----------
        move: str
            The move string to be validated.

        Raises:
        -------
        InvalidMoveError:
            If the given move string is invalid.
        """
        if not bool(ALL_QUORIDOR_MOVES_REGEX.fullmatch(move)):
            raise InvalidMoveError()
        if len(move) == 2:
            self._validate_pawn_move(move)
        else:
            self._validate_wall_move(move)

    def make_move(self, move: str):
        """
        Makes the given move and updates the Quoridor instance accordingly.

        Parameters:
        -----------
        move: str
            The move string to be made.

        Raises:
        -------
        GameCompletedError:
            If the game has already been completed.

        InvalidMoveError:
            If the given move string is invalid.
        """

        if self.is_terminated:
            raise GameCompletedError()

        self.validate_move(move)
        self.moves.append(move)

        if len(move) == 2:
            self._make_pawn_move(move)
            if self.current_player.pos[1] == self.current_player.goal:
                self.is_terminated = True
                self.status = GameStatus.COMPLETED
                return
        else:
            self._make_wall_move(self.board, move)
        self._switch_player()

    def get_pgn(self) -> str:
        """
        Returns the PGN string representation of the moves made in the Quoridor game.

        Returns:
        --------
        pgn: str
            The PGN string representation of the moves made in the Quoridor game.
        """
        return "/".join(self.moves)

    def undo_move(self):
        """
        Undo the last move played in the game.

        If the game is in its initial state, i.e., no moves have been played yet,
        this function raises a `NothingToUndoError` exception.

        Returns
        -------
        None

        Raises
        ------
        NothingToUndoError
            If there are no moves to undo.
        """
        if len(self.moves) == 0:
            raise NothingToUndoError()
        last_move = self.moves.pop()
        if len(last_move) == 2:
            self.waiting_player.pos = self.waiting_player.position_history.pop()
        else:
            wall = self.placed_walls.pop()
            self.waiting_player.placed_walls.pop()
            cell = wall[:2]
            if wall[2] == "h":
                # e3h verwijderd verbinding tussen e3-e4 en f3-f4
                connected_cells = [
                    (cell, cell[0] + chr(ord(cell[1]) + 1)),
                    (
                        chr(ord(cell[0]) + 1) + cell[1],
                        chr(ord(cell[0]) + 1) + chr(ord(cell[1]) + 1),
                    ),
                ]
            else:
                # g6v verwijderd verbinding tussen g6-h6 en g7-h7
                connected_cells = [
                    (cell, chr(ord(cell[0]) + 1) + cell[1]),
                    (
                        cell[0] + chr(ord(cell[1]) + 1),
                        chr(ord(cell[0]) + 1) + chr(ord(cell[1]) + 1),
                    ),
                ]
            for cell_pair in connected_cells:
                # remove cell connections
                self.board[cell_pair[1]].append(cell_pair[0])
                self.board[cell_pair[0]].append(cell_pair[1])

        self._switch_player()

    def play_terminal(self) -> GameResult:
        """
        Starts the game and prompts the users to input their moves through the terminal.

        Returns:
        -------
        GameResult
            A named tuple that contains the outcome of the game and its associated
            metadata, including:
            * status: The status of the game at the end of play.
            * total_moves: The total number of moves made during the game.
            * placed_walls: The number of walls placed during the game.
            * winner: The player who won the game.
            * loser: The player who lost the game.
            * pgn: The Portable Game Notation representation of the game's moves.
        """
        while not self.is_terminated:
            print(f"current player: {self.current_player}")
            print(f"waiting player: {self.waiting_player}")
            print(f"legal_moves {self.get_legal_moves()}")
            command = input("Your move: ")
            if command == "q":
                self.status = GameStatus.CANCELLED
                return GameResult(
                    status=self.status,
                    total_moves=len(self.moves),
                    placed_walls=self.placed_walls,
                    pgn=self.get_pgn(),
                )
            if command == "undo":
                self.undo_move()
            else:
                self.make_move(command)

        return GameResult(
            status=self.status,
            total_moves=len(self.moves),
            placed_walls=self.placed_walls,
            winner=self.current_player,
            loser=self.waiting_player,
            pgn=self.get_pgn(),
        )

    def print_pretty_board(self):
        """Print the board in a pretty way"""
        pass

    def _switch_player(self) -> None:
        """
        Swaps the current player and waiting player.
        """
        waiting = self.current_player
        self.current_player = self.waiting_player
        self.waiting_player = waiting

    def _validate_pawn_move(self, move):
        """
        Validates if the specified pawn move is legal.

        Parameters:
        ----------
        move : str
            The move to be validated.

        Raises:
        -------
        IllegalPawnMoveError
            If the move is not legal.
        """
        if move not in self.get_legal_pawn_moves():
            raise IllegalPawnMoveError()

    def _validate_wall_move(self, move):
        """
        Validates if the specified wall move is legal.

        Parameters:
        ----------
        move : str
            The move to be validated.

        Raises:
        -------
        NoWallToPlaceError
            If the current player has no walls to place.
        IllegalWallPlacementError
            If the move is not legal, e.g. if the wall is out of bounds,
            overlaps with another wall, or
            blocks one of the players from reaching their goal.
        """
        if self.current_player.walls == 0:
            raise NoWallToPlaceError()
        if self._wall_out_of_bounds(move):
            raise IllegalWallPlacementError(
                message="Illegal wall placement, wall out of bounds"
            )
        if self._wall_overlaps(move):
            raise IllegalWallPlacementError(
                message="Illegal wall placements, wall overlaps with another wall"
            )

        # check reachability for both players
        copy_board = deepcopy(self.board)
        self._remove_connections(copy_board, move)

        if not self._is_reachable(
            copy_board, self.current_player.pos, self.current_player.goal
        ):
            raise IllegalWallPlacementError(
                message="Illegal wall placement, you cannot reach your goal"
            )
        if not self._is_reachable(
            copy_board, self.waiting_player.pos, self.waiting_player.goal
        ):
            raise IllegalWallPlacementError(
                message="Illegal wall placement, opponent cannot reach goal"
            )

    def _is_reachable(self, board, player_pos, player_goal) -> bool:
        """
        Determines if the player can reach their goal from their
        current position on the board.

        Parameters:
        ----------
        board : dict
            A dictionary representing the board's configuration.
        player_pos : str
            A string representing the player's position on the board.
        player_goal : int
            The row number of the player's goal.

        Returns:
        -------
        bool
            True if the player can reach their goal, False otherwise.
        """

        return self._dfs(set(), board, player_pos, player_goal)

    def _dfs(self, visited, graph, node, goal):
        """
        Recursive function to perform depth-first search on the board graph.

        Parameters:
        ----------
        visited : set
            A set of visited nodes.
        graph : dict
            A dictionary representing the board's configuration.
        node : str
            The current node being visited.
        goal : int
            The row number of the player's goal.

        Returns:
        -------
        bool
            True if a path to the goal exists, False otherwise.
        """
        if node not in visited:
            visited.add(node)
            for neighbour in graph[node]:
                if neighbour[1] == goal:
                    return True
                if self._dfs(visited, graph, neighbour, goal):
                    return True
        return False

    def _make_pawn_move(self, move: str):
        """
        Makes a move for the current player by moving their pawn to
        the specified position on the board.

        Parameters:
        ----------
        move : str
            A string representing the new position of the player's pawn on the board.
        """
        self.current_player.pos = move

    def get_legal_pawn_moves(self) -> Set[str]:
        """
        Get the legal moves for the current player's pawn.

        Returns
        -------
        set of str
            The set of legal moves for the current player's pawn.
        """

        # make a temporary copy of the list
        legal_pawn_moves = self.board[self.current_player.pos][:]

        # check if the other player is in range of current player for jumping moves
        if self.waiting_player.pos in legal_pawn_moves:
            legal_pawn_moves.remove(self.waiting_player.pos)
            # same row
            if self.current_player.pos[1] == self.waiting_player.pos[1]:
                if self.current_player.pos[0] > self.waiting_player.pos[0]:
                    pos_behind = (
                        chr(ord(self.current_player.pos[0]) - 2)
                        + self.current_player.pos[1]
                    )
                else:
                    pos_behind = (
                        chr(ord(self.current_player.pos[0]) + 2)
                        + self.current_player.pos[1]
                    )

            elif (
                self.current_player.pos[0] == self.waiting_player.pos[0]
            ):  # same column
                if self.current_player.pos[1] > self.waiting_player.pos[1]:
                    pos_behind = self.current_player.pos[0] + chr(
                        ord(self.current_player.pos[1]) - 2
                    )
                else:
                    pos_behind = self.current_player.pos[0] + chr(
                        ord(self.current_player.pos[1]) + 2
                    )
            if pos_behind in self.board[self.waiting_player.pos]:
                legal_pawn_moves.append(pos_behind)
            else:
                legal_pawn_moves.extend(
                    pos
                    for pos in self.board[self.waiting_player.pos]
                    if pos != self.current_player.pos
                )

        return set(legal_pawn_moves)

    def get_legal_wall_moves(self) -> List[str]:
        """
        Get the legal wall moves for the current player.

        Returns
        -------
        list of str
            The list of legal wall moves for the current player.
        """
        legal_walls = []
        if self.current_player.walls == 0:
            return legal_walls
        for wall in POSSIBLE_WALLS:
            if wall in self.placed_walls:
                continue
            try:
                self.validate_move(wall)
            except Exception:
                continue
            legal_walls.append(wall)
        return legal_walls

    def get_legal_moves(self) -> List[str]:
        """
        Get the legal moves for the current player.

        Returns
        -------
        list of str
            The list of legal moves for the current player.
        """
        return list(self.get_legal_pawn_moves()) + self.get_legal_wall_moves()

    def _wall_overlaps(self, wall: str) -> bool:
        """
        Check if the given wall overlaps with a previously placed wall.

        Parameters
        ----------
        wall : str
            The wall to check for overlaps.

        Returns
        -------
        bool
            True if the wall overlaps with a previously placed wall, False otherwise.
        """

        if wall in self.placed_walls:
            return True

        overlapping_walls = []

        if wall[2] == "h":
            overlapping_walls.append(chr(ord(wall[0]) - 1) + wall[1:])
            overlapping_walls.append(chr(ord(wall[0]) + 1) + wall[1:])
            overlapping_walls.append(wall[:2] + "v")
        elif wall[2] == "v":
            overlapping_walls.append(wall[0] + chr(ord(wall[1]) - 1) + wall[2])
            overlapping_walls.append(wall[0] + chr(ord(wall[1]) + 1) + wall[2])
            overlapping_walls.append(wall[:2] + "h")

        for overlapping_wall in overlapping_walls:
            if overlapping_wall in self.placed_walls:
                return True
        return False

    def _wall_out_of_bounds(self, wall) -> bool:
        """
        Check if the given wall is out of bounds.

        Parameters
        ----------
        wall : str
            The wall to check.

        Returns
        -------
        bool
            True if the wall is out of bounds, False otherwise.
        """
        return wall[0] < "a" or wall[0] > "h" or wall[1] < "1" or wall[1] > "8"

    def _remove_connections(self, board: Dict[str, List[str]], wall: str):
        """
        Remove the connections between the cells affected by the given wall.

        Parameters
        ----------
        board : dict of {str: list of str}
            The board to remove the connections from.
        wall : str
            The wall to remove the connections for.
        """
        # remove connections
        cell = wall[:2]
        if wall[2] == "h":
            # e3h verwijderd verbinding tussen e3-e4 en f3-f4
            connected_cells = [
                (cell, cell[0] + chr(ord(cell[1]) + 1)),
                (
                    chr(ord(cell[0]) + 1) + cell[1],
                    chr(ord(cell[0]) + 1) + chr(ord(cell[1]) + 1),
                ),
            ]
        else:
            # g6v verwijderd verbinding tussen g6-h6 en g7-h7
            connected_cells = [
                (cell, chr(ord(cell[0]) + 1) + cell[1]),
                (
                    cell[0] + chr(ord(cell[1]) + 1),
                    chr(ord(cell[0]) + 1) + chr(ord(cell[1]) + 1),
                ),
            ]
        for cell_pair in connected_cells:
            # remove cell connections
            if cell_pair[0] in board[cell_pair[1]]:
                board[cell_pair[1]].remove(cell_pair[0])
            if cell_pair[1] in self.board[cell_pair[0]]:
                board[cell_pair[0]].remove(cell_pair[1])

    def _make_wall_move(self, board: Dict[str, List[str]], wall: str):
        """
        Make a wall move for the current player.

        Parameters
        ----------
        board : dict of {str: list of str}
            The board to make the move on.
        wall : str
            The wall to place on the board.
        """
        self.placed_walls.append(wall)
        self.current_player.placed_walls.append(wall)
        self.current_player.walls -= 1

        self._remove_connections(board, wall)
