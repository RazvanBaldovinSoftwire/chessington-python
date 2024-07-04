from __future__ import annotations
from abc import ABC, abstractmethod
from chessington.engine.data import Player, Square
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
	from chessington.engine.board import Board


class Piece(ABC):
	"""
    An abstract base class from which all pieces inherit.
    """

	def __init__(self, player: Player):
		self.player = player

	@abstractmethod
	def get_available_moves(self, board: Board) -> List[Square]:
		"""
        Get all squares that the piece is allowed to move to.
        """
		pass

	def move_to(self, board, new_square):
		"""
        Move this piece to the given square on the board.
        """
		current_square = board.find_piece(self)
		board.move_piece(current_square, new_square)

	def is_position_on_board(self, new_square: Square) -> bool:
		return 0 <= new_square.row < 8 and 0 <= new_square.col < 8


class Pawn(Piece):
	"""
    A class representing a chess pawn.
    """

	def get_available_moves(self, board) -> List[Square]:
		current_square = board.find_piece(self)
		available_moves = []

		if self.player == Player.BLACK:
			square_in_front = Square.at(current_square.row - 1, current_square.col)
			if (self.is_position_on_board(square_in_front)
					and board.get_piece(square_in_front) is None):
				available_moves.append(square_in_front)

			two_squares_in_front = Square.at(current_square.row - 2, current_square.col)
			if (current_square.row == 6
					and board.get_piece(two_squares_in_front) is None
					and board.get_piece(square_in_front) is None):
				available_moves.append(two_squares_in_front)

			attack_left = Square.at(current_square.row - 1, current_square.col - 1)
			if (self.is_position_on_board(attack_left)
					and board.get_piece(attack_left) is Player.WHITE):
				available_moves.append(attack_left)

			attack_right = Square.at(current_square.row - 1, current_square.col + 1)
			if (self.is_position_on_board(attack_right)
					and board.get_piece(attack_right) is Player.WHITE):
				available_moves.append(attack_right)

		else:
			square_in_front = Square.at(current_square.row + 1, current_square.col)
			if (self.is_position_on_board(square_in_front)
					and board.get_piece(square_in_front) is None):
				available_moves.append(square_in_front)

			two_squares_in_front = Square.at(current_square.row + 2, current_square.col)
			if (current_square.row == 1
					and board.get_piece(two_squares_in_front) is None
					and board.get_piece(square_in_front) is None):
				available_moves.append(two_squares_in_front)

			attack_left = Square.at(current_square.row + 1, current_square.col - 1)
			if (self.is_position_on_board(attack_left)
					and board.get_piece(attack_left) is Player.BLACK):
				available_moves.append(attack_left)

			attack_right = Square.at(current_square.row + 1, current_square.col + 1)
			if (self.is_position_on_board(attack_right)
					and board.get_piece(attack_right) is Player.BLACK):
				available_moves.append(attack_right)

		return available_moves


class Knight(Piece):
	"""
    A class representing a chess knight.
    """

	def get_available_moves(self, board):
		return []


class Bishop(Piece):
	"""
    A class representing a chess bishop.
    """

	def get_available_moves(self, board):
		return []


class Rook(Piece):
	"""
    A class representing a chess rook.
    """

	def get_available_moves(self, board):
		return []


class Queen(Piece):
	"""
    A class representing a chess queen.
    """

	def get_available_moves(self, board):
		return []


class King(Piece):
	"""
    A class representing a chess king.
    """

	def get_available_moves(self, board):
		return []
