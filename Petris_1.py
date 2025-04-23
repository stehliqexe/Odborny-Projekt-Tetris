# Import potřebných knihoven
import pygame  # Hlavní knihovna pro vytvoření hry
import random  # Pro generování náhodných čísel (tvary kamenů)
import time  # Pro práci s časem (rychlost hry)
import sys  # Pro systémové funkce (ukončení programu)

# Inicializace pygame knihovny
pygame.init()

# Nastavení herního okna
SCREEN_WIDTH = 500  # Šířka okna v pixelech
SCREEN_HEIGHT = 600  # Výška okna v pixelech
BLOCK_SIZE = 30  # Velikost jednoho bloku (čtverečku) v pixelech
COLUMNS = 10  # Počet sloupců v herním poli
ROWS = 20  # Počet řádků v herním poli
GAME_WIDTH = COLUMNS * BLOCK_SIZE  # Šířka herní plochy (300px)
GAME_HEIGHT = ROWS * BLOCK_SIZE  # Výška herní plochy (600px)

# Vytvoření okna s danými rozměry
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


# Třída definující barvy používané ve hře
class Colors:
    WHITE = (255, 255, 255)  # Bílá
    CYAN = (0, 255, 255)  # Azurová
    BLUE = (0, 0, 255)  # Modrá
    ORANGE = (255, 165, 0)  # Oranžová
    YELLOW = (255, 255, 0)  # Žlutá
    GREEN = (0, 255, 0)  # Zelená
    PURPLE = (128, 0, 128)  # Fialová
    RED = (255, 0, 0)  # Červená
    BLACK = (0, 0, 0)  # Černá (prázdné políčko)
    DARK_PURPLE = (73, 8, 150)  # Tmavě fialová
    GRAY = (40, 40, 40)  # Šedá (mřížka)
    DARK_GRAY = (30, 30, 30)  # Tmavě šedá (pozadí)
    LIGHT_GRAY = (100, 100, 100)  # Světle šedá (okraje)


# Třída definující tvary tetramin (kamenů)
class Shapes:
    # Všechny možné tvary kamenů reprezentované maticemi
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
    SHAPES_COLORS = [Colors.CYAN, Colors.BLUE, Colors.ORANGE,
                     Colors.YELLOW, Colors.GREEN, Colors.PURPLE, Colors.RED]

    # Metoda pro získání náhodného tvaru a barvy
    @staticmethod
    def new_piece():
        shape = random.choice(Shapes.SHAPES)  # Náhodný výběr tvaru
        color = random.choice(Shapes.SHAPES_COLORS)  # Náhodný výběr barvy
        return shape, color


# Funkce pro vykreslení mřížky herního pole
def draw_grid():
    # Vykreslení svislých čar mřížky
    for x in range(0, GAME_WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, Colors.GRAY, (x, 0), (x, GAME_HEIGHT))
    # Vykreslení vodorovných čar mřížky
    for y in range(0, GAME_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, Colors.GRAY, (0, y), (GAME_WIDTH, y))


