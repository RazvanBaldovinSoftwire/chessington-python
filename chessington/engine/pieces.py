from __future__ import annotations
from abc import ABC, abstractmethod
from chessington.engine.data import Player, Square
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
	from chessington.engine.board import Board

BOARD_SIZE = 8
BLACK_PAWN_ROW = 6
WHITE_PAWN_ROW = 1
SHORT_CASTLE_ROOK_COL = 7
LONG_CASTLE_ROOK_COL = 0

last_piece_moved = None
last_moved_from = None
last_moved_to = None

def set_last_move(piece: Piece, moved_from: Square, moved_to: Square):
	global last_piece_moved, last_moved_from, last_moved_to
	last_piece_moved = piece
	last_moved_from = moved_from
	last_moved_to = moved_to

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
		current_piece = board.get_piece(current_square)

		piece_attacked = board.get_piece(new_square)
		if piece_attacked is None or type(piece_attacked) is not King:
			board.move_piece(current_square, new_square)
			set_last_move(current_piece, current_square, new_square)
		else:
			print("No one can capture the king!")
			return

		if current_piece is not None:
			if type(current_piece) is King:
				current_piece.moved = True
			elif type(current_piece) is Rook:
				current_piece.moved = True

		# Check if castle and finish the move
		if type(current_piece) is King and abs(current_square.col - new_square.col) == 2:
			# Short castle
			if current_square.col - new_square.col < 0:
				rook_current_square = Square.at(current_square.row, SHORT_CASTLE_ROOK_COL)
				rook_new_square = Square.at(current_square.row, SHORT_CASTLE_ROOK_COL - 2)
			else:
				rook_current_square = Square.at(current_square.row, LONG_CASTLE_ROOK_COL)
				rook_new_square = Square.at(current_square.row, LONG_CASTLE_ROOK_COL + 3)

			# Since our interface doesn't allow us to move two pieces of the same color at the same time, we create a
			# new rook on the castled position
			board.set_piece(rook_new_square, Rook(self.player))
			board.set_piece(rook_current_square, None)

		# Check if pawn did an en passant
		if type(current_piece) is Pawn and piece_attacked is None and current_square.col != new_square.col:
			if self.player == Player.WHITE:
				captured_pawn_square = Square.at(new_square.row - 1, new_square.col)
			else:
				captured_pawn_square = Square.at(new_square.row + 1, new_square.col)

			board.set_piece(captured_pawn_square, None)

	def is_position_on_board(self, new_square: Square) -> bool:
		return 0 <= new_square.row < BOARD_SIZE and 0 <= new_square.col < BOARD_SIZE

	def is_attacked(self, board, square: Square, color) -> bool:
		for i in range(0, BOARD_SIZE):
			for j in range(0, BOARD_SIZE):
				piece = board.get_piece(Square.at(i, j))

				if piece is not None and piece.player != color:
					if square in piece.get_available_moves(board):
						return True

		return False


