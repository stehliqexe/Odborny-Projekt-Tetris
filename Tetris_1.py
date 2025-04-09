import pygame
import random
import time
import sys

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
    DARK_PURPLE = (73, 8, 150)
    GRAY = (40, 40, 40)


class Shapes:
    SHAPES = [
        [[1, 1, 1], [0, 1, 0]],  # T-shape
        [[1, 1], [1, 1]],  # O-shape
        [[0, 1, 1], [1, 1, 0]],  # S-shape
        [[1, 0, 0], [1, 1, 1]],  # L-shape
        [[0, 0, 1], [1, 1, 1]],  # J-shape
        [[1, 1, 0], [0, 1, 1]],  # Z-shape
        [[1, 1, 1, 1]]  # I-shape
    ]

    SHAPES_COLORS = [Colors.CYAN, Colors.BLUE, Colors.ORANGE, Colors.YELLOW, Colors.GREEN, Colors.PURPLE, Colors.RED]

    @staticmethod
    def new_piece():
        shape = random.choice(Shapes.SHAPES)
        color = random.choice(Shapes.SHAPES_COLORS)
        return shape, color

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


def draw_grid():
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, Colors.GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, Colors.GRAY, (0, y), (SCREEN_WIDTH, y))


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


class Tetris:
    def __init__(self, game_field, score):
        self.game_field = game_field
        self.score = score
        self.current_piece = Shapes.new_piece()
        self.x = COLUMNS // 2 - len(self.current_piece[0]) // 2
        self.y = 0
        self.game_over = False

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
        self.score.add_placement()  # přidá 10 bodů za položení
        for i, row in enumerate(self.current_piece[0]):
            for j, cell in enumerate(row):
                if cell:
                    self.game_field.board[self.y + i][self.x + j] = self.current_piece[1]
        lines_cleared = self.game_field.clear_lines()
        self.score.add_score(lines_cleared)

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
                    pygame.draw.rect(
                        screen, self.current_piece[1],
                        ((self.x + j) * BLOCK_SIZE, (self.y + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    )


class Score:
    def __init__(self):
        self.score = 0
        self.streak = 0

    def add_placement(self):
        self.score += 10

    def add_score(self, lines_cleared):
        if lines_cleared > 0:
            bonus = 0
            if self.streak > 0:
                bonus = 50 * lines_cleared
            self.score += lines_cleared * 100 + bonus
            self.streak += 1
        else:
            self.streak = 0

    def draw(self):
        font = pygame.font.Font(None, 50)
        score_text = font.render(f"Score: {self.score}", True, Colors.WHITE)
        screen.blit(score_text, (10, 10))


class HighScore:
    def __init__(self):
        self.high_score = self.load_high_score()

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self, current_score):
        if current_score > self.high_score:
            self.high_score = current_score
            with open("highscore.txt", "w") as f:
                f.write(str(self.high_score))

    def draw(self):
        font = pygame.font.Font(None, 40)
        high_score_text = font.render(f"High Score: {self.high_score}", True, Colors.WHITE)
        screen.blit(high_score_text, (10, 60))

class Menu:
    def __init__(self):
        self.selected_option = 0
        self.options = ["START GAME", "HIGH SCORES", "QUIT"]
        self.title_font = pygame.font.Font(None, 72)
        self.option_font = pygame.font.Font(None, 42)
        self.small_font = pygame.font.Font(None, 24)
        self.title_color = Colors.RED
        self.option_colors = [Colors.WHITE, Colors.WHITE, Colors.WHITE]
        self.show_high_scores = False
        self.high_score = HighScore()
        self.animation_offset = 0
        self.last_animation_time = time.time()

    def update_animation(self):
        current_time = time.time()
        if current_time - self.last_animation_time > 0.05:
            self.animation_offset = (self.animation_offset + 1) % BLOCK_SIZE
            self.last_animation_time = current_time

    def draw_title(self, screen):
        # Main title
        title = self.title_font.render("TETRIS", True, self.title_color)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        # Decorative lines
        pygame.draw.line(
            screen, Colors.CYAN,
            (SCREEN_WIDTH // 2 - title.get_width() // 2 - 20, 80),
            (SCREEN_WIDTH // 2 + title.get_width() // 2 + 20, 80),
            3
        )

    def draw_background(self, screen):
        # Draw grid lines
        for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
            pygame.draw.line(
                screen, Colors.DARK_PURPLE,
                (x + self.animation_offset, 0),
                (x + self.animation_offset, SCREEN_HEIGHT),
                1
            )
        for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
            pygame.draw.line(
                screen, Colors.DARK_PURPLE,
                (0, y + self.animation_offset),
                (SCREEN_WIDTH, y + self.animation_offset),
                1
            )

    def draw_options(self, screen):
        # Draw black background boxes for each option first
        for i, option in enumerate(self.options):
            # Black semi-transparent background for each option
            option_bg = pygame.Surface((220, 50), pygame.SRCALPHA)
            option_bg.fill((0, 0, 0, 180))  # Semi-transparent black
            screen.blit(option_bg, (SCREEN_WIDTH // 2 - 110, 185 + i * 60))

            if i == self.selected_option:
                # Selected option effect - yellow border
                pygame.draw.rect(
                    screen, Colors.YELLOW,
                    (SCREEN_WIDTH // 2 - 110, 185 + i * 60, 220, 50),
                    2
                )

            # Draw the option text
            text_color = Colors.YELLOW if i == self.selected_option else Colors.WHITE
            text = self.option_font.render(option, True, text_color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 190 + i * 60))

    def draw_high_scores(self, screen):
        # Dark semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # High scores title
        title = self.option_font.render("HIGH SCORES", True, Colors.YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        # Score display
        score_text = self.title_font.render(str(self.high_score.high_score), True, Colors.CYAN)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 220))

        # Decorative frame
        pygame.draw.rect(
            screen, Colors.PURPLE,
            (SCREEN_WIDTH // 2 - 150, 130, 300, 200),
            3
        )

        # Back instruction
        back_text = self.small_font.render("Press ESC to return", True, Colors.WHITE)
        screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 350))

    def draw(self, screen):
        screen.fill(Colors.BLACK)
        self.update_animation()
        self.draw_background(screen)
        self.draw_title(screen)

        if not self.show_high_scores:
            self.draw_options(screen)

            # Draw instructions
            controls = [
                "CONTROLS:",
                "Key_UP, Key_DOWN - Navigate",
                'Key_LEFT, Key_RIGHT - Move',
                "ENTER - Select",
                "ESC - Back"
            ]
            for i, line in enumerate(controls):
                color = Colors.CYAN if i == 0 else Colors.WHITE
                text = self.small_font.render(line, True, color)
                screen.blit(text, (20, SCREEN_HEIGHT - 100 + i * 20))
        else:
            self.draw_high_scores(screen)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if not self.show_high_scores:
                    if event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                    elif event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_option == 0:  # Start Game
                            return "start"
                        elif self.selected_option == 1:  # High Scores
                            self.show_high_scores = True
                        elif self.selected_option == 2:  # Quit
                            return "quit"
                else:
                    if event.key == pygame.K_ESCAPE:
                        self.show_high_scores = False

        return "menu"


def show_menu():
    menu = Menu()
    clock = pygame.time.Clock()

    while True:
        result = menu.handle_input()
        if result != "menu":
            return result

        menu.draw(screen)
        pygame.display.flip()
        clock.tick(60)


def main():
    pygame.init()
    global screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetris')

    while True:
        menu_result = show_menu()

        if menu_result == "start":
            game_instance = Game()
            game_instance.run()
        elif menu_result == "quit":
            pygame.quit()
            sys.exit()


class GameOverScreen:
    def __init__(self, score, high_score):
        self.score = score
        self.high_score = high_score
        self.title_font = pygame.font.Font(None, 60)
        self.option_font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 24)
        self.selected_option = 0  # 0 for view high scores, 1 for restart
        self.new_high_score = score > high_score.high_score
        self.animation_offset = 0
        self.last_animation_time = time.time()
        self.options = ["VIEW HIGH SCORES", "PLAY AGAIN", "MAIN MENU"]

    def update_animation(self):
        current_time = time.time()
        if current_time - self.last_animation_time > 0.05:
            self.animation_offset = (self.animation_offset + 1) % BLOCK_SIZE
            self.last_animation_time = current_time

    def draw_title(self, screen):
        # Main title
        title = self.title_font.render("GAME OVER", True, Colors.RED)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        # Decorative lines
        pygame.draw.line(
            screen, Colors.CYAN,
            (SCREEN_WIDTH // 2 - title.get_width() // 2 - 20, 80),
            (SCREEN_WIDTH // 2 + title.get_width() // 2 + 20, 80),
            3
        )

    def draw_score_info(self, screen):
        # Score display
        score_text = self.option_font.render(f"YOUR SCORE: {self.score}", True, Colors.WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 120))

        # High score indication if applicable
        if self.new_high_score:
            new_high_text = self.small_font.render("NEW HIGH SCORE!", True, Colors.YELLOW)
            screen.blit(new_high_text, (SCREEN_WIDTH // 2 - new_high_text.get_width() // 2, 170))

    def draw_options(self, screen):
        # Draw black background boxes for each option first
        for i, option in enumerate(self.options):
            # Black semi-transparent background for each option
            option_bg = pygame.Surface((220, 50), pygame.SRCALPHA)
            option_bg.fill((0, 0, 0, 180))  # Semi-transparent black
            screen.blit(option_bg, (SCREEN_WIDTH // 2 - 110, 220 + i * 60))

            if i == self.selected_option:
                # Selected option effect - yellow border
                pygame.draw.rect(
                    screen, Colors.YELLOW,
                    (SCREEN_WIDTH // 2 - 110, 220 + i * 60, 220, 50),
                    2
                )

            # Draw the option text
            text_color = Colors.YELLOW if i == self.selected_option else Colors.WHITE
            text = self.option_font.render(option, True, text_color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 225 + i * 60))

    def draw(self, screen):
        # Keep the game board visible in the background
        screen.fill(Colors.BLACK)
        self.update_animation()
        self.draw_title(screen)
        self.draw_score_info(screen)
        self.draw_options(screen)

        # Draw instructions
        controls = [
            "CONTROLS:",
            "Key_UP, Key_DOWN - Navigate",
            "Key_LEFT, Key_RIGHT - Move",
            "ENTER - Select",
            "ESC - Back"
        ]
        for i, line in enumerate(controls):
            color = Colors.CYAN if i == 0 else Colors.WHITE
            text = self.small_font.render(line, True, color)
            screen.blit(text, (20, SCREEN_HEIGHT - 100 + i * 20))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.selected_option == 0:  # View High Scores
                        return "view_scores"
                    elif self.selected_option == 1:  # Play Again
                        return "restart"
                    elif self.selected_option == 2:  # Main Menu
                        return "menu"
                elif event.key == pygame.K_ESCAPE:
                    return "menu"
        return "game_over"


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
                    if event.key == pygame.K_SPACE:
                        self.tetris.drop()

            self.tetris.move_down()

            screen.fill(Colors.BLACK)
            draw_grid()
            self.game_field.draw()
            self.tetris.draw()
            self.score.draw()
            self.high_score.draw()

            pygame.display.flip()

        # Save high score and show game over screen
        self.high_score.save_high_score(self.score.score)
        game_over_screen = GameOverScreen(self.score.score, self.high_score)

        while True:
            action = game_over_screen.handle_input()

            if action == "quit":
                pygame.quit()
                sys.exit()
            elif action == "view_scores":
                self.show_high_scores()
            elif action == "restart":
                return "restart"
            elif action == "menu":
                return "menu"

            screen.fill(Colors.BLACK)
            # Redraw the game board in the background
            draw_grid()
            self.game_field.draw()
            self.tetris.draw()
            # Then draw the game over screen
            game_over_screen.draw(screen)
            pygame.display.flip()
            self.clock.tick(60)

    def show_high_scores(self):
        # Create a high score display screen matching the menu style
        clock = pygame.time.Clock()
        showing_scores = True

        # Create a temporary menu-like object for consistent styling
        class TempMenu:
            def __init__(self, high_score, current_score):
                self.high_score = high_score
                self.current_score = current_score
                self.title_font = pygame.font.Font(None, 60)
                self.score_font = pygame.font.Font(None, 36)
                self.small_font = pygame.font.Font(None, 24)
                self.animation_offset = 0
                self.last_animation_time = time.time()

            def update_animation(self):
                current_time = time.time()
                if current_time - self.last_animation_time > 0.05:
                    self.animation_offset = (self.animation_offset + 1) % BLOCK_SIZE
                    self.last_animation_time = current_time

            def draw_background(self, screen):
                # Draw grid lines
                for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
                    pygame.draw.line(
                        screen, Colors.DARK_PURPLE,
                        (x + self.animation_offset, 0),
                        (x + self.animation_offset, SCREEN_HEIGHT),
                        1
                    )
                for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
                    pygame.draw.line(
                        screen, Colors.DARK_PURPLE,
                        (0, y + self.animation_offset),
                        (SCREEN_WIDTH, y + self.animation_offset),
                        1
                    )

            def draw(self, screen):
                self.update_animation()

                # Dark semi-transparent background
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                screen.blit(overlay, (0, 0))

                self.draw_background(screen)

                # Score display box
                score_bg = pygame.Surface((250, 120), pygame.SRCALPHA)
                score_bg.fill((0, 0, 0, 180))
                screen.blit(score_bg, (SCREEN_WIDTH // 2 - 125, 150))

                # Current score
                current_text = self.score_font.render(f"Your Score: {self.current_score}", True, Colors.WHITE)
                screen.blit(current_text, (SCREEN_WIDTH // 2 - current_text.get_width() // 2, 170))

                # High score
                high_text = self.score_font.render(f"High Score: {self.high_score}", True, Colors.CYAN)
                screen.blit(high_text, (SCREEN_WIDTH // 2 - high_text.get_width() // 2, 220))

                # Instructions
                instructions = self.small_font.render("Press ENTER or ESC to continue", True, Colors.WHITE)
                screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 350))

        temp_menu = TempMenu(self.high_score.high_score, self.score.score)

        while showing_scores:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                        showing_scores = False

            # Redraw the game board in the background
            screen.fill(Colors.BLACK)
            draw_grid()
            self.game_field.draw()
            self.tetris.draw()

            # Draw the high scores overlay
            temp_menu.draw(screen)

            pygame.display.flip()
            clock.tick(60)

# Modify the main function to handle the restart option
def main():
    pygame.init()
    global screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetris')

    while True:
        menu_result = show_menu()

        if menu_result == "start":
            while True:
                game_instance = Game()
                result = game_instance.run()
                if result == "menu":
                    break
                # If "restart", the loop will continue and create a new game
        elif menu_result == "quit":
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()