# Třída reprezentující herní pole
class GameField:
    def __init__(self):
        # Inicializace 2D pole reprezentujícího herní plochu
        self.board = []
        for i in range(ROWS):
            # Každý řádek obsahuje COLUMNS černých políček (prázdné)
            self.board.append([Colors.BLACK] * COLUMNS)

    # Metoda pro mazání plných řádků
    def clear_lines(self):
        full_lines = []  # Seznam indexů plných řádků

        # Prohledání všech řádků
        for i, row in enumerate(self.board):
            # Pokud řádek neobsahuje žádné černé políčko (je plný)
            if all(cell != Colors.BLACK for cell in row):
                full_lines.append(i)  # Přidání indexu do seznamu

        # Smazání plných řádků a přidání nových prázdných nahoře
        for i in full_lines:
            del self.board[i]  # Smazání řádku
            # Přidání nového prázdného řádku na začátek
            self.board.insert(0, [Colors.BLACK] * COLUMNS)

        return len(full_lines)  # Vrácení počtu smazaných řádků

    # Metoda pro vykreslení herního pole
    def draw(self):
        # Procházení všech políček herního pole
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell != Colors.BLACK:  # Pokud není políčko prázdné
                    # Vykreslení barevného čtverečku
                    pygame.draw.rect(
                        screen, cell,
                        (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    )


# Hlavní třída pro logiku hry Tetris
class Tetris:
    def __init__(self, game_field, score):
        self.game_field = game_field  # Reference na herní pole
        self.score = score  # Reference na objekt skóre
        self.current_piece = Shapes.new_piece()  # Aktuální padající kámen
        self.next_piece = Shapes.new_piece()  # Následující kámen
        # Počáteční pozice kamene (centrovaná horizontálně)
        self.x = COLUMNS // 2 - len(self.current_piece[0]) // 2
        self.y = 0  # Vertikální pozice kamene
        self.game_over = False  # Příznak konce hry

    # Metoda pro rotaci kamene
    def rotate_piece(self):
        shape, color = self.current_piece
        original_shape = shape  # Uložení původního tvaru pro případ kolize

        # Rotace tvaru (transpozice a obrácení řádků)
        new_shape = [list(row) for row in zip(*shape[::-1])]
        self.current_piece = (new_shape, color)  # Nastavení nového tvaru

        # Pokud po rotaci dojde ke kolizi, vrátit původní tvar
        if self.check_collision(0, 0):
            self.current_piece = (original_shape, color)

    # Metoda pro kontrolu kolizí
    def check_collision(self, offset_x, offset_y):
        shape, color = self.current_piece
        # Procházení všech bloků kamene
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:  # Pokud je blok obsazený
                    # Nové souřadnice po posunu
                    new_x = self.x + j + offset_x
                    new_y = self.y + i + offset_y

                    # Kontrola, zda je nová pozice mimo hrací pole
                    if new_x < 0 or new_x >= COLUMNS or new_y >= ROWS or new_y < 0:
                        return True
                    # Kontrola kolize s již umístěnými kameny
                    if new_y >= 0 and self.game_field.board[new_y][new_x] != Colors.BLACK:
                        return True
        return False  # Není kolize

    # Metoda pro umístění kamene na herní pole
    def place_piece(self):
        self.score.add_placement()  # Přidání bodů za umístění

        # Procházení všech bloků kamene
        for i, row in enumerate(self.current_piece[0]):
            for j, cell in enumerate(row):
                if cell:  # Pokud je blok obsazený
                    # Umístění barvy na herní pole
                    self.game_field.board[self.y + i][self.x + j] = self.current_piece[1]

        # Mazání plných řádků a přidání bodů
        lines_cleared = self.game_field.clear_lines()
        self.score.add_score(lines_cleared)

    # Metoda pro rychlý pád kamene (hard drop)
    def drop(self):
        # Posouvání kamene dolů, dokud není kolize
        while not self.check_collision(0, 1):
            self.y += 1

        self.place_piece()  # Umístění kamene

        # Nastavení následujícího kamene jako aktuálního
        self.current_piece = self.next_piece
        self.next_piece = Shapes.new_piece()  # Nový náhodný následující kámen
        # Reset pozice
        self.x = COLUMNS // 2 - len(self.current_piece[0]) // 2
        self.y = 0

        # Kontrola konce hry (nový kámen se nemůže umístit)
        if self.check_collision(0, 0):
            self.game_over = True

    # Metoda pro pohyb doleva
    def move_left(self):
        if not self.check_collision(-1, 0):  # Pokud není kolize vlevo
            self.x -= 1  # Posun doleva

    # Metoda pro pohyb doprava
    def move_right(self):
        if not self.check_collision(1, 0):  # Pokud není kolize vpravo
            self.x += 1  # Posun doprava

    # Metoda pro pohyb dolů (soft drop)
    def move_down(self):
        if not self.check_collision(0, 1):  # Pokud není kolize dole
            self.y += 1  # Posun dolů
        else:
            self.place_piece()  # Umístění kamene
            # Nastavení následujícího kamene jako aktuálního
            self.current_piece = self.next_piece
            self.next_piece = Shapes.new_piece()
            # Reset pozice
            self.x = COLUMNS // 2 - len(self.current_piece[0]) // 2
            self.y = 0
            # Kontrola konce hry
            if self.check_collision(0, 0):
                self.game_over = True

    # Metoda pro vykreslení aktuálního kamene
    def draw(self):
        # Procházení všech bloků kamene
        for i, row in enumerate(self.current_piece[0]):
            for j, cell in enumerate(row):
                if cell:  # Pokud je blok obsazený
                    # Vykreslení čtverečku
                    pygame.draw.rect(
                        screen, self.current_piece[1],
                        ((self.x + j) * BLOCK_SIZE, (self.y + i) * BLOCK_SIZE,
                         BLOCK_SIZE, BLOCK_SIZE)
                    )

    # Metoda pro vykreslení náhledu následujícího kamene
    def draw_next_piece(self):
        # Vykreslení textu "NEXT"
        font = pygame.font.Font(None, 36)
        next_text = font.render("NEXT:", True, Colors.WHITE)
        screen.blit(next_text, (GAME_WIDTH + 20, 30))

        # Vykreslení rámečku pro náhled
        preview_x = GAME_WIDTH + 50
        preview_y = 70
        box_size = 120
        pygame.draw.rect(screen, Colors.DARK_GRAY,
                         (preview_x - 10, preview_y - 10, box_size, box_size))

        # Výpočet velikosti kamene
        shape, color = self.next_piece
        shape_width = len(shape[0]) * BLOCK_SIZE
        shape_height = len(shape) * BLOCK_SIZE

        # Výpočet offsetu pro centrování kamene v náhledu
        offset_x = (box_size - shape_width) // 2
        offset_y = (box_size - shape_height) // 2

        # Vykreslení náhledu následujícího kamene
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        screen, color,
                        (preview_x + offset_x + j * BLOCK_SIZE,
                         preview_y + offset_y + i * BLOCK_SIZE,
                         BLOCK_SIZE, BLOCK_SIZE)
                    )