class Pawn(Piece):
	"""
    A class representing a chess pawn.
    """

	def check_square_in_front(self, board, square: Square) -> bool:
		return self.is_position_on_board(square) and board.get_piece(square) is None

	def check_two_squares_in_front(self, board, row, square_in_front: Square, two_squares_in_front: Square) -> bool:
		if self.player == Player.BLACK:
			return (row == BLACK_PAWN_ROW and board.get_piece(square_in_front) is None
					and board.get_piece(two_squares_in_front) is None)
		else:
			return (row == WHITE_PAWN_ROW and board.get_piece(square_in_front) is None
					and board.get_piece(two_squares_in_front) is None)

	def check_attack(self, board, square: Square) -> bool:
		if self.is_position_on_board(square):
			piece_attacked = board.get_piece(square)

			if self.player == Player.BLACK:
				return piece_attacked is not None and piece_attacked.player is Player.WHITE
			else:
				return piece_attacked is not None and piece_attacked.player is Player.BLACK

		return False

	def check_en_passant(self, board, square: Square) -> bool:
		if last_piece_moved is None or type(last_piece_moved) is not Pawn:
			return False

		if last_moved_to is None or last_moved_from is None:
			return False

		if abs(last_moved_from.row - last_moved_to.row) == 1:
			return False

		if abs(last_moved_to.col - board.find_piece(self).col) != 1:
			return False

		if self.player == Player.WHITE:
			piece_attacked = board.get_piece(Square.at(square.row - 1, square.col))
		else:
			piece_attacked = board.get_piece(Square.at(square.row + 1, square.col))

		if piece_attacked is None or piece_attacked.player is self.player:
			return False

		return True

	def get_available_moves(self, board) -> List[Square]:
		current_square = board.find_piece(self)
		available_moves = []
		direction = 1 if self.player == Player.WHITE else -1

		square_in_front = Square.at(current_square.row + 1 * direction, current_square.col)
		two_squares_in_front = Square.at(current_square.row + 2 * direction, current_square.col)
		attack_left = Square.at(current_square.row + 1 * direction, current_square.col - 1)
		attack_right = Square.at(current_square.row + 1 * direction, current_square.col + 1)

		if self.check_square_in_front(board, square_in_front):
			available_moves.append(square_in_front)
		if self.check_two_squares_in_front(board, current_square.row, square_in_front, two_squares_in_front):
			available_moves.append(two_squares_in_front)
		if self.check_attack(board, attack_left) or self.check_en_passant(board, attack_left):
			available_moves.append(attack_left)
		if self.check_attack(board, attack_right) or self.check_en_passant(board, attack_right):
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
			for distance in range(1, BOARD_SIZE):
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
	moved = False

	def get_available_moves(self, board):
		current_square = board.find_piece(self)
		available_moves = []

		dx = [-1, 0, 1, 0]
		dy = [0, -1, 0, 1]

		for i in range(len(dx)):
			for distance in range(1, BOARD_SIZE):
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
		current_square = board.find_piece(self)
		available_moves = []

		# Mix of bishop and rook
		dx = [-1, 0, 1, 0, -1, -1, 1, 1]
		dy = [0, -1, 0, 1, -1, 1, -1, 1]

		for i in range(len(dx)):
			for distance in range(1, BOARD_SIZE):
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


class King(Piece):
	"""
    A class representing a chess king.
    """
	moved = False

	def check_castle(self, board, rook_col):
		current_square = board.find_piece(self)
		rook = board.get_piece(Square.at(current_square.row, rook_col))

		if rook is None or type(rook) is not Rook:
			return False

		if self.moved is True or rook.moved is True or self.player is not rook.player:
			return False

		direction = 1 if rook_col == SHORT_CASTLE_ROOK_COL else -1

		if (board.get_piece(Square.at(current_square.row, current_square.col + 1 * direction)) is not None
				or board.get_piece(Square.at(current_square.row, current_square.col + 2 * direction)) is not None):
			return False

		# Long castle has 3 pieces in between, not 2
		if rook_col == 0 and board.get_piece(Square.at(current_square.row, rook_col + 1)) is not None:
			return False

		for i in range(0, 3):
			if self.is_attacked(board, Square.at(current_square.row, current_square.col + i * direction), self.player):
				return False

		return True

	def get_available_moves(self, board):
		current_square = board.find_piece(self)
		available_moves = []

		# Mix of bishop and rook
		dx = [-1, 0, 1, 0, -1, -1, 1, 1]
		dy = [0, -1, 0, 1, -1, 1, -1, 1]

		for i in range(len(dx)):
			next_square = Square(current_square.row + dx[i], current_square.col + dy[i])

			if self.is_position_on_board(next_square):
				piece_attacked = board.get_piece(next_square)
				if piece_attacked is not None:
					if self.player != piece_attacked.player:
						available_moves.append(next_square)
				# If there is no piece on the next square
				else:
					available_moves.append(next_square)

		# Check short castle
		if self.check_castle(board, SHORT_CASTLE_ROOK_COL):
			available_moves.append(Square.at(current_square.row, current_square.col + 2))

		# Check long castle
		if self.check_castle(board, LONG_CASTLE_ROOK_COL):
			available_moves.append(Square.at(current_square.row, current_square.col - 2))

		return available_moves
