# Import potřebných knihoven
import pygame  # Knihovna pro tvorbu her
import random  # Pro generování náhodných čísel
import time  # Pro práci s časem
import sys  # Pro systémové funkce (ukončení programu)

# Inicializace Pygame
pygame.init()

# Nastavení velikosti obrazovky
SCREEN_WIDTH = 300  # Šířka hrací plochy
SCREEN_HEIGHT = 600  # Výška hrací plochy
BLOCK_SIZE = 30  # Velikost jednoho bloku
COLUMNS = 10  # Počet sloupců v herním poli
ROWS = 20  # Počet řádků v herním poli

# Vytvoření okna hry
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Petris')  # Název okna

# Třída pro definici barev
class Colors:
    WHITE = (255, 255, 255)  # Bílá
    CYAN = (0, 255, 255)  # Azurová
    BLUE = (0, 0, 255)  # Modrá
    ORANGE = (255, 165, 0)  # Oranžová
    YELLOW = (255, 255, 0)  # Žlutá
    GREEN = (0, 255, 0)  # Zelená
    PURPLE = (128, 0, 128)  # Fialová
    RED = (255, 0, 0)  # Červená
    BLACK = (0, 0, 0)  # Černá
    DARK_PURPLE = (73, 8, 150)  # Tmavě fialová
    GRAY = (40, 40, 40)  # Šedá

# Třída pro tvary tetramin
class Shapes:
    SHAPES = [
        [[1, 1, 1], [0, 1, 0]],  # T-tvar
        [[1, 1], [1, 1]],  # O-tvar (čtverec)
        [[0, 1, 1], [1, 1, 0]],  # S-tvar
        [[1, 0, 0], [1, 1, 1]],  # L-tvar
        [[0, 0, 1], [1, 1, 1]],  # J-tvar
        [[1, 1, 0], [0, 1, 1]],  # Z-tvar
        [[1, 1, 1, 1]]  # I-tvar
    ]

    # Barvy pro jednotlivé tvary
    SHAPES_COLORS = [Colors.CYAN, Colors.BLUE, Colors.ORANGE, Colors.YELLOW, Colors.GREEN, Colors.PURPLE, Colors.RED]

    # Statická metoda pro vytvoření nového kusu
    @staticmethod
    def new_piece():
        shape = random.choice(Shapes.SHAPES)  # Náhodný výběr tvaru
        color = random.choice(Shapes.SHAPES_COLORS)  # Náhodný výběr barvy
        return shape, color

# Funkce pro vykreslení mřížky
def draw_grid():
    # Vykreslení vertikálních čar mřížky
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, Colors.GRAY, (x, 0), (x, SCREEN_HEIGHT))
    # Vykreslení horizontálních čar mřížky
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, Colors.GRAY, (0, y), (SCREEN_WIDTH, y))