# Třída pro správu skóre
class Score:
    def __init__(self):
        self.score = 0  # Aktuální skóre
        self.streak = 0  # Počet po sobě jdoucích smazaných řádků
        self.level = 1  # Aktuální level
        self.lines_cleared = 0  # Celkový počet smazaných řádků

    # Metoda pro přidání bodů za umístění kamene
    def add_placement(self):
        self.score += 10  # 10 bodů za každé umístění

    # Metoda pro přidání bodů za smazané řádky
    def add_score(self, lines_cleared):
        if lines_cleared > 0:  # Pokud byly smazány nějaké řádky
            self.lines_cleared += lines_cleared  # Přidání k celkovému počtu
            # Výpočet levelu (každých 10 řádků = +1 level)
            self.level = self.lines_cleared // 10 + 1

            bonus = 0
            if self.streak > 0:  # Bonus za sérii
                bonus = 50 * lines_cleared

            # Bodování podle počtu smazaných řádků
            if lines_cleared == 1:
                self.score += 100 * self.level
            elif lines_cleared == 2:
                self.score += 300 * self.level
            elif lines_cleared == 3:
                self.score += 500 * self.level
            elif lines_cleared >= 4:
                self.score += 800 * self.level

            self.score += bonus  # Přidání bonusu
            self.streak += 1  # Zvýšení série
        else:
            self.streak = 0  # Reset série

    # Metoda pro vykreslení informací o skóre
    def draw(self):
        # Vykreslení pozadí panelu se skóre
        panel_x = GAME_WIDTH + 10
        panel_y = 180
        panel_width = SCREEN_WIDTH - GAME_WIDTH - 20
        pygame.draw.rect(screen, Colors.DARK_GRAY,
                         (panel_x, panel_y, panel_width, 180))

        # Vytvoření fontů
        font_large = pygame.font.Font(None, 36)  # Větší písmo
        font_small = pygame.font.Font(None, 28)  # Menší písmo

        # Vykreslení textu "SCORE"
        score_text = font_large.render(f"SCORE", True, Colors.WHITE)
        screen.blit(score_text, (panel_x + 20, panel_y + 10))

        # Vykreslení hodnoty skóre (formátované na 6 míst)
        score_value = font_large.render(f"{self.score:06d}", True, Colors.YELLOW)
        screen.blit(score_value, (panel_x + 20, panel_y + 40))

        # Vykreslení textu "MULTIPLIER" (násobič levelu)
        level_text = font_small.render(f"MULTIPLIER", True, Colors.WHITE)
        screen.blit(level_text, (panel_x + 20, panel_y + 90))

        # Vykreslení hodnoty levelu
        level_value = font_small.render(f"{self.level}", True, Colors.CYAN)
        screen.blit(level_value, (panel_x + 20, panel_y + 120))

        # Vykreslení textu "LINES" (smazané řádky)
        lines_text = font_small.render(f"LINES", True, Colors.WHITE)
        screen.blit(lines_text, (panel_x + 20, panel_y + 150))

        # Vykreslení počtu smazaných řádků
        lines_value = font_small.render(f"{self.lines_cleared}", True, Colors.GREEN)
        screen.blit(lines_value, (panel_x + 20, panel_y + 180))


