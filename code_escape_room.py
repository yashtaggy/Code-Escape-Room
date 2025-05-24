import pygame
import sys
import time
import os

# Print current directory for debugging
print(f"Current directory: {os.getcwd()}")
print(f"Running game from: {__file__}")

# Initialize pygame with debug info
print("Initializing pygame...")
pygame.init()
print("Pygame initialized successfully")

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
FONT_SIZE = 32
TIME_PER_ROOM = 120  # 2 minutes per room

class Room:
    def __init__(self, puzzle, answer, hint=""):
        self.puzzle = puzzle
        self.answer = answer
        self.hint = hint
        self.time_left = TIME_PER_ROOM
        self.start_time = None

    def start_timer(self):
        self.start_time = time.time()

    def update_time(self):
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.time_left = max(0, TIME_PER_ROOM - elapsed)

    def check_answer(self, player_answer):
        return player_answer.strip().lower() == self.answer.lower()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Code Escape Room")

        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.small_font = pygame.font.SysFont(None, FONT_SIZE // 2)

        # Game state
        self.current_room = 0
        self.game_over = False
        self.win = False
        self.feedback = ""
        self.feedback_timer = 0

        # Input box
        self.input_box = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT - 100, SCREEN_WIDTH // 2, 50)
        self.input_text = ""
        self.input_active = True

        # Create rooms with puzzles
        self.rooms = [
            Room("What data type would you use to store a collection of unique elements in Python?",
                 "set",
                 "It's not a list or dictionary..."),

            Room("What is the output of: print(2 + '2')?",
                 "typeerror",
                 "Can you add an integer and a string?"),

            Room("What keyword is used to define a function in Python?",
                 "def",
                 "It's a three-letter word...")
        ]

        # Start the timer for the first room
        self.rooms[self.current_room].start_timer()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return False  # Exit game on Enter if game is over
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.check_room_answer()
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    self.input_text += event.unicode

        return True

    def check_room_answer(self):
        current = self.rooms[self.current_room]
        if current.check_answer(self.input_text):
            self.feedback = "Correct! Moving to next room..."
            self.input_text = ""
            self.current_room += 1

            if self.current_room >= len(self.rooms):
                self.win = True
                self.game_over = True
            else:
                self.rooms[self.current_room].start_timer()
        else:
            self.feedback = "Incorrect answer. Try again!"

        self.feedback_timer = time.time()

    def update(self):
        # Update timer for current room
        if not self.game_over:
            current = self.rooms[self.current_room]
            current.update_time()

            # Check if time ran out
            if current.time_left <= 0:
                self.game_over = True

        # Clear feedback after 2 seconds
        if self.feedback and time.time() - self.feedback_timer > 2:
            self.feedback = ""

    def draw(self):
        self.screen.fill(WHITE)

        if self.game_over:
            if self.win:
                self.draw_win_screen()
            else:
                self.draw_game_over_screen()
        else:
            self.draw_room()

        pygame.display.flip()

    def draw_room(self):
        current = self.rooms[self.current_room]

        # Draw room number
        room_text = self.font.render(f"Room {self.current_room + 1}/{len(self.rooms)}", True, BLACK)
        self.screen.blit(room_text, (20, 20))

        # Draw timer
        minutes = int(current.time_left) // 60
        seconds = int(current.time_left) % 60
        timer_text = self.font.render(f"Time: {minutes:02d}:{seconds:02d}", True, BLACK)
        self.screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 20, 20))

        # Draw puzzle
        puzzle_text = self.font.render("Puzzle:", True, BLACK)
        self.screen.blit(puzzle_text, (SCREEN_WIDTH // 2 - puzzle_text.get_width() // 2, 100))

        # Split puzzle text into multiple lines if needed
        words = current.puzzle.split()
        lines = []
        line = ""
        for word in words:
            test_line = line + word + " "
            if self.small_font.render(test_line, True, BLACK).get_width() < SCREEN_WIDTH - 100:
                line = test_line
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)

        for i, line in enumerate(lines):
            puzzle_line = self.small_font.render(line, True, BLUE)
            self.screen.blit(puzzle_line, (SCREEN_WIDTH // 2 - puzzle_line.get_width() // 2, 150 + i * 30))

        # Draw hint
        hint_text = self.small_font.render(f"Hint: {current.hint}", True, GRAY)
        self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, 250))

        # Draw input box
        pygame.draw.rect(self.screen, BLACK, self.input_box, 2)
        input_surface = self.font.render(self.input_text, True, BLACK)
        self.screen.blit(input_surface, (self.input_box.x + 5, self.input_box.y + 5))

        # Draw instructions
        instructions = self.small_font.render("Type your answer and press Enter", True, BLACK)
        self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, self.input_box.y - 30))

        # Draw feedback
        if self.feedback:
            color = GREEN if "Correct" in self.feedback else RED
            feedback_text = self.font.render(self.feedback, True, color)
            self.screen.blit(feedback_text, (SCREEN_WIDTH // 2 - feedback_text.get_width() // 2, 350))

    def draw_game_over_screen(self):
        game_over_text = self.font.render("GAME OVER", True, RED)
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

        reason_text = self.small_font.render("You ran out of time!", True, BLACK)
        self.screen.blit(reason_text, (SCREEN_WIDTH // 2 - reason_text.get_width() // 2, SCREEN_HEIGHT // 2))

        exit_text = self.small_font.render("Press Enter to exit", True, BLACK)
        self.screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    def draw_win_screen(self):
        win_text = self.font.render("CONGRATULATIONS!", True, GREEN)
        self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

        message_text = self.small_font.render("You've escaped all the rooms!", True, BLACK)
        self.screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width() // 2, SCREEN_HEIGHT // 2))

        exit_text = self.small_font.render("Press Enter to exit", True, BLACK)
        self.screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)

        pygame.quit()
        sys.exit()

# Main entry point
if __name__ == "__main__":
    game = Game()
    game.run()
