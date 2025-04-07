import pygame
import random
import os

# Inicializace pygame
pygame.init()

# Nastavení obrazovky
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
COLUMNS = 10
ROWS = 20

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')

# Barvy
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

# Tvar a barva bloků
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

    SHAPES_COLORS = [
        Colors.CYAN,
        Colors.BLUE,
        Colors.ORANGE,
        Colors.YELLOW,
        Colors.GREEN,
        Colors.PURPLE,
        Colors.RED
    ]

    @staticmethod
    def new_piece():
        shape = random.choice(Shapes.SHAPES)
        color = random.choice(Shapes.SHAPES_COLORS)
        return shape, color

# Herní pole
class GameField:
    def __init__(self):
        self.board = []
        for i in range(ROWS):
            self.board.append([Colors.BLACK] * COLUMNS)

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
                    pygame.draw.rect(
                        screen, cell,
                        (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    )

# Třída pro aktuální skóre
class Score:
    def __init__(self):
        self.score = 0

    def add_block_score(self):
        self.score += 10

    def add_line_score(self, lines_cleared):
        self.score += 100 * lines_cleared

    def get_score(self):
        return self.score

# Třída pro High Score
class HighScore:
    def __init__(self, file_path="highscore.txt"):
        self.file_path = file_path
        self.high_score = self.load_high_score()

    def load_high_score(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    return int(f.read())
            except:
                return 0
        return 0

    def save_high_score(self):
        with open(self.file_path, "w") as f:
            f.write(str(self.high_score))

    def update(self, current_score):
        if current_score > self.high_score:
            self.high_score = current_score
            self.save_high_score()

    def get_high_score(self):
        return self.high_score

# Hlavní Tetris logika
class Tetris:
    def __init__(self, game_field, score, high_score):
        self.game_field = game_field
        self.score = score
        self.high_score = high_score
        self.current_piece = Shapes.new_piece()
        self.x = COLUMNS // 2 - len(self.current_piece[0]) // 2
        self.y = 0
        self.game_over = False

    def rotate_piece(self):
        shape, color = self.current_piece
        rotated = [list(row) for row in zip(*shape[::-1])]
        old_piece = self.current_piece
        self.current_piece = (rotated, color)
        if self.check_collision(0, 0):
            self.current_piece = old_piece

    def check_collision(self, offset_x, offset_y):
        shape, _ = self.current_piece
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
        shape, color = self.current_piece
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    self.game_field.board[self.y + i][self.x + j] = color
        self.score.add_block_score()
        lines = self.game_field.clear_lines()
        self.score.add_line_score(lines)
        self.high_score.update(self.score.get_score())

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
        shape, color = self.current_piece
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        screen, color,
                        ((self.x + j) * BLOCK_SIZE, (self.y + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    )

# Hlavní hra
class Game:
    def __init__(self):
        self.field = GameField()
        self.score = Score()
        self.high_score = HighScore()
        self.tetris = Tetris(self.field, self.score, self.high_score)
        self.clock = pygame.time.Clock()

    def draw_scores(self):
        font = pygame.font.Font(None, 28)
        score_text = font.render(f"Score: {self.score.get_score()}", True, Colors.WHITE)
        high_score_text = font.render(f"High Score: {self.high_score.get_high_score()}", True, Colors.WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 40))

    def run(self):
        while not self.tetris.game_over:
            self.clock.tick(5)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.tetris.game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.tetris.move_left()
                    elif event.key == pygame.K_RIGHT:
                        self.tetris.move_right()
                    elif event.key == pygame.K_DOWN:
                        self.tetris.move_down()
                    elif event.key == pygame.K_UP:
                        self.tetris.rotate_piece()

            self.tetris.move_down()

            screen.fill(Colors.BLACK)
            self.field.draw()
            self.tetris.draw()
            self.draw_scores()
            pygame.display.flip()

        self.end_screen()

    def end_screen(self):
        font = pygame.font.Font(None, 48)
        text = font.render("Game Over", True, Colors.WHITE)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.fill(Colors.BLACK)
        screen.blit(text, rect)
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()

# Spuštění hry
if __name__ == "__main__":
    game = Game()
    game.run()
