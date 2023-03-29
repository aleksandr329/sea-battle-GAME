import os
import random
import time
from string import ascii_uppercase as letters


BOARD_SIZE = 6
SHIP_RULES = [3, 2, 2, 1, 1, 1, 1]
EMPTY_SYMBOL = '~'
SHIP_SYMBOL = '■'
HIT_SYMBOL = 'X'
MISS_SYMBOL = '·'
SCR_WIDTH = BOARD_SIZE * 8
CLEAR_SCREEN = 'cls' if os.name == 'nt' else 'clear'
TIMEOUT = 1


def print_intro(board1, board2, with_ships=False):
    
    os.system(CLEAR_SCREEN)

    print('-' * SCR_WIDTH)
    print('Морской бой'.center(SCR_WIDTH))
    print()
    print('формат ввода ходов: «строка колонка»'.center(SCR_WIDTH))
    print('-' * SCR_WIDTH)
    print()
    print('Игрок'.center(SCR_WIDTH // 2) + 'Компьютер'.center(SCR_WIDTH // 2))
    print(f'Кораблей: {len(board1.ships)}'.center(SCR_WIDTH // 2)
        + f'Кораблей: {len(board2.ships)}'.center(SCR_WIDTH // 2))
    print()

    col_numbers1 = ' ' + '|'.join(letters[:board1.size])
    col_numbers2 = ' ' + '|'.join(letters[:board2.size])
    print(col_numbers1.center(SCR_WIDTH // 2)
        + col_numbers2.center(SCR_WIDTH // 2))

    for row_number, rows in enumerate(zip(board1.state, board2.state)):
        hidden_row = [EMPTY_SYMBOL if cell == SHIP_SYMBOL
                      else cell for cell in rows[1]]
        row1 = letters[row_number] + '|' + '|'.join(map(str, rows[0]))
        row2 = (letters[row_number] + '|' + '|'.join(map(str, rows[1]))
                if with_ships else
                letters[row_number] + '|' + '|'.join(map(str, hidden_row)))
        print(row1.center(SCR_WIDTH // 2) + row2.center(SCR_WIDTH // 2))

    print()
    print('-' * SCR_WIDTH)
    print()


class Board:
    
    board_size = BOARD_SIZE
    ship_rules = SHIP_RULES

    def __init__(self):
        self.reset()

    def reset(self):
        
        self.size = self.board_size
        self.state = [[EMPTY_SYMBOL for col in range(self.size)]
                      for row in range(self.size)]
        self.ships = []

    def setup(self, auto=True):
       
        dummy = Board()
        while len(self.ships) < len(self.ship_rules):
            ship_size = self.ship_rules[len(self.ships)]

            if auto:
                
                try_count = 0
                while try_count <= 20:
                    try_count += 1
                    orientation = random.choice(('h', 'v'))
                    start_position = (random.randrange(self.size),
                                      random.randrange(self.size))
                    ship = Ship(ship_size, orientation, start_position)
                    if self.is_ship_fit(ship):
                        self.add_ship(ship)
                        break
                if try_count > 20:
                    self.reset()

            
            else:
                print_intro(self, dummy)
                print(f'Расстановка — Корабль №{len(self.ships) + 1}, '
                      f'{ship_size}-палубный')
                try:
                    if ship_size > 1:
                        orientation = input('Введите ориентацию корабля — '
                            'горизонтальная (h) или вертикальная (v): ')
                        start_position = (letters.index(l) for l in
                        input('Введите координаты верхней левой '
                        'точки: ').upper() if l in letters)
                    
                    else:
                        orientation = 'h'
                        start_position = (letters.index(l) for l in
                            input('Введите координаты корабля: ').upper()
                            if l in letters)
                    ship = Ship(ship_size, orientation, start_position)
                    if self.is_ship_fit(ship):
                        self.add_ship(ship)
                    else:
                        raise ValueError
                except ValueError:
                    print('Корабль нельзя разместить в указанных координатах.')
                    print('(r)eset — начать расстановку сначала.\n'
                          '(a)uto — закончить расстановку автоматически.\n'
                          '<Enter> для продолжения:', end=' ')
                    reset = input()
                    if reset.lower() in ('r', 'reset'):
                        self.reset()
                    elif reset.lower() in ('a', 'auto'):
                        auto = True

    def add_ship(self, ship):
        
        for x, y in ship.coordinates:
            self.state[x][y] = SHIP_SYMBOL
        self.ships.append(ship)

    def is_ship_fit(self, ship):
        
        
        if (ship.x + ship.height - 1 >= self.size or
            ship.y + ship.width - 1 >= self.size or
            ship.x < 0 or ship.y < 0):
            return False

        
        for x in range(ship.x - 1, ship.x + ship.height + 1):
            for y in range(ship.y - 1, ship.y + ship.width + 1):
                try:
                    if x < 0 or y < 0:
                        raise IndexError
                    if self.state[x][y] != EMPTY_SYMBOL:
                        return False
                except IndexError:
                    continue

        
        return True

    def take_shot(self, is_ai):
        
        while True:
            if is_ai:
                x, y = (random.randrange(self.size),
                        random.randrange(self.size))
                if self.state[x][y] in (MISS_SYMBOL, HIT_SYMBOL):
                    continue
                time.sleep(TIMEOUT)
                print(letters[x], letters[y])
                break
            try:
                x, y = (letters.index(l)
                        for l in input().upper() if l in letters)
                if x < 0 or x >= self.size or y < 0 or y >= self.size:
                    raise IndexError('Таких координат не существует.')
                if self.state[x][y] in (MISS_SYMBOL, HIT_SYMBOL):
                    raise IndexError('Вы уже стреляли в эту точку.')
            except ValueError:
                print('Неверный формат ввода. Попробуйте ещё раз:', end=' ')
            except IndexError as error_message:
                print(f'{error_message} Попробуйте ещё раз:', end=' ')
            else:
                break

        if self.state[x][y] == SHIP_SYMBOL:
            self.state[x][y] = HIT_SYMBOL
            time.sleep(TIMEOUT)
            print('Попадание!', end=' ', flush=True)
            if self.is_ship_dead(x, y):
                print('Корабль потоплен!')
                self.mark_ship_dead(x, y)
            else:
                print('Корабль ранен!')
            time.sleep(TIMEOUT)
            return True

        self.state[x][y] = MISS_SYMBOL
        time.sleep(TIMEOUT)
        print('Промах!')
        time.sleep(TIMEOUT)
        return False

    def is_ship_dead(self, shot_x, shot_y):
        
        dead_ship = [ship for ship in self.ships
                     if (shot_x, shot_y) in ship.coordinates][0]
        for x, y in dead_ship.coordinates:
            if self.state[x][y] == SHIP_SYMBOL:
                return False
        return True

    def mark_ship_dead(self, shot_x, shot_y):
       
        dead_ship = [ship for ship in self.ships
                     if (shot_x, shot_y) in ship.coordinates][0]
        for x in range(dead_ship.x - 1, dead_ship.x + dead_ship.height + 1):
            for y in range(dead_ship.y - 1, dead_ship.y + dead_ship.width + 1):
                try:
                    if x < 0 or y < 0:
                        raise IndexError
                    if self.state[x][y] == EMPTY_SYMBOL:
                        self.state[x][y] = MISS_SYMBOL
                except IndexError:
                    continue
        dead_ship_index = self.ships.index(dead_ship)
        self.ships.pop(dead_ship_index)

    def is_lose(self):
        
        return not self.ships


class Ship:
    
    def __init__(self, size, orientation, start_position):
        self.size = size
        self.orientation = orientation
        self.width = size if orientation in ('h', 'H') else 1
        self.height = 1 if orientation in ('h', 'H') else size
        self.x, self.y = start_position
        self.coordinates = []
        for cell in range(self.size):
            self.coordinates.append((self.x, self.y + cell)
                if self.orientation in ('h', 'H') else (self.x + cell, self.y))


def battleship():
    
    board1 = Board()
    board2 = Board()

    
    print_intro(board1, board2)
    auto = input('Расставить корабли автоматически? (y/n) ') in ('y', 'Y')
    board1.setup(auto)
    board2.setup()

    
    turn_count = 0
    current_board = board2
    while turn_count < BOARD_SIZE**2 * 2:
        turn_count += 1
        print_intro(board1, board2)
        print(f'Ход №{turn_count} —', end=' ')
        print('Компьютер' if current_board == board1 else 'Игрок')
        print('Координаты выстрела:', end=' ', flush=True)

        
        if not current_board.take_shot(is_ai=current_board == board1):
            current_board = board2 if current_board == board1 else board1
        if current_board.is_lose():
            break

    
    print_intro(board1, board2)
    print('Вы проиграли!' if current_board == board1 else 'Вы выиграли!')


    restart = input('Хотите сыграть ещё раз? (y/n) ') in ('y', 'Y')
    if restart:
        battleship()

    os.system(CLEAR_SCREEN)

if __name__ == '__main__':
    battleship()
