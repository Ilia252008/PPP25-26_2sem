# -*- coding: utf-8 -*-
"""
Шахматный симулятор — ООП версия
Допы:
- 3 новые фигуры (3 балла)
- Откат ходов (1 балл)
- Подсказка ходов (1 балл)
- Взятие на проходе + превращение пешки (1 балл)
Итого: 6 баллов
"""

import copy

# --------------------------------------------------------------
# Базовый класс фигуры
# --------------------------------------------------------------
class Piece:
    def __init__(self, color, row, col):
        self.color = color      # 'white' или 'black'
        self.row = row
        self.col = col
        self.symbol = '?'       # переопределяется в наследниках

    def __repr__(self):
        return self.symbol

    def get_possible_moves(self, board):
        """Возвращает список (row, col) возможных ходов (без проверки шаха)."""
        return []

    def move_to(self, row, col):
        self.row = row
        self.col = col


# --------------------------------------------------------------
# Стандартные фигуры
# --------------------------------------------------------------
class King(Piece):
    def __init__(self, color, row, col):
        super().__init__(color, row, col)
        self.symbol = 'K' if color == 'white' else 'k'

    def get_possible_moves(self, board):
        moves = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = self.row + dr, self.col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = board.grid[r][c]
                    if target is None or target.color != self.color:
                        moves.append((r, c))
        return moves


class Queen(Piece):
    def __init__(self, color, row, col):
        super().__init__(color, row, col)
        self.symbol = 'Q' if color == 'white' else 'q'

    def get_possible_moves(self, board):
        moves = []
        dirs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
        for dr, dc in dirs:
            r, c = self.row + dr, self.col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board.grid[r][c]
                if target is None:
                    moves.append((r, c))
                else:
                    if target.color != self.color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc
        return moves


class Rook(Piece):
    def __init__(self, color, row, col):
        super().__init__(color, row, col)
        self.symbol = 'R' if color == 'white' else 'r'

    def get_possible_moves(self, board):
        moves = []
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        for dr, dc in dirs:
            r, c = self.row + dr, self.col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board.grid[r][c]
                if target is None:
                    moves.append((r, c))
                else:
                    if target.color != self.color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc
        return moves


class Bishop(Piece):
    def __init__(self, color, row, col):
        super().__init__(color, row, col)
        self.symbol = 'B' if color == 'white' else 'b'

    def get_possible_moves(self, board):
        moves = []
        dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]
        for dr, dc in dirs:
            r, c = self.row + dr, self.col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board.grid[r][c]
                if target is None:
                    moves.append((r, c))
                else:
                    if target.color != self.color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc
        return moves


class Knight(Piece):
    def __init__(self, color, row, col):
        super().__init__(color, row, col)
        self.symbol = 'N' if color == 'white' else 'n'

    def get_possible_moves(self, board):
        moves = []
        jumps = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
        for dr, dc in jumps:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = board.grid[r][c]
                if target is None or target.color != self.color:
                    moves.append((r, c))
        return moves


class Pawn(Piece):
    def __init__(self, color, row, col):
        super().__init__(color, row, col)
        self.symbol = 'P' if color == 'white' else 'p'
        self.direction = -1 if color == 'white' else 1   # белые вверх (уменьшение row)

    def get_possible_moves(self, board):
        moves = []
        forward = self.row + self.direction
        # одна клетка вперёд
        if 0 <= forward < 8 and board.grid[forward][self.col] is None:
            moves.append((forward, self.col))
            # две клетки из начальной позиции
            if (self.color == 'white' and self.row == 6) or (self.color == 'black' and self.row == 1):
                forward2 = self.row + 2 * self.direction
                if board.grid[forward2][self.col] is None:
                    moves.append((forward2, self.col))

        # взятие по диагонали
        for dc in (-1, 1):
            r, c = forward, self.col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = board.grid[r][c]
                if target and target.color != self.color:
                    moves.append((r, c))

        # взятие на проходе (en passant)
        if board.en_passant_target is not None:
            ep_row, ep_col = board.en_passant_target
            # пешка может взять на проходе, если стоит на нужной горизонтали
            if self.color == 'white' and self.row == 3 and abs(self.col - ep_col) == 1 and ep_row == 2:
                moves.append((ep_row, ep_col))
            elif self.color == 'black' and self.row == 4 and abs(self.col - ep_col) == 1 and ep_row == 5:
                moves.append((ep_row, ep_col))

        return moves


