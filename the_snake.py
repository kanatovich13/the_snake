import sys
from random import choice, randint

import pygame as pg

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

CENTER = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

OPPOSITE_DIRECTIONS = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT
}

BOARD_BACKGROUND_COLOR = (211, 211, 211)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

DEFAULT_POSITION = (0, 0)

SPEED = 10

# Константа для заголовка
CAPTION_TEXT = 'Змейка | Рекорд: {high_score} | Длина: {length} | ESC - выход'

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=DEFAULT_POSITION, body_color=None):
        """Инициализация объекта."""
        self.position = position
        self.body_color = body_color

    def draw_cell(self, position, color=None, border_color=BORDER_COLOR):
        """Отрисовка одной ячейки."""
        color = color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, border_color, rect, 1)

    def draw(self):
        """Метод отрисовки (переопределяется)."""
        raise NotImplementedError(
            f'Метод draw не определен в классе {self.__class__.__name__}'
        )


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, occupied_positions=None, body_color=APPLE_COLOR):
        """Инициализация яблока."""
        super().__init__(body_color=body_color)
        self.randomize_position(occupied_positions or [])

    def randomize_position(self, occupied_positions):
        """Выбор случайной позиции."""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовка яблока."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Инициализация змейки."""
        super().__init__(body_color=body_color)
        self.reset()

    def get_head_position(self):
        """Получение позиции головы."""
        return self.positions[0]

    def reset(self):
        """Сброс состояния змейки."""
        self.length = 1
        self.positions = [CENTER]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None

    def update_direction(self, next_direction):
        """Обновление направления движения."""
        if next_direction != OPPOSITE_DIRECTIONS.get(self.direction):
            self.direction = next_direction

    def move(self):
        """Перемещение змейки."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        self.positions.insert(0, (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        ))

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовка змейки."""
        for position in self.positions:
            self.draw_cell(position)

        if self.last:
            self.draw_cell(
                self.last,
                BOARD_BACKGROUND_COLOR,
                BOARD_BACKGROUND_COLOR
            )


def handle_keys(snake):
    """Обработка нажатий клавиш."""
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
    """Основная функция игры."""
    pg.init()
    snake = Snake()
    apple = Apple(snake.positions)

    screen.fill(BOARD_BACKGROUND_COLOR)

    high_score = 0

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

            score = snake.length - 1
            if score > high_score:
                high_score = score

        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        # Применение format для заголовка
        pg.display.set_caption(
            CAPTION_TEXT.format(high_score=high_score, length=snake.length)
        )

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
