import pygame
import random

pygame.init()

# Set the dimensions of the screen
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
COLUMNS = 10
ROWS = 20
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')

# Define the colors
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

SHAPES = [
    [[1, 1, 1], [0, 1, 0]],  # T-shape
    [[1, 1], [1, 1]],        # O-shape
    [[0, 1, 1], [1, 1, 0]],  # S-shape
    [[1, 0, 0], [1, 1, 1]],  # L-shape
    [[0, 0, 1], [1, 1, 1]],  # J-shape
    [[1, 1, 0], [0, 1, 1]],  # Z-shape
    [[1, 1, 1, 1]]           # I-shape
]

SHAPES_COLORS = [CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED]

class Tetris:
    def __init__(self):
        self.board = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.game_over = False
        self.current_piece = self.new_piece()
        self.x = COLUMNS // 2 - len(self.current_piece[0]) // 2
        self.y = 0
        self.clock = pygame.time.Clock()

    def new_piece(self):
        shape = random.choice(SHAPES)
        color = random.choice(SHAPES_COLORS)
        return shape, color

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
                    # Check for boundary collisions
                    if new_x < 0 or new_x >= COLUMNS or new_y >= ROWS or new_y < 0:
                        return True
                    # Check for collision with placed pieces
                    if new_y >= 0 and self.board[new_y][new_x] != BLACK:
                        return True
        return False

    def place_piece(self):
        for i, row in enumerate(self.current_piece[0]):
            for j, cell in enumerate(row):
                if cell:
                    self.board[self.y + i][self.x + j] = self.current_piece[1]
        self.clear_lines()

    def clear_lines(self):
        full_lines = [i for i, row in enumerate(self.board) if all(cell != BLACK for cell in row)]
        for i in full_lines:
            del self.board[i]
            self.board.insert(0, [BLACK] * COLUMNS)

    def drop(self):
        while not self.check_collision(0, 1):
            self.y += 1
        self.place_piece()
        self.current_piece = self.new_piece()
        self.x = COLUMNS // 2 - len(self.current_piece[0]) // 2
        self.y = 0
        # Check collision for new piece after placement
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
            self.current_piece = self.new_piece()
            self.x = COLUMNS // 2 - len(self.current_piece[0]) // 2
            self.y = 0
            if self.check_collision(0, 0):
                self.game_over = True

    def draw(self):
        screen.fill(BLACK)
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell != BLACK:
                    pygame.draw.rect(screen, cell, (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        for i, row in enumerate(self.current_piece[0]):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, self.current_piece[1],
                                     ((self.x + j) * BLOCK_SIZE, (self.y + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        pygame.display.flip()

def main():
    game = Tetris()

    while not game.game_over:
        game.clock.tick(10)  # Controls the speed of the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move_left()
                if event.key == pygame.K_RIGHT:
                    game.move_right()
                if event.key == pygame.K_DOWN:
                    game.move_down()
                if event.key == pygame.K_UP:
                    game.rotate_piece()

        game.move_down()
        game.draw()

    # Game Over message
    font = pygame.font.Font(None, 74)
    text = font.render("Game Over", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.fill(BLACK)
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)  # Wait for 2 seconds before quitting

    pygame.quit()

if __name__ == "__main__":
    main()