# --------------------------------------------------------------
# НОВЫЕ ФИГУРЫ (3 балла)
# --------------------------------------------------------------
class Guardian(Piece):
    """Страж: ходит как король, но на 2 клетки (включая диагонали)."""
    def __init__(self, color, row, col):
        super().__init__(color, row, col)
        self.symbol = 'G' if color == 'white' else 'g'

    def get_possible_moves(self, board):
        moves = []
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                if dr == 0 and dc == 0:
                    continue
                if abs(dr) <= 2 and abs(dc) <= 2:
                    r, c = self.row + dr, self.col + dc
                    if 0 <= r < 8 and 0 <= c < 8:
                        target = board.grid[r][c]
                        if target is None or target.color != self.color:
                            moves.append((r, c))
        return moves


class Archer(Piece):
    """Лучник: ходит как слон, но не дальше 3 клеток."""
    def __init__(self, color, row, col):
        super().__init__(color, row, col)
        self.symbol = 'A' if color == 'white' else 'a'

    def get_possible_moves(self, board):
        moves = []
        dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]
        for dr, dc in dirs:
            for step in range(1, 4):
                r, c = self.row + dr*step, self.col + dc*step
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                target = board.grid[r][c]
                if target is None:
                    moves.append((r, c))
                else:
                    if target.color != self.color:
                        moves.append((r, c))
                    break
        return moves


class Mage(Piece):
    """Маг: телепорт на любую пустую клетку того же цвета (чёрная/белая)."""
    def __init__(self, color, row, col):
        super().__init__(color, row, col)
        self.symbol = 'M' if color == 'white' else 'm'

    def get_possible_moves(self, board):
        moves = []
        target_color = (self.row + self.col) % 2   # 0 - чёрная, 1 - белая
        for r in range(8):
            for c in range(8):
                if (r + c) % 2 == target_color and (r, c) != (self.row, self.col):
                    if board.grid[r][c] is None:
                        moves.append((r, c))
        return moves