# Třída pro správu nejvyššího skóre
class HighScore:
    def __init__(self):
        self.high_score = self.load_high_score()  # Načtení nejvyššího skóre

    # Metoda pro načtení nejvyššího skóre ze souboru
    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())  # Přečtení hodnoty ze souboru
        except:
            return 0  # Výchozí hodnota, pokud soubor neexistuje

    # Metoda pro uložení nejvyššího skóre do souboru
    def save_high_score(self, current_score):
        if current_score > self.high_score:  # Pokud je aktuální skóre vyšší
            self.high_score = current_score  # Aktualizace nejvyššího skóre
            with open("highscore.txt", "w") as f:
                f.write(str(self.high_score))  # Uložení do souboru

    # Metoda pro vykreslení nejvyššího skóre
    def draw(self):
        font = pygame.font.Font(None, 28)
        # Vykreslení textu "HIGH SCORE"
        high_score_text = font.render(f"HIGH SCORE:", True, Colors.WHITE)
        screen.blit(high_score_text, (GAME_WIDTH + 20, SCREEN_HEIGHT - 80))

        # Vykreslení hodnoty nejvyššího skóre
        high_score_value = font.render(f"{self.high_score:06d}", True, Colors.YELLOW)
        screen.blit(high_score_value, (GAME_WIDTH + 20, SCREEN_HEIGHT - 50))


