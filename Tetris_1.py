import pygame
import random
import os

pygame.init()

SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
COLUMNS = 10
ROWS = 20
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')

class Colors:
    WHITE = (255, 255, 255)
    CYAN = (0, 255, 255)
    BLUE = (0, 0, 255)
    ORANGE = (255, 165, 0)
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0)
    PURPLE = (128, 0, 128)
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)
    GRAY = (40, 40, 40)

class Shapes:
    SHAPES = [
        [[1, 1, 1], [0, 1, 0]],
        [[1, 1], [1, 1]],
        [[0, 1, 1], [1, 1, 0]],
        [[1, 0, 0], [1, 1, 1]],
        [[0, 0, 1], [1, 1, 1]],
        [[1, 1, 0], [0, 1, 1]],
        [[1, 1, 1, 1]]
    ]

    SHAPES_COLORS = [Colors.CYAN, Colors.BLUE, Colors.ORANGE, Colors.YELLOW, Colors.GREEN, Colors.PURPLE, Colors.RED]

    @staticmethod
    def new_piece():
        shape = random.choice(Shapes.SHAPES)
        color = random.choice(Shapes.SHAPES_COLORS)
        return shape, color

class GameField:
    def __init__(self):
        self.board = [[Colors.BLACK] * COLUMNS for _ in range(ROWS)]

    def clear_lines(self):
        full_lines = []
        for i, row in enumerate(self.board):
            if all(cell != Colors.BLACK for cell in row):
                full_lines.append(i)

        for i in full_lines:
            del self.board[i]
            self.board.insert(0, [Colors.BLACK] * COLUMNS)

        return len(full_lines)

    def draw(self):
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell != Colors.BLACK:
                    pygame.draw.rect(screen, cell, (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(screen, Colors.BLACK, (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

# Čtverečkované pozadí
def draw_grid():
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, Colors.GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, Colors.GRAY, (0, y), (SCREEN_WIDTH, y))

class Tetris:
    def __init__(self, game_field, score):
        self.game_field = game_field
        self.score = score
        self.current_piece = Shapes.new_piece()
        self.x = COLUMNS // 2 - len(self.current_piece[0]) // 2
        self.y = 0
        self.game_over = False
        self.combo = 0

    def rotate_piece(self):
        shape, color = self.current_piece
        original_shape = shape
        new_shape = [list(row) for row in zip(*shape[::-1])]
        self.current_piece = (new_shape, color)
        if self.check_collision(0, 0):
            self.current_piece = (original_shape, color)

    def check_collision(self, offset_x, offset_y):
        shape, color = self.current_piece
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    new_x = self.x + j + offset_x
                    new_y = self.y + i + offset_y
                    if new_x < 0 or new_x >= COLUMNS or new_y >= ROWS or new_y < 0:
                        return True
                    if new_y >= 0 and self.game_field.board[new_y][new_x] != Colors.BLACK:
                        return True
        return False

    def place_piece(self):
        for i, row in enumerate(self.current_piece[0]):
            for j, cell in enumerate(row):
                if cell:
                    self.game_field.board[self.y + i][self.x + j] = self.current_piece[1]

        self.score.add_placement()
        lines_cleared = self.game_field.clear_lines()
        if lines_cleared > 0:
            self.combo += 1
        else:
            self.combo = 0

        self.score.add_score(lines_cleared, self.combo)

    def drop(self):
        while not self.check_collision(0, 1):
            self.y += 1
        self.place_piece()
        self.current_piece = Shapes.new_piece()
        self.x = COLUMNS // 2 - len(self.current_piece[0]) // 2
        self.y = 0
        if self.check_collision(0, 0):
            self.game_over = True

    def move_left(self):
        if not self.check_collision(-1, 0):
            self.x -= 1

    def move_right(self):
        if not self.check_collision(1, 0):
            self.x += 1

    def move_down(self):
        if not self.check_collision(0, 1):
            self.y += 1
        else:
            self.place_piece()
            self.current_piece = Shapes.new_piece()
            self.x = COLUMNS // 2 - len(self.current_piece[0]) // 2
            self.y = 0
            if self.check_collision(0, 0):
                self.game_over = True

    def draw(self):
        for i, row in enumerate(self.current_piece[0]):
            for j, cell in enumerate(row):
                if cell:
                    x = (self.x + j) * BLOCK_SIZE
                    y = (self.y + i) * BLOCK_SIZE
                    pygame.draw.rect(screen, self.current_piece[1], (x, y, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(screen, Colors.BLACK, (x, y, BLOCK_SIZE, BLOCK_SIZE), 1)

class Score:
    def __init__(self):
        self.score = 0

    def add_placement(self):
        self.score += 10

    def add_score(self, lines_cleared, combo):
        if lines_cleared > 0:
            self.score += lines_cleared * 100
            if combo > 1:
                self.score += (combo - 1) * 50

    def draw(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, Colors.WHITE)
        screen.blit(score_text, (10, 10))

class HighScore:
    def __init__(self, path="highscore.txt"):
        self.path = path
        self.high_score = self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                try:
                    return int(f.read())
                except:
                    return 0
        return 0

    def save(self):
        with open(self.path, "w") as f:
            f.write(str(self.high_score))

    def update(self, current_score):
        if current_score > self.high_score:
            self.high_score = current_score
            self.save()

    def draw(self):
        font = pygame.font.Font(None, 36)
        high_text = font.render(f"High Score: {self.high_score}", True, Colors.WHITE)
        screen.blit(high_text, (10, 50))

# Hra
class Game:
    def __init__(self):
        self.game_field = GameField()
        self.score = Score()
        self.high_score = HighScore()
        self.tetris = Tetris(self.game_field, self.score)
        self.clock = pygame.time.Clock()

    def run(self):
        while not self.tetris.game_over:
            self.clock.tick(5)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.tetris.game_over = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.tetris.move_left()
                    if event.key == pygame.K_RIGHT:
                        self.tetris.move_right()
                    if event.key == pygame.K_DOWN:
                        self.tetris.move_down()
                    if event.key == pygame.K_UP:
                        self.tetris.rotate_piece()

            self.tetris.move_down()

            screen.fill(Colors.BLACK)
            draw_grid()
            self.game_field.draw()
            self.tetris.draw()
            self.score.draw()
            self.high_score.update(self.score.score)
            self.high_score.draw()

            pygame.display.flip()

        font = pygame.font.Font(None, 74)
        text = font.render("Game Over", True, Colors.WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.fill(Colors.BLACK)
        screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()

if __name__ == "__main__":
    game_instance = Game()
    game_instance.run()