# Třída pro herní pole
class GameField:
    def __init__(self):
        # Inicializace prázdného herního pole
        self.board = []
        for i in range(ROWS):
            self.board.append([Colors.BLACK] * COLUMNS)  # Všechny buňky černé (prázdné)

    # Metoda pro mazání plných řádků
    def clear_lines(self):
        full_lines = []  # Seznam indexů plných řádků
        # Prohledání všech řádků
        for i, row in enumerate(self.board):
            if all(cell != Colors.BLACK for cell in row):  # Pokud je řádek plný
                full_lines.append(i)  # Přidáme index do seznamu

        # Smazání plných řádků a přidání nových prázdných nahoře
        for i in full_lines:
            del self.board[i]  # Smazání řádku
            self.board.insert(0, [Colors.BLACK] * COLUMNS)  # Přidání prázdného řádku nahoru

        return len(full_lines)  # Vrátíme počet smazaných řádků

    # Metoda pro vykreslení herního pole
    def draw(self):
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell != Colors.BLACK:  # Pokud buňka není prázdná
                    pygame.draw.rect(
                        screen, cell,
                        (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    )  # Vykreslení čtverečku

# Třída pro hlavní herní logiku Tetris
class Tetris:
    def __init__(self, game_field, score):
        self.game_field = game_field  # Reference na herní pole
        self.score = score  # Reference na skóre
        self.current_piece = Shapes.new_piece()  # Vytvoření nového kusu
        self.x = COLUMNS // 2 - len(self.current_piece[0]) // 2  # Výchozí X pozice
        self.y = 0  # Výchozí Y pozice
        self.game_over = False  # Stav hry

    # Metoda pro rotaci kusu
    def rotate_piece(self):
        shape, color = self.current_piece
        original_shape = shape  # Uložení původního tvaru
        # Rotace tvaru (transpozice a obrácení řádků)
        new_shape = [list(row) for row in zip(*shape[::-1])]
        self.current_piece = (new_shape, color)

        # Pokud by po rotaci došlo ke kolizi, vrátíme původní tvar
        if self.check_collision(0, 0):
            self.current_piece = (original_shape, color)

    # Metoda pro kontrolu kolizí
    def check_collision(self, offset_x, offset_y):
        shape, color = self.current_piece
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:  # Pokud je část kusu na této pozici
                    new_x = self.x + j + offset_x  # Nová X pozice
                    new_y = self.y + i + offset_y  # Nová Y pozice
                    # Kontrola, zda jsme mimo hrací pole
                    if new_x < 0 or new_x >= COLUMNS or new_y >= ROWS or new_y < 0:
                        return True
                    # Kontrola kolize s již umístěnými kusy
                    if new_y >= 0 and self.game_field.board[new_y][new_x] != Colors.BLACK:
                        return True
        return False  # Nedošlo ke kolizi

    # Metoda pro umístění kusu na herní pole
    def place_piece(self):
        self.score.add_placement()  # Přidání bodů za umístění
        for i, row in enumerate(self.current_piece[0]):
            for j, cell in enumerate(row):
                if cell:  # Pokud je část kusu na této pozici
                    # Umístění barvy kusu na herní pole
                    self.game_field.board[self.y + i][self.x + j] = self.current_piece[1]
        # Mazání plných řádků a přidání bodů
        lines_cleared = self.game_field.clear_lines()
        self.score.add_score(lines_cleared)

    # Metoda pro rychlý pád kusu
    def drop(self):
        # Posun kusu dolů, dokud nenarazí
        while not self.check_collision(0, 1):
            self.y += 1
        self.place_piece()  # Umístění kusu
        # Vytvoření nového kusu
        self.current_piece = Shapes.new_piece()
        self.x = COLUMNS // 2 - len(self.current_piece[0]) // 2  # Reset X pozice
        self.y = 0  # Reset Y pozice
        # Kontrola konce hry (nový kus nemůže být umístěn)
        if self.check_collision(0, 0):
            self.game_over = True

    # Metoda pro pohyb doleva
    def move_left(self):
        if not self.check_collision(-1, 0):  # Pokud nedojde ke kolizi
            self.x -= 1  # Posun doleva

    # Metoda pro pohyb doprava
    def move_right(self):
        if not self.check_collision(1, 0):  # Pokud nedojde ke kolizi
            self.x += 1  # Posun doprava

    # Metoda pro pohyb dolů
    def move_down(self):
        if not self.check_collision(0, 1):  # Pokud nedojde ke kolizi
            self.y += 1  # Posun dolů
        else:
            self.place_piece()  # Pokud nelze dál, umístíme kus
            # Vytvoření nového kusu
            self.current_piece = Shapes.new_piece()
            self.x = COLUMNS // 2 - len(self.current_piece[0]) // 2
            self.y = 0
            # Kontrola konce hry
            if self.check_collision(0, 0):
                self.game_over = True

    # Metoda pro vykreslení aktuálního kusu
    def draw(self):
        for i, row in enumerate(self.current_piece[0]):
            for j, cell in enumerate(row):
                if cell:  # Pokud je část kusu na této pozici
                    pygame.draw.rect(
                        screen, self.current_piece[1],
                        ((self.x + j) * BLOCK_SIZE, (self.y + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    )  # Vykreslení čtverečku

# Třída pro správu skóre
class Score:
    def __init__(self):
        self.score = 0  # Aktuální skóre
        self.streak = 0  # Počet po sobě jdoucích smazaných řádků

    # Metoda pro přidání bodů za umístění kusu
    def add_placement(self):
        self.score += 10  # 10 bodů za každý umístěný kus

    # Metoda pro přidání bodů za smazané řádky
    def add_score(self, lines_cleared):
        if lines_cleared > 0:  # Pokud byly smazány nějaké řádky
            bonus = 0
            if self.streak > 0:  # Pokud jde o sekvenci
                bonus = 50 * lines_cleared  # Bonus za sekvenci
            self.score += lines_cleared * 100 + bonus  # 100 bodů za řádek + bonus
            self.streak += 1  # Zvýšení počtu sekvence
        else:
            self.streak = 0  # Reset sekvence

    # Metoda pro vykreslení skóre
    def draw(self):
        font = pygame.font.Font(None, 50)  # Vytvoření fontu
        score_text = font.render(f"Score: {self.score}", True, Colors.WHITE)  # Vytvoření textu
        screen.blit(score_text, (10, 10))  # Vykreslení textu

# Třída pro správu nejlepšího skóre
class HighScore:
    def __init__(self):
        self.high_score = self.load_high_score()  # Načtení nejlepšího skóre ze souboru

    # Metoda pro načtení nejlepšího skóre ze souboru
    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())  # Přečtení hodnoty
        except:
            return 0  # Pokud soubor neexistuje, vrátíme 0

    # Metoda pro uložení nejlepšího skóre do souboru
    def save_high_score(self, current_score):
        if current_score > self.high_score:  # Pokud je aktuální skóre lepší
            self.high_score = current_score  # Aktualizujeme nejlepší skóre
            with open("highscore.txt", "w") as f:
                f.write(str(self.high_score))  # Uložení do souboru

    # Metoda pro vykreslení nejlepšího skóre
    def draw(self):
        font = pygame.font.Font(None, 40)  # Vytvoření fontu
        high_score_text = font.render(f"High Score: {self.high_score}", True, Colors.WHITE)  # Vytvoření textu
        screen.blit(high_score_text, (10, 60))  # Vykreslení textu

# Třída pro hlavní menu
class Menu:
    def __init__(self):
        self.selected_option = 0  # Aktuálně vybraná možnost
        self.options = ["START GAME", "HIGH SCORES", "QUIT"]  # Možnosti menu
        self.title_font = pygame.font.Font(None, 72)  # Font pro nadpis
        self.option_font = pygame.font.Font(None, 42)  # Font pro možnosti
        self.small_font = pygame.font.Font(None, 24)  # Malý font
        self.title_color = Colors.RED  # Barva nadpisu
        self.option_colors = [Colors.WHITE, Colors.WHITE, Colors.WHITE]  # Barvy možností
        self.show_high_scores = False  # Příznak zobrazení nejlepších skóre
        self.high_score = HighScore()  # Instance pro nejlepší skóre
        self.animation_offset = 0  # Posun pro animaci pozadí
        self.last_animation_time = time.time()  # Čas poslední animace

    # Metoda pro aktualizaci animace pozadí
    def update_animation(self):
        current_time = time.time()
        if current_time - self.last_animation_time > 0.05:  # Každých 0.05 sekundy
            self.animation_offset = (self.animation_offset + 1) % BLOCK_SIZE  # Posun mřížky
            self.last_animation_time = current_time

    # Metoda pro vykreslení nadpisu
    def draw_title(self, screen):
        # Vykreslení hlavního nadpisu
        title = self.title_font.render("PETRIS", True, self.title_color)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        # Dekorační čára pod nadpisem
        pygame.draw.line(
            screen, Colors.CYAN,
            (SCREEN_WIDTH // 2 - title.get_width() // 2 - 20, 80),
            (SCREEN_WIDTH // 2 + title.get_width() // 2 + 20, 80),
            3
        )

    # Metoda pro vykreslení pozadí s animovanou mřížkou
    def draw_background(self, screen):
        # Vykreslení vertikálních čar
        for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
            pygame.draw.line(
                screen, Colors.DARK_PURPLE,
                (x + self.animation_offset, 0),
                (x + self.animation_offset, SCREEN_HEIGHT),
                1
            )
        # Vykreslení horizontálních čar
        for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
            pygame.draw.line(
                screen, Colors.DARK_PURPLE,
                (0, y + self.animation_offset),
                (SCREEN_WIDTH, y + self.animation_offset),
                1
            )

    # Metoda pro vykreslení možností menu
    def draw_options(self, screen):
        # Vykreslení pozadí pro každou možnost
        for i, option in enumerate(self.options):
            # Poloprůhledné černé pozadí
            option_bg = pygame.Surface((220, 50), pygame.SRCALPHA)
            option_bg.fill((0, 0, 0, 180))
            screen.blit(option_bg, (SCREEN_WIDTH // 2 - 110, 185 + i * 60))

            # Zvýraznění vybrané možnosti žlutým rámečkem
            if i == self.selected_option:
                pygame.draw.rect(
                    screen, Colors.YELLOW,
                    (SCREEN_WIDTH // 2 - 110, 185 + i * 60, 220, 50),
                    2
                )

            # Vykreslení textu možnosti
            text_color = Colors.YELLOW if i == self.selected_option else Colors.WHITE
            text = self.option_font.render(option, True, text_color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 190 + i * 60))

    # Metoda pro vykreslení obrazovky s nejlepšími skóre
    def draw_high_scores(self, screen):
        # Poloprůhledné černé pozadí
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Nadpis
        title = self.option_font.render("HIGH SCORES", True, Colors.YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        # Nejlepší skóre
        score_text = self.title_font.render(str(self.high_score.high_score), True, Colors.CYAN)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 220))

        # Dekorační rámeček
        pygame.draw.rect(
            screen, Colors.PURPLE,
            (SCREEN_WIDTH // 2 - 150, 130, 300, 200),
            3
        )

        # Návod pro návrat
        back_text = self.small_font.render("Press ESC to return", True, Colors.WHITE)
        screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 350))

    # Hlavní metoda pro vykreslení menu
    def draw(self, screen):
        screen.fill(Colors.BLACK)  # Vyplnění černou barvou
        self.update_animation()  # Aktualizace animace
        self.draw_background(screen)  # Vykreslení pozadí
        self.draw_title(screen)  # Vykreslení nadpisu

        if not self.show_high_scores:  # Pokud nezobrazujeme skóre
            self.draw_options(screen)  # Vykreslení možností

            # Vykreslení ovládání
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
            self.draw_high_scores(screen)  # Vykreslení nejlepších skóre

    # Metoda pro zpracování vstupu v menu
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Pokud uživatel zavře okno
                return "quit"

            if event.type == pygame.KEYDOWN:  # Stisk klávesy
                if not self.show_high_scores:  # Pokud jsme v hlavním menu
                    if event.key == pygame.K_DOWN:  # Šipka dolů
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                    elif event.key == pygame.K_UP:  # Šipka nahoru
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:  # Enter
                        if self.selected_option == 0:  # Start hry
                            return "start"
                        elif self.selected_option == 1:  # Nejlepší skóre
                            self.show_high_scores = True
                        elif self.selected_option == 2:  # Konec
                            return "quit"
                else:  # Pokud zobrazujeme skóre
                    if event.key == pygame.K_ESCAPE:  # Escape pro návrat
                        self.show_high_scores = False

        return "menu"  # Vrátíme stav menu

# Funkce pro zobrazení menu
def show_menu():
    menu = Menu()  # Vytvoření instance menu
    clock = pygame.time.Clock()  # Vytvoření hodin pro FPS

    while True:
        result = menu.handle_input()  # Zpracování vstupu
        if result != "menu":  # Pokud uživatel něco vybral
            return result  # Vrátíme výsledek

        menu.draw(screen)  # Vykreslení menu
        pygame.display.flip()  # Aktualizace obrazovky
        clock.tick(60)  # Omezení na 60 FPS

# Hlavní funkce programu
def main():
    pygame.init()  # Inicializace Pygame
    global screen  # Globální proměnná pro obrazovku
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Petris')  # Název okna

    while True:
        menu_result = show_menu()  # Zobrazení menu a získání výsledku

        if menu_result == "start":  # Spuštění hry
            game_instance = Game()  # Vytvoření instance hry
            game_instance.run()  # Spuštění hry
        elif menu_result == "quit":  # Ukončení programu
            pygame.quit()  # Ukončení Pygame
            sys.exit()  # Ukončení programu

# Třída pro obrazovku konce hry
class GameOverScreen:
    def __init__(self, score, high_score):
        self.score = score  # Aktuální skóre
        self.high_score = high_score  # Instance pro nejlepší skóre
        self.title_font = pygame.font.Font(None, 60)  # Font pro nadpis
        self.option_font = pygame.font.Font(None, 30)  # Font pro možnosti
        self.small_font = pygame.font.Font(None, 24)  # Malý font
        self.selected_option = 0  # Vybraná možnost (0 = skóre, 1 = znovu, 2 = menu)
        self.new_high_score = score > high_score.high_score  # Příznak nového rekordu
        self.animation_offset = 0  # Posun pro animaci
        self.last_animation_time = time.time()  # Čas poslední animace
        self.options = ["VIEW HIGH SCORES", "PLAY AGAIN", "MAIN MENU"]  # Možnosti

    # Metoda pro aktualizaci animace
    def update_animation(self):
        current_time = time.time()
        if current_time - self.last_animation_time > 0.05:
            self.animation_offset = (self.animation_offset + 1) % BLOCK_SIZE
            self.last_animation_time = current_time

    # Metoda pro vykreslení nadpisu
    def draw_title(self, screen):
        title = self.title_font.render("GAME OVER", True, Colors.RED)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        # Dekorační čára
        pygame.draw.line(
            screen, Colors.CYAN,
            (SCREEN_WIDTH // 2 - title.get_width() // 2 - 20, 80),
            (SCREEN_WIDTH // 2 + title.get_width() // 2 + 20, 80),
            3
        )

    # Metoda pro vykreslení informací o skóre
    def draw_score_info(self, screen):
        score_text = self.option_font.render(f"YOUR SCORE: {self.score}", True, Colors.WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 120))

        # Pokud je nové nejlepší skóre
        if self.new_high_score:
            new_high_text = self.small_font.render("NEW HIGH SCORE!", True, Colors.YELLOW)
            screen.blit(new_high_text, (SCREEN_WIDTH // 2 - new_high_text.get_width() // 2, 170))

    # Metoda pro vykreslení možností
    def draw_options(self, screen):
        for i, option in enumerate(self.options):
            # Poloprůhledné pozadí
            option_bg = pygame.Surface((220, 50), pygame.SRCALPHA)
            option_bg.fill((0, 0, 0, 180))
            screen.blit(option_bg, (SCREEN_WIDTH // 2 - 110, 220 + i * 60))

            # Zvýraznění vybrané možnosti
            if i == self.selected_option:
                pygame.draw.rect(
                    screen, Colors.YELLOW,
                    (SCREEN_WIDTH // 2 - 110, 220 + i * 60, 220, 50),
                    2
                )

            # Vykreslení textu možnosti
            text_color = Colors.YELLOW if i == self.selected_option else Colors.WHITE
            text = self.option_font.render(option, True, text_color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 225 + i * 60))

    # Hlavní metoda pro vykreslení
    def draw(self, screen):
        screen.fill(Colors.BLACK)  # Vyčištění obrazovky
        self.update_animation()  # Aktualizace animace
        self.draw_title(screen)  # Vykreslení nadpisu
        self.draw_score_info(screen)  # Vykreslení skóre
        self.draw_options(screen)  # Vykreslení možností

        # Vykreslení ovládání
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

    # Metoda pro zpracování vstupu
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Zavření okna
                return "quit"
            if event.type == pygame.KEYDOWN:  # Stisk klávesy
                if event.key == pygame.K_DOWN:  # Šipka dolů
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_UP:  # Šipka nahoru
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:  # Enter
                    if self.selected_option == 0:  # Zobrazení skóre
                        return "view_scores"
                    elif self.selected_option == 1:  # Nová hra
                        return "restart"
                    elif self.selected_option == 2:  # Návrat do menu
                        return "menu"
                elif event.key == pygame.K_ESCAPE:  # Escape
                    return "menu"
        return "game_over"  # Vrátíme stav

# Hlavní třída hry
class Game:
    def __init__(self):
        self.game_field = GameField()  # Vytvoření herního pole
        self.score = Score()  # Vytvoření skóre
        self.high_score = HighScore()  # Vytvoření nejlepšího skóre
        self.tetris = Tetris(self.game_field, self.score)  # Vytvoření Tetris
        self.clock = pygame.time.Clock()  # Vytvoření hodin
        self.base_speed = 0.5  # Základní rychlost pádu
        self.current_speed = self.base_speed  # Aktuální rychlost
        self.last_drop_time = time.time()  # Čas posledního pádu
        self.speed_increase_thresholds = [1000, 3000]  # Prahy pro zrychlení
        self.next_threshold_index = 0  # Index dalšího prahu

    # Metoda pro aktualizaci rychlosti hry
    def update_speed(self):
        # Kontrola, zda máme dosáhnout dalšího prahu
        if self.next_threshold_index < len(self.speed_increase_thresholds):
            next_threshold = self.speed_increase_thresholds[self.next_threshold_index]
            if self.score.score >= next_threshold:  # Pokud jsme dosáhli prahu
                # Zvýšení rychlosti (minimálně 0.1 sekundy)
                self.current_speed = max(0.1, self.current_speed * 0.7)
                self.next_threshold_index += 1

                # Výpočet dalšího prahu
                if self.next_threshold_index >= len(self.speed_increase_thresholds):
                    last_threshold = self.speed_increase_thresholds[-1]
                    increment = 2000 + (self.next_threshold_index - 2) * 1000
                    next_threshold = last_threshold + increment
                    self.speed_increase_thresholds.append(next_threshold)

    # Hlavní herní smyčka
    def run(self):
        while not self.tetris.game_over:  # Dokud hra neskončila
            current_time = time.time()
            self.clock.tick(60)  # Omezení na 60 FPS

            # Automatický pád kusu podle aktuální rychlosti
            if current_time - self.last_drop_time > self.current_speed:
                self.tetris.move_down()
                self.last_drop_time = current_time

            self.update_speed()  # Aktualizace rychlosti

            # Zpracování událostí
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Zavření okna
                    self.tetris.game_over = True
                if event.type == pygame.KEYDOWN:  # Stisk klávesy
                    if event.key == pygame.K_LEFT:  # Šipka vlevo
                        self.tetris.move_left()
                    if event.key == pygame.K_RIGHT:  # Šipka vpravo
                        self.tetris.move_right()
                    if event.key == pygame.K_DOWN:  # Šipka dolů
                        self.tetris.move_down()
                    if event.key == pygame.K_UP:  # Šipka nahoru
                        self.tetris.rotate_piece()
                    if event.key == pygame.K_SPACE:  # Mezerník - rychlý pád
                        self.tetris.drop()

            # Vykreslení
            screen.fill(Colors.BLACK)  # Vyčištění obrazovky
            draw_grid()  # Vykreslení mřížky
            self.game_field.draw()  # Vykreslení herního pole
            self.tetris.draw()  # Vykreslení aktuálního kusu
            self.score.draw()  # Vykreslení skóre
            self.high_score.draw()  # Vykreslení nejlepšího skóre

            pygame.display.flip()  # Aktualizace obrazovky

        # Uložení nejlepšího skóre a zobrazení obrazovky konce hry
        self.high_score.save_high_score(self.score.score)
        game_over_screen = GameOverScreen(self.score.score, self.high_score)

        while True:
            action = game_over_screen.handle_input()  # Zpracování vstupu

            if action == "quit":  # Ukončení
                pygame.quit()
                sys.exit()
            elif action == "view_scores":  # Zobrazení skóre
                self.show_high_scores()
            elif action == "restart":  # Nová hra
                return "restart"
            elif action == "menu":  # Návrat do menu
                return "menu"

            # Vykreslení
            screen.fill(Colors.BLACK)
            draw_grid()
            self.game_field.draw()
            self.tetris.draw()
            game_over_screen.draw(screen)
            pygame.display.flip()
            self.clock.tick(60)

    # Metoda pro zobrazení nejlepších skóre
    def show_high_scores(self):
        clock = pygame.time.Clock()
        showing_scores = True

        # Dočasná třída pro stylizované zobrazení skóre
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

                    # Třída pro dočasné menu při zobrazování skóre
                    def draw(self, screen):
                        self.update_animation()

                        # Poloprůhledné černé pozadí
                        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                        overlay.fill((0, 0, 0, 200))
                        screen.blit(overlay, (0, 0))

                        self.draw_background(screen)

                        # Vykreslení pozadí pro skóre
                        score_bg = pygame.Surface((250, 120), pygame.SRCALPHA)
                        score_bg.fill((0, 0, 0, 180))
                        screen.blit(score_bg, (SCREEN_WIDTH // 2 - 125, 150))

                        # Aktuální skóre hráče
                        current_text = self.score_font.render(f"Your Score: {self.current_score}", True, Colors.WHITE)
                        screen.blit(current_text, (SCREEN_WIDTH // 2 - current_text.get_width() // 2, 170))

                        # Nejlepší skóre
                        high_text = self.score_font.render(f"High Score: {self.high_score}", True, Colors.CYAN)
                        screen.blit(high_text, (SCREEN_WIDTH // 2 - high_text.get_width() // 2, 220))

                        # Návod pro pokračování
                        instructions = self.small_font.render("Press ENTER or ESC to continue", True, Colors.WHITE)
                        screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 350))

                # Vytvoření instance dočasného menu
                temp_menu = TempMenu(self.high_score.high_score, self.score.score)

                # Smyčka pro zobrazování skóre
                while showing_scores:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:  # Zavření okna
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN:  # Stisk klávesy
                            if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):  # Enter nebo Escape
                                showing_scores = False  # Ukončení zobrazování skóre

                    # Vykreslení herního pole v pozadí
                    screen.fill(Colors.BLACK)
                    draw_grid()
                    self.game_field.draw()
                    self.tetris.draw()

                    # Vykreslení overlay se skóre
                    temp_menu.draw(screen)

                    pygame.display.flip()
                    clock.tick(60)  # Omezení na 60 FPS

        # Upravená hlavní funkce pro podporu restartu hry
        def main():
            pygame.init()  # Inicializace Pygame
            global screen  # Globální proměnná pro obrazovku
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption('Petris')  # Název okna

            # Hlavní herní smyčka
            while True:
                menu_result = show_menu()  # Zobrazení hlavního menu

                if menu_result == "start":  # Spuštění hry
                    while True:  # Smyčka pro opakované spouštění hry
                        game_instance = Game()  # Vytvoření instance hry
                        result = game_instance.run()  # Spuštění hry
                        if result == "menu":  # Návrat do hlavního menu
                            break  # Ukončení vnitřní smyčky
                        # Pokud je výsledek "restart", smyčka pokračuje a vytvoří novou hru
                elif menu_result == "quit":  # Ukončení programu
                    pygame.quit()  # Ukončení Pygame
                    sys.exit()  # Ukončení programu

        # Spuštění programu, pokud je skript spuštěn přímo
        if __name__ == "__main__":
            main()