# Třída pro hlavní menu hry
class Menu:
    def __init__(self):
        self.selected_option = 0  # Index vybrané možnosti
        self.options = ["START GAME", "HIGH SCORES", "QUIT"]  # Možnosti menu
        self.title_font = pygame.font.Font(None, 72)  # Písmo pro nadpis
        self.option_font = pygame.font.Font(None, 42)  # Písmo pro možnosti
        self.small_font = pygame.font.Font(None, 24)  # Malé písmo
        self.title_color = Colors.RED  # Barva nadpisu
        self.option_colors = [Colors.WHITE, Colors.WHITE, Colors.WHITE]  # Barvy možností
        self.show_high_scores = False  # Příznak zobrazení nejvyšších skóre
        self.high_score = HighScore()  # Instance pro nejvyšší skóre
        self.animation_offset = 0  # Posun pro animaci pozadí
        self.last_animation_time = time.time()  # Čas poslední animace

    # Metoda pro aktualizaci animace pozadí
    def update_animation(self):
        current_time = time.time()
        # Každých 0.05 sekundy posun animace
        if current_time - self.last_animation_time > 0.05:
            self.animation_offset = (self.animation_offset + 1) % BLOCK_SIZE
            self.last_animation_time = current_time

    # Metoda pro vykreslení nadpisu menu
    def draw_title(self, screen):
        # Vykreslení textu "PETRIS"
        title = self.title_font.render("PETRIS", True, self.title_color)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        # Vykreslení dekorativní čáry pod nadpisem
        pygame.draw.line(
            screen, Colors.CYAN,
            (SCREEN_WIDTH // 2 - title.get_width() // 2 - 20, 80),
            (SCREEN_WIDTH // 2 + title.get_width() // 2 + 20, 80),
            3
        )

    # Metoda pro vykreslení animovaného pozadí
    def draw_background(self, screen):
        # Vykreslení svislých čar pozadí
        for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
            pygame.draw.line(
                screen, Colors.DARK_PURPLE,
                (x + self.animation_offset, 0),
                (x + self.animation_offset, SCREEN_HEIGHT),
                1
            )
        # Vykreslení vodorovných čar pozadí
        for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
            pygame.draw.line(
                screen, Colors.DARK_PURPLE,
                (0, y + self.animation_offset),
                (SCREEN_WIDTH, y + self.animation_offset),
                1
            )

    # Metoda pro vykreslení možností menu
    def draw_options(self, screen):
        # Procházení všech možností menu
        for i, option in enumerate(self.options):
            # Vytvoření poloprůhledného pozadí pro možnost
            option_bg = pygame.Surface((220, 50), pygame.SRCALPHA)
            option_bg.fill((0, 0, 0, 180))  # Poloprůhledná černá
            screen.blit(option_bg, (SCREEN_WIDTH // 2 - 110, 185 + i * 60))

            # Pokud je možnost vybraná, vykreslí se žlutý rámeček
            if i == self.selected_option:
                pygame.draw.rect(
                    screen, Colors.YELLOW,
                    (SCREEN_WIDTH // 2 - 110, 185 + i * 60, 220, 50),
                    2
                )

            # Nastavení barvy textu (žlutá pro vybranou, bílá pro ostatní)
            text_color = Colors.YELLOW if i == self.selected_option else Colors.WHITE
            text = self.option_font.render(option, True, text_color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 190 + i * 60))

    # Metoda pro vykreslení obrazovky s nejvyššími skóre
    def draw_high_scores(self, screen):
        # Vytvoření poloprůhledného tmavého pozadí
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Vykreslení nadpisu "HIGH SCORES"
        title = self.option_font.render("HIGH SCORES", True, Colors.YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        # Vykreslení hodnoty nejvyššího skóre
        score_text = self.title_font.render(str(self.high_score.high_score), True, Colors.CYAN)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 220))

        # Vykreslení dekorativního rámečku
        pygame.draw.rect(
            screen, Colors.PURPLE,
            (SCREEN_WIDTH // 2 - 150, 130, 300, 200),
            3
        )

        # Vykreslení instrukce pro návrat
        back_text = self.small_font.render("Press ESC to return", True, Colors.WHITE)
        screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 350))

    # Hlavní metoda pro vykreslení menu
    def draw(self, screen):
        screen.fill(Colors.BLACK)  # Vyplnění černou barvou
        self.update_animation()  # Aktualizace animace
        self.draw_background(screen)  # Vykreslení pozadí
        self.draw_title(screen)  # Vykreslení nadpisu

        if not self.show_high_scores:  # Pokud se nezobrazují skóre
            self.draw_options(screen)  # Vykreslení možností menu

            # Vykreslení ovládání
            controls = [
                "CONTROLS:",
                "Key_UP, Key_DOWN - Navigate",
                "Key_LEFT, Key_RIGHT - Move",
                "ENTER - Select",
                "ESC - Back"
            ]
            # Vykreslení jednotlivých řádků ovládání
            for i, line in enumerate(controls):
                color = Colors.CYAN if i == 0 else Colors.WHITE
                text = self.small_font.render(line, True, color)
                screen.blit(text, (20, SCREEN_HEIGHT - 100 + i * 20))
        else:
            self.draw_high_scores(screen)  # Vykreslení nejvyšších skóre

    # Metoda pro zpracování vstupu v menu
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Pokud uživatel zavře okno
                return "quit"

            if event.type == pygame.KEYDOWN:  # Stisknutí klávesy
                if not self.show_high_scores:  # Pokud není zobrazeno skóre
                    if event.key == pygame.K_DOWN:  # Šipka dolů
                        # Posun výběru dolů (cyklické)
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                    elif event.key == pygame.K_UP:  # Šipka nahoru
                        # Posun výběru nahoru (cyklické)
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:  # Enter
                        if self.selected_option == 0:  # Start hry
                            return "start"
                        elif self.selected_option == 1:  # Nejvyšší skóre
                            self.show_high_scores = True
                        elif self.selected_option == 2:  # Konec
                            return "quit"
                else:
                    if event.key == pygame.K_ESCAPE:  # ESC pro návrat
                        self.show_high_scores = False

        return "menu"  # Výchozí návratová hodnota


# Funkce pro zobrazení a obsluhu menu
def show_menu():
    menu = Menu()  # Vytvoření instance menu
    clock = pygame.time.Clock()  # Vytvoření hodin pro řízení FPS

    while True:
        result = menu.handle_input()  # Zpracování vstupu
        if result != "menu":  # Pokud uživatel něco vybral
            return result

        menu.draw(screen)  # Vykreslení menu
        pygame.display.flip()  # Aktualizace obrazovky
        clock.tick(60)  # Omezení na 60 FPS


# Třída pro obrazovku konce hry
class GameOverScreen:
    def __init__(self, score, high_score):
        self.score = score  # Aktuální skóre
        self.high_score = high_score  # Instance pro nejvyšší skóre
        self.title_font = pygame.font.Font(None, 60)  # Písmo pro nadpis
        self.option_font = pygame.font.Font(None, 30)  # Písmo pro možnosti
        self.small_font = pygame.font.Font(None, 24)  # Malé písmo
        self.selected_option = 0  # Vybraná možnost
        self.new_high_score = score > high_score.high_score  # Nový rekord?
        self.animation_offset = 0  # Posun pro animaci
        self.last_animation_time = time.time()  # Čas poslední animace
        self.options = ["VIEW HIGH SCORES", "PLAY AGAIN", "MAIN MENU"]  # Možnosti

    # Metoda pro aktualizaci animace
    def update_animation(self):
        current_time = time.time()
        # Každých 0.05 sekundy posun animace
        if current_time - self.last_animation_time > 0.05:
            self.animation_offset = (self.animation_offset + 1) % BLOCK_SIZE
            self.last_animation_time = current_time

    # Metoda pro vykreslení nadpisu
    def draw_title(self, screen):
        # Vykreslení textu "GAME OVER"
        title = self.title_font.render("GAME OVER", True, Colors.RED)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        # Vykreslení dekorativní čáry pod nadpisem
        pygame.draw.line(
            screen, Colors.CYAN,
            (SCREEN_WIDTH // 2 - title.get_width() // 2 - 20, 80),
            (SCREEN_WIDTH // 2 + title.get_width() // 2 + 20, 80),
            3
        )

    # Metoda pro vykreslení informací o skóre
    def draw_score_info(self, screen):
        # Vykreslení textu s aktuálním skóre
        score_text = self.option_font.render(f"YOUR SCORE: {self.score}", True, Colors.WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 120))

        # Pokud je dosaženo nového rekordu
        if self.new_high_score:
            new_high_text = self.small_font.render("NEW HIGH SCORE!", True, Colors.YELLOW)
            screen.blit(new_high_text, (SCREEN_WIDTH // 2 - new_high_text.get_width() // 2, 170))

    # Metoda pro vykreslení možností
    def draw_options(self, screen):
        # Procházení všech možností
        for i, option in enumerate(self.options):
            # Vytvoření poloprůhledného pozadí pro možnost
            option_bg = pygame.Surface((220, 50), pygame.SRCALPHA)
            option_bg.fill((0, 0, 0, 180))
            screen.blit(option_bg, (SCREEN_WIDTH // 2 - 110, 220 + i * 60))

            # Pokud je možnost vybraná, vykreslí se žlutý rámeček
            if i == self.selected_option:
                pygame.draw.rect(
                    screen, Colors.YELLOW,
                    (SCREEN_WIDTH // 2 - 110, 220 + i * 60, 220, 50),
                    2
                )

            # Nastavení barvy textu (žlutá pro vybranou, bílá pro ostatní)
            text_color = Colors.YELLOW if i == self.selected_option else Colors.WHITE
            text = self.option_font.render(option, True, text_color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 225 + i * 60))

    # Hlavní metoda pro vykreslení
    def draw(self, screen):
        screen.fill(Colors.BLACK)  # Vyplnění černou barvou
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
        # Vykreslení jednotlivých řádků ovládání
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
                    # Posun výběru dolů (cyklické)
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_UP:  # Šipka nahoru
                    # Posun výběru nahoru (cyklické)
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:  # Enter
                    if self.selected_option == 0:  # Zobrazit skóre
                        return "view_scores"
                    elif self.selected_option == 1:  # Hrát znovu
                        return "restart"
                    elif self.selected_option == 2:  # Hlavní menu
                        return "menu"
                elif event.key == pygame.K_ESCAPE:  # ESC
                    return "menu"
        return "game_over"  # Výchozí návratová hodnota

class Game:
    def __init__(self):
        self.game_field = GameField()
        self.score = Score()
        self.high_score = HighScore()
        self.tetris = Tetris(self.game_field, self.score)
        self.clock = pygame.time.Clock()
        self.base_speed = 0.5  # Initial delay in seconds between automatic drops
        self.current_speed = self.base_speed
        self.last_drop_time = time.time()
        self.speed_increase_thresholds = [1000, 3000]  # Initial thresholds
        self.next_threshold_index = 0

    def update_speed(self):
        # Update game speed based on score thresholds
        if self.next_threshold_index < len(self.speed_increase_thresholds):
            next_threshold = self.speed_increase_thresholds[self.next_threshold_index]
            if self.score.score >= next_threshold:
                # Increase speed by reducing the delay (minimum of 0.1 seconds)
                self.current_speed = max(0.1, self.current_speed * 0.7)  # 30% faster each time
                self.next_threshold_index += 1

                # Calculate next threshold (1000, 3000, 6000, 10000, 15000, etc.)
                if self.next_threshold_index >= len(self.speed_increase_thresholds):
                    last_threshold = self.speed_increase_thresholds[-1]
                    increment = 2000 + (self.next_threshold_index - 2) * 1000
                    next_threshold = last_threshold + increment
                    self.speed_increase_thresholds.append(next_threshold)

    def run(self):
        while not self.tetris.game_over:
            current_time = time.time()
            self.clock.tick(60)  # Keep a consistent frame rate

            # Handle automatic dropping based on current speed
            if current_time - self.last_drop_time > self.current_speed:
                self.tetris.move_down()
                self.last_drop_time = current_time

            self.update_speed()  # Check if we need to increase speed

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

            # Draw everything
            screen.fill(Colors.BLACK)

            # Draw game area with a border
            pygame.draw.rect(screen, Colors.LIGHT_GRAY, (0, 0, GAME_WIDTH, GAME_HEIGHT), 1)
            draw_grid()
            self.game_field.draw()
            self.tetris.draw()

            # Draw side panel
            pygame.draw.rect(screen, Colors.DARK_GRAY, (GAME_WIDTH, 0, SCREEN_WIDTH - GAME_WIDTH, SCREEN_HEIGHT))

            # Draw game info
            self.tetris.draw_next_piece()
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

def main():
    pygame.display.set_caption('Petris')

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