# --------------------------------------------------------------
# Класс доски
# --------------------------------------------------------------
class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.current_turn = 'white'
        self.en_passant_target = None   # клетка, куда можно взять на проходе (row, col)
        self.setup()

    def setup(self):
        """Начальная расстановка с новыми фигурами вместо некоторых."""
        # Белые: ладья, страж, лучник, ферзь, король, лучник, конь, ладья
        white_spec = [Rook, Guardian, Archer, Queen, King, Archer, Knight, Rook]
        black_spec = [Rook, Guardian, Archer, Queen, King, Archer, Knight, Rook]

        for col, piece_class in enumerate(white_spec):
            self.grid[7][col] = piece_class('white', 7, col)
        for col, piece_class in enumerate(black_spec):
            self.grid[0][col] = piece_class('black', 0, col)

        # пешки
        for col in range(8):
            self.grid[6][col] = Pawn('white', 6, col)
            self.grid[1][col] = Pawn('black', 1, col)

    def display(self, highlight_moves=None):
        """Печатает доску. Если highlight_moves не пуст, подсвечивает клетки."""
        print("  a b c d e f g h")
        for r in range(8):
            print(8 - r, end=" ")
            for c in range(8):
                piece = self.grid[r][c]
                symbol = str(piece) if piece else '.'
                if highlight_moves and (r, c) in highlight_moves:
                    print(f"[{symbol}]", end="")
                else:
                    print(f" {symbol} ", end="")
            print(" ", 8 - r)
        print("  a b c d e f g h\n")

    def get_piece_at(self, row, col):
        return self.grid[row][col]

    def move_piece(self, start, end):
        """Перемещает фигуру без проверок, возвращает взятую фигуру и флаг двойного хода пешки."""
        sr, sc = start
        er, ec = end
        piece = self.grid[sr][sc]
        if piece is None:
            return None, False
        captured = self.grid[er][ec]
        self.grid[er][ec] = piece
        self.grid[sr][sc] = None
        piece.move_to(er, ec)

        # Проверка на двойной ход пешки (для en passant)
        double_step = False
        if isinstance(piece, Pawn) and abs(er - sr) == 2:
            double_step = True

        return captured, double_step

    def undo_move(self, start, end, captured, was_double_step, old_en_passant):
        """Откатывает перемещение, восстанавливая en_passant_target."""
        sr, sc = start
        er, ec = end
        piece = self.grid[er][ec]
        self.grid[sr][sc] = piece
        self.grid[er][ec] = captured
        if piece:
            piece.move_to(sr, sc)
        self.en_passant_target = old_en_passant

    def is_in_check(self, color):
        """Проверяет, находится ли король цвета color под шахом."""
        # найдём короля
        king_pos = None
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p and p.color == color and isinstance(p, King):
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        if not king_pos:
            return False
        # смотрим, может ли фигура противника пойти на короля
        opponent = 'black' if color == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p and p.color == opponent:
                    moves = p.get_possible_moves(self)
                    if king_pos in moves:
                        return True
        return False

    def is_legal_move(self, start, end, color):
        """Проверяет легальность хода (с учётом шаха и en passant)."""
        sr, sc = start
        er, ec = end
        piece = self.grid[sr][sc]
        if piece is None or piece.color != color:
            return False

        # особый случай: взятие на проходе
        # если ход ведёт на en_passant_target и там нет фигуры, но пешка может взять
        if self.en_passant_target == (er, ec) and isinstance(piece, Pawn):
            # нужно проверить, что сбоку есть пешка противника
            direction = -1 if color == 'white' else 1
            expected_pawn_row = er - direction
            if abs(ec - sc) == 1 and expected_pawn_row == sr:
                # пробный ход: удаляем пешку противника вручную
                captured_pawn = self.grid[expected_pawn_row][ec]
                if captured_pawn and isinstance(captured_pawn, Pawn) and captured_pawn.color != color:
                    # сохраняем состояние
                    old_grid = copy.deepcopy(self.grid)
                    old_en_passant = self.en_passant_target
                    # выполняем ход
                    self.grid[er][ec] = piece
                    self.grid[sr][sc] = None
                    self.grid[expected_pawn_row][ec] = None
                    piece.move_to(er, ec)
                    in_check = self.is_in_check(color)
                    # откатываем
                    self.grid = old_grid
                    self.en_passant_target = old_en_passant
                    piece.move_to(sr, sc)
                    return not in_check

        # обычная проверка
        possible = piece.get_possible_moves(self)
        if (er, ec) not in possible:
            return False

        # пробный ход
        captured, double_step = self.move_piece(start, end)
        old_en_passant = self.en_passant_target
        # после хода обновляем en_passant_target (только если пешка сделала двойной шаг)
        if isinstance(piece, Pawn) and abs(er - sr) == 2:
            self.en_passant_target = ((sr + er)//2, sc)
        else:
            self.en_passant_target = None

        in_check = self.is_in_check(color)
        # откат
        self.undo_move(start, end, captured, double_step, old_en_passant)
        return not in_check

    def get_all_moves(self, color):
        """Возвращает список всех легальных ходов для цвета."""
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece and piece.color == color:
                    for er, ec in piece.get_possible_moves(self):
                        if self.is_legal_move((r, c), (er, ec), color):
                            moves.append(((r, c), (er, ec)))
        return moves

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
        return len(self.get_all_moves(color)) == 0

    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False
        return len(self.get_all_moves(color)) == 0


# --------------------------------------------------------------
# Класс игры (управление, история, подсказки, превращение пешки)
# --------------------------------------------------------------
class Game:
    def __init__(self):
        self.board = Board()
        self.history = []   # (start, end, captured, turn, was_double_step, old_en_passant)
        self.current_turn = 'white'

    def parse_coord(self, s):
        if len(s) != 2:
            return None
        col = ord(s[0]) - ord('a')
        row = 8 - int(s[1])
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None

    def coord_to_str(self, rc):
        r, c = rc
        return f"{chr(c+ord('a'))}{8-r}"

    def show_possible_moves(self, pos):
        piece = self.board.get_piece_at(pos[0], pos[1])
        if piece is None or piece.color != self.current_turn:
            print("Там нет твоей фигуры!")
            return []
        raw = piece.get_possible_moves(self.board)
        legal = []
        for end in raw:
            if self.board.is_legal_move(pos, end, self.current_turn):
                legal.append(end)
        if legal:
            print("Можно сходить на:", [self.coord_to_str(e) for e in legal])
            self.board.display(highlight_moves=legal)
        else:
            print("Нет ходов у этой фигуры.")
        return legal

    def promote_pawn(self, row, col, color):
        """Превращение пешки (вызывается, когда пешка дошла до последней горизонтали)."""
        print("Пешка дошла до конца! Во что превратить?")
        print("1 - Ферзь (Q)")
        print("2 - Ладья (R)")
        print("3 - Слон (B)")
        print("4 - Конь (N)")
        print("5 - Страж (G)")
        print("6 - Лучник (A)")
        print("7 - Маг (M)")
        choice = input("Твой выбор (1-7): ").strip()
        piece_classes = {
            '1': Queen, '2': Rook, '3': Bishop, '4': Knight,
            '5': Guardian, '6': Archer, '7': Mage
        }
        cls = piece_classes.get(choice, Queen)   # по умолчанию ферзь
        self.board.grid[row][col] = cls(color, row, col)

    def make_move(self, start_str, end_str):
        start = self.parse_coord(start_str)
        end = self.parse_coord(end_str)
        if start is None or end is None:
            print("Неверный формат, пиши типа 'e2'")
            return False

        piece = self.board.get_piece_at(start[0], start[1])
        if not piece or piece.color != self.current_turn:
            print("Не твоя фигура!")
            return False

        # особый случай: взятие на проходе
        ep_capture = False
        if self.board.en_passant_target == end and isinstance(piece, Pawn):
            ep_capture = True

        if not self.board.is_legal_move(start, end, self.current_turn):
            print("Ход недопустим (шах или правила фигуры).")
            return False

        # запоминаем состояние для отката
        old_en_passant = self.board.en_passant_target
        captured_piece = self.board.get_piece_at(end[0], end[1])

        # выполняем ход
        if ep_capture:
            # вручную убираем пешку противника
            direction = -1 if self.current_turn == 'white' else 1
            pawn_row = end[0] - direction
            captured_piece = self.board.grid[pawn_row][end[1]]
            self.board.grid[pawn_row][end[1]] = None
            # перемещаем свою пешку
            self.board.grid[end[0]][end[1]] = piece
            self.board.grid[start[0]][start[1]] = None
            piece.move_to(end[0], end[1])
            was_double = False
        else:
            captured_piece, was_double = self.board.move_piece(start, end)

        # обновляем en_passant_target
        new_en_passant = None
        if isinstance(piece, Pawn) and abs(end[0] - start[0]) == 2:
            new_en_passant = ((start[0] + end[0]) // 2, start[1])
        self.board.en_passant_target = new_en_passant

        # сохраняем в историю
        self.history.append((start, end, captured_piece, self.current_turn, was_double, old_en_passant, ep_capture))

        # превращение пешки
        if isinstance(piece, Pawn) and (end[0] == 0 or end[0] == 7):
            self.promote_pawn(end[0], end[1], self.current_turn)

        # смена хода
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        return True

    def undo(self):
        if not self.history:
            print("Нечего откатывать.")
            return
        start, end, captured, turn, was_double, old_en_passant, ep_capture = self.history.pop()
        if ep_capture:
            # откат взятия на проходе: нужно вернуть пешку противника
            piece = self.board.get_piece_at(end[0], end[1])
            self.board.grid[start[0]][start[1]] = piece
            self.board.grid[end[0]][end[1]] = None
            if piece:
                piece.move_to(start[0], start[1])
            # возвращаем взятую пешку
            direction = -1 if turn == 'white' else 1
            pawn_row = end[0] - direction
            self.board.grid[pawn_row][end[1]] = captured
        else:
            self.board.undo_move(start, end, captured, was_double, old_en_passant)
        self.board.en_passant_target = old_en_passant
        self.current_turn = turn
        print(f"Откатили ход {self.coord_to_str(start)} -> {self.coord_to_str(end)}")

    def run(self):
        print("Добро пожаловать в шахматы с новыми фигурами (Страж, Лучник, Маг)!")
        print("Команды: <клетка> <клетка>  – сделать ход")
        print("         moves <клетка>     – показать возможные ходы")
        print("         undo               – отменить последний ход")
        print("         exit               – выйти\n")

        while True:
            self.board.display()
            print(f"Ход {'белых' if self.current_turn == 'white' else 'черных'}.")

            if self.board.is_checkmate(self.current_turn):
                winner = 'черные' if self.current_turn == 'white' else 'белые'
                print(f"Мат! Победили {winner}.")
                break
            if self.board.is_stalemate(self.current_turn):
                print("Пат! Ничья.")
                break
            if self.board.is_in_check(self.current_turn):
                print("Шах!")

            cmd = input("> ").strip().lower()
            if cmd == "exit":
                break
            if cmd == "undo":
                self.undo()
                continue
            if cmd.startswith("moves "):
                parts = cmd.split()
                if len(parts) == 2:
                    pos = self.parse_coord(parts[1])
                    if pos:
                        self.show_possible_moves(pos)
                    else:
                        print("Плохая клетка.")
                else:
                    print("Пример: moves e2")
                continue
            parts = cmd.split()
            if len(parts) == 2:
                if self.make_move(parts[0], parts[1]):
                    continue
                else:
                    print("Попробуй ещё.")
            else:
                print("Не понял команду.")


if __name__ == "__main__":
    g = Game()
    g.run()
