# МОРСКОЙ БОЙ
from random import randint
from time import sleep

# ВНУТРЕННЯЯ ЛОГИКА ИГРЫ

# ИСКЛЮЧЕНИЯ
# Общий класс
class BoardException(Exception):
    pass
# Частные случаи
class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел МИМО доски! Попробуйте еще раз!"
class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту точку! Попробуйте еще раз!"
class BoardWrongShipException(BoardException):
    pass

# ТОЧКА
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    # для удобства отображения создадим __repr__
    def __repr__(self):
        return f"({self.x}, {self.y})"

# КОРАБЛЬ
class Ship:
    def __init__(self, bowCoord, length, direction):
        self.bow = bowCoord
        self.l = length
        self.direction = direction
        self.lives = length

    @property
    def dots(self):
        shipDots = []
        for i in range(self.l):
            bowX = self.bow.x
            bowY = self.bow.y

            if self.direction == 0:
                bowX += i

            elif self.direction == 1:
                bowY += i

            shipDots.append(Dot(bowX, bowY))

        return shipDots

    def shooten(self, shot):
        return shot in self.dots

# ИГРОВОЕ ПОЛЕ
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.damaged = 0
        self.field = [["O"] * size for _ in range(size)]
        self.busyDots = []
        self.shipList = []

    # вывод корабля через магический метод __str__
    def __str__(self):
        res = "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"
        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        nearDots = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in nearDots:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busyDots:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busyDots.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busyDots:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busyDots.append(d)

        self.shipList.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        if d in self.busyDots:
            raise BoardUsedException()

        self.busyDots.append(d)

        for ship in self.shipList:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"

                if ship.lives == 0:
                    self.damaged += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    # ход переходит противнику
                    return True
                else:
                    print("Корабль ранен!")
                    # можно ходить повторно
                    return True

        # ни один корабль не поражен
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busyDots = []

    def defeat(self):
        return self.damaged == len(self.shipList)

# Внешняя логика игры

class Player:
    def __init__(self, userboard, enemyboard):
        self.board = userboard
        self.enemy = enemyboard

    def ask(self):
        # для того, чтобы объявить метод у родителя, но определять его в потомках
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                request = self.ask()
                repeat = self.enemy.shot(request)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Противник выстрелил по {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            coord = input("Куда стреляем? \n").split()

            if len(coord) != 2:
                print("Введите 2 координаты через пробел!")
                continue

            x, y = coord
            if not (x.isdigit()) or not (y.isdigit()):
                print("Вводите только числа!")
                continue

            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)

# ИГРА
class Game:
    def __init__(self, size=6):
        self.size = size
        player = self.random_board()
        comp = self.random_board()
        comp.hid = True

        self.ai = AI(comp, player)
        self.user = User(player, comp)
    # попытка сгенерировать поле
    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print('============================================')
        print('            Свистать всех наверх!           ')
        print('      Добро пожаловать в морской бой!      \n')
        print('ЦЕЛЬ игры - уничтожить 7 кораблей противника')
        print('============================================')
        confirmation = input('             Готов к битве? \nВведи Y для начала игры, N - если передумал:\n').upper()
        while True:
            if confirmation == 'N':
                print('============================================')
                print('        Приходи поиграть потом! Пока!       ')
                print('============================================')
                break
            elif confirmation != 'N' and confirmation != 'Y':
                confirmation = input('Сыграем? Введи Y или N \n').upper()
                continue
            else:
                self.loop()
                break

    def loop(self):
        num = 0
        while True:
            #print('-'*27)
            #print('Ваша доска:')
            #print(self.user.board)
            #print('-' * 27)
            #print('Доска противника:')
            #print(self.ai.board)

            col_len = 40

            user_board_str = self.user.board.__str__().split('\n')
            ai_board_str = self.ai.board.__str__().split('\n')

            print(' '.join(([str('-'*27).center(col_len), str('-'*28).center(col_len)])))
            print(' '.join(['Ваша доска:'.center(col_len), 'Доска противника:'.center(col_len)]))
            for a,b in zip(user_board_str, ai_board_str):
                print('  '.join([a.center(col_len), b.center(col_len)]))
            print(' '.join(([str('-' * 27).center(col_len), str('-' * 28).center(col_len)])))
            if num % 2 == 0:
                # print('-' * 27)
                print('Ваш ход!')
                repeat = self.user.move()
            else:
               # print('-' * 27)
                print('Ход компьютера!')
                sleep(2)
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                print('='*27)
                print('         Вы выиграли!   ')
                print('=' * 27)
                break
            if self.user.board.defeat():
                print('=' * 27)
                print('   Выиграл компьютер!   ')
                print('=' * 27)
                break
            num += 1

    def start(self):
        self.greet()


g = Game()
g.start()