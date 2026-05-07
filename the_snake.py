import sys
from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центр экрана:
CENTER = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Словарь противоположных направлений
OPPOSITE_DIRECTIONS = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT
}

# Цвета:
BOARD_BACKGROUND_COLOR = (211, 211, 211)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Позиция по умолчанию:
DEFAULT_POSITION = (0, 0)

# Скорость:
SPEED = 10

# Настройка окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
clock = pg.time.Clock()


class GameObject:
    """Родитель классов Snake и Apple."""

    def __init__(self, position=DEFAULT_POSITION, body_color=None):
        self.position = position
        self.body_color = body_color

    def draw_cell(self, position, color=None):
        """Отрисовывает одну ячейку на игровом поле."""
        color = color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Метод для переопределения в наследниках."""
        raise NotImplementedError(
            f'Метод draw не определен в классе {self.__class__.__name__}'
        )


class Apple(GameObject):
    """Класс для яблока."""

    def __init__(self, occupied_positions=None, body_color=APPLE_COLOR):
        super().__init__(body_color=body_color)
        self.randomize_position(occupied_positions or [])

    def randomize_position(self, occupied_positions):
        """Устанавливает случайное положение яблока, не занятое змейкой."""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовка яблока на экране."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс для змеи."""

    def __init__(self):
        super().__init__(body_color=SNAKE_COLOR)
        self.reset()

    def get_head_position(self):
        """Возвращает позицию головы змеи."""
        return self.positions[0]

    def reset(self):
        """Начальная позиция."""
        self.length = 1
        self.positions = [CENTER]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None

    def update_direction(self, next_direction):
        """Обновляет направление, если оно не противоположное текущему."""
        if next_direction != OPPOSITE_DIRECTIONS.get(self.direction):
            self.direction = next_direction

    def move(self):
        """Логика перемещения."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        # Вставка новой головы с расчетом сквозного прохода
        self.positions.insert(0, (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        ))

        # Удаление хвоста с использованием тернарного оператора
        self.last = self.positions.pop() if len(self.positions) > self.length else None

    def draw(self):
        """Отрисовка головы змейки и затирание хвоста."""
        # Отрисовываем голову
        self.draw_cell(self.get_head_position())

        # Затираем старый хвост цветом фона
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)


def handle_keys(snake):
    """Функция обработки нажатий клавиш."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()

            if event.key == pg.K_UP:
                snake.update_direction(UP)
            elif event.key == pg.K_DOWN:
                snake.update_direction(DOWN)
            elif event.key == pg.K_LEFT:
                snake.update_direction(LEFT)
            elif event.key == pg.K_RIGHT:
                snake.update_direction(RIGHT)


def main():
    """Основной цикл."""
    pg.init()
    snake = Snake()
    apple = Apple(snake.positions)

    # Очистка экрана один раз при старте
    screen.fill(BOARD_BACKGROUND_COLOR)

    # Счет и рекорд (для заголовка)
    high_score = 0

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.move()

        # Проверка на поедание яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
            apple.draw()

        # Обновление рекорда и заголовка
        score = snake.length - 1
        if score > high_score:
            high_score = score
        
        caption = f"Змейка | Рекорд: {high_score} | Длина: {snake.length} | ESC - выход"
        pg.display.set_caption(caption)

        # Проверка на "самоукус" (начиная с длины 5)
        if snake.get_head_position() in snake.positions[4:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
