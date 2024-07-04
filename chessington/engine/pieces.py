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

	def check_square_in_front(self, board, square: Square) -> bool:
		return self.is_position_on_board(square) and board.get_piece(square) is None

	def check_two_squares_in_front(self, board, row, square_in_front: Square, two_squares_in_front: Square) -> bool:
		if self.player == Player.BLACK:
			return (row == 6 and board.get_piece(square_in_front) is None
					and board.get_piece(two_squares_in_front) is None)
		else:
			return (row == 1 and board.get_piece(square_in_front) is None
					and board.get_piece(two_squares_in_front) is None)

	def check_attack(self, board, square: Square) -> bool:
		if self.is_position_on_board(square):
			piece_attacked = board.get_piece(square)

			if self.player == Player.BLACK:
				return piece_attacked is not None and piece_attacked.player is Player.WHITE
			else:
				return piece_attacked is not None and piece_attacked.player is Player.BLACK

		return False

	def get_available_moves(self, board) -> List[Square]:
		current_square = board.find_piece(self)
		available_moves = []

		if self.player == Player.BLACK:
			square_in_front = Square.at(current_square.row - 1, current_square.col)
			two_squares_in_front = Square.at(current_square.row - 2, current_square.col)
			attack_left = Square.at(current_square.row - 1, current_square.col - 1)
			attack_right = Square.at(current_square.row - 1, current_square.col + 1)

		else:
			square_in_front = Square.at(current_square.row + 1, current_square.col)
			two_squares_in_front = Square.at(current_square.row + 2, current_square.col)
			attack_left = Square.at(current_square.row + 1, current_square.col - 1)
			attack_right = Square.at(current_square.row + 1, current_square.col + 1)

		if self.check_square_in_front(board, square_in_front):
			available_moves.append(square_in_front)
		if self.check_two_squares_in_front(board, current_square.row, square_in_front, two_squares_in_front):
			available_moves.append(two_squares_in_front)
		if self.check_attack(board, attack_left):
			available_moves.append(attack_left)
		if self.check_attack(board, attack_right):
			available_moves.append(attack_right)

		return available_moves


class Knight(Piece):
	"""
    A class representing a chess knight.
    """

	def get_available_moves(self, board):
		current_square = board.find_piece(self)
		available_moves = []

		dx = [-2, -2, -1, -1, 1, 1, 2, 2]
		dy = [-1, 1, -2, 2, -2, 2, -1, 1]

		for i in range(len(dx)):
			next_square = Square(current_square.row + dx[i], current_square.col + dy[i])

			if self.is_position_on_board(next_square):
				piece_attacked = board.get_piece(next_square)

				if piece_attacked is not None:
					if self.player != piece_attacked.player:
						available_moves.append(next_square)
				else:
					available_moves.append(next_square)

		return available_moves


class Bishop(Piece):
	"""
    A class representing a chess bishop.
    """

	def get_available_moves(self, board):
		current_square = board.find_piece(self)
		available_moves = []

		dx = [-1, -1, 1, 1]
		dy = [-1, 1, -1, 1]

		for i in range(len(dx)):
			for distance in range(1, 7):
				next_square = Square(current_square.row + dx[i] * distance, current_square.col + dy[i] * distance)

				if self.is_position_on_board(next_square):
					piece_attacked = board.get_piece(next_square)
					if piece_attacked is not None:
						if self.player != piece_attacked.player:
							available_moves.append(next_square)

						# Whether the piece is a friendly or enemy one, the bishop cannot continue past neither
						break
					# If there is no piece on the next square
					else:
						available_moves.append(next_square)
				# If the next square is not valid (not on the board)
				else:
					break

		return available_moves


class Rook(Piece):
	"""
    A class representing a chess rook.
    """

	def get_available_moves(self, board):
		current_square = board.find_piece(self)
		available_moves = []

		dx = [-1, 0, 1, 0]
		dy = [0, -1, 0, 1]

		for i in range(len(dx)):
			for distance in range(1, 7):
				next_square = Square(current_square.row + dx[i] * distance, current_square.col + dy[i] * distance)

				if self.is_position_on_board(next_square):
					piece_attacked = board.get_piece(next_square)
					if piece_attacked is not None:
						if self.player != piece_attacked.player:
							available_moves.append(next_square)

						# Whether the piece is a friendly or enemy one, the bishop cannot continue past neither
						break
					# If there is no piece on the next square
					else:
						available_moves.append(next_square)
				# If the next square is not valid (not on the board)
				else:
					break

		return available_moves


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
