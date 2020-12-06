# TODO: Add add more complex angle change on ball collision with player

# ImportError thrown when pygame is not installed
try:
    import pygame
    import pygame.freetype

    pygame.init()
# When pygame is not installed, it will install it using pip
except ImportError:
    from sys import executable
    from subprocess import check_call

    check_call([executable, "-m", "pip", "install", "--user", "pygame==1.9.6"])
    import pygame
    import pygame.freetype

    pygame.init()

from math import cos, sin
from random import randint
from time import perf_counter

# Constants for colours
COLOUR_WHITE = (255, 255, 255)
COLOUR_GREY = (100, 100, 100)
COLOUR_BLACK = (0, 0, 0)

# Constants for the window
WIN_WIDTH = 800
WIN_HEIGHT = 600

# Constants for the background
LINE_X = int(WIN_WIDTH / 2)
SCORE_FONT_SIZE = 90  # Width = 0.5 * Size and Height = 0.75 * Size
SCORE_FONT_WIDTH = int(SCORE_FONT_SIZE * 0.5)
SCORE_FONT = pygame.freetype.SysFont("Courier New Bold", SCORE_FONT_SIZE)

# Constants for the players
PLAYER_WIDTH = 10
PLAYER_HEIGHT = 75
PLAYER_VELOCITY = 475
PLAYER_OFFSET = 10

# Constants for the ball
BALL_RADIUS = 5
BALL_VELOCITY = 450
PI = 3.14159  # Allows calculations using radians
BALL_CONE = int(PI / 12 * 100)  # ~0.26 radians, cone is ~0.51 radians wide (30 degrees)


class Player:
    def __init__(self, x, y):
        # Starting x,y for player1
        self.x = x
        self.y = y

    def draw(self, win) -> None:
        # Draws a player (surface, colour, (x, y, width, height))
        pygame.draw.rect(win, COLOUR_WHITE, (self.x, self.y, PLAYER_WIDTH, PLAYER_HEIGHT))

    def move_up(self, game) -> None:
        # When moving up would move player off the screen
        # Only move to top of screen
        if int(self.y - (PLAYER_VELOCITY * game.delta_time)) < 0:
            self.y = 0
        else:
            self.y -= int(PLAYER_VELOCITY * game.delta_time)

    def move_down(self, game) -> None:
        # When moving down would move player off the screen
        # Only move to bottom of screen
        if int(self.y + PLAYER_HEIGHT + (PLAYER_VELOCITY * game.delta_time)) > WIN_HEIGHT:
            self.y = WIN_HEIGHT - PLAYER_HEIGHT
        else:
            self.y += int(PLAYER_VELOCITY * game.delta_time)


class Ball:
    def __init__(self):
        # Starting x,y of the ball
        self.x = int(WIN_WIDTH / 2)
        self.y = int(WIN_HEIGHT / 2)

        # Chooses random starting angle for the ball
        # 1.2 radian (~70 degrees) cone to the left or right
        # https://www.desmos.com/calculator/4lj2bek1dg
        direction = randint(0, 1)
        if direction == 0:  # Left
            self.angle = randint(-BALL_CONE, BALL_CONE) / 100
        else:  # Right
            self.angle = randint(-BALL_CONE, BALL_CONE) / 100 + PI

    def draw(self, win) -> None:
        # Draws a white circle (surface, colour, pos, radius)
        pygame.draw.circle(win, COLOUR_WHITE, (self.x, self.y), BALL_RADIUS)

    def move(self, game, player1, player2) -> None:
        next_x = self.x + int(BALL_VELOCITY * cos(self.angle) * game.delta_time)
        next_y = self.y - int(BALL_VELOCITY * sin(self.angle) * game.delta_time)

        # Hitting top/bottom
        if next_y <= 0 or next_y >= WIN_HEIGHT:
            self.angle = -self.angle
            self.move(game, player1, player2)

        # Hitting player 1
        elif next_x <= player1.x + PLAYER_WIDTH and player1.y <= self.y <= player1.y + PLAYER_HEIGHT:
            self.angle = PI - self.angle
            self.move(game, player1, player2)

        # Hitting player 2
        elif next_x >= player2.x and player2.y <= self.y <= player2.y + PLAYER_HEIGHT:
            self.angle = PI - self.angle
            self.move(game, player1, player2)

        # Gone past player 1
        elif next_x <= 0:
            game.score[1] += 1
            game.run = False

        # Gone past player 2
        elif next_x >= WIN_WIDTH:
            game.score[0] += 1
            game.run = False

        # Normal movement
        else:
            self.x = next_x
            self.y = next_y


class Game:
    def __init__(self):
        self.run = True
        self.exit = False
        self.score = [0, 0]

        # Used to calculate delta time
        # (just declaration, values of no significance)
        self.delta_time, self.time_now, self.time_last = 0, 0, 0

    def game_loop(self, win, player1, player2, ball) -> None:
        # Measures the start of the first frame to calculate the first delta time
        self.time_last = perf_counter()

        while self.run:
            # Delta time used for consistent movement across frames
            self.get_delta_time()

            # The set delay between each tick/frame
            # Game has a frame time of 10ms so 100fps
            # 1000ms / 10ms = 100fps
            pygame.time.delay(10)

            # Gets list of events in that tick
            for event in pygame.event.get():
                # Ends game loop when QUIT event is triggered
                if event.type == pygame.QUIT:
                    self.exit = True
                    self.run = False

            # Gets a list of all the keys pressed in that tick
            keys = pygame.key.get_pressed()

            # Player 1 movement
            if keys[pygame.K_w]:
                player1.move_up(self)
            if keys[pygame.K_s]:
                player1.move_down(self)

            # Player 2 movement
            if keys[pygame.K_UP]:
                player2.move_up(self)
            if keys[pygame.K_DOWN]:
                player2.move_down(self)

            # Ball movement
            ball.move(self, player1, player2)

            # Draws a black background
            win.fill(COLOUR_BLACK)
            # Draws the centre line (surface, colour, pos, dimensions)
            pygame.draw.line(win, COLOUR_GREY, (LINE_X, 0), (LINE_X, WIN_HEIGHT))
            # Draws the score
            self.draw_score(win)
            # Draws the players
            player1.draw(win)
            player2.draw(win)
            # Draws the ball
            ball.draw(win)

            # Refreshes the display
            pygame.display.update()

    def get_delta_time(self) -> None:
        # Time current frame started
        self.time_now = perf_counter()

        # Delta time is time taken for last frame to process
        self.delta_time = (self.time_now - self.time_last)

        # Switches ready for next use
        self.time_last = self.time_now

    def draw_score(self, win) -> None:
        # Draws player 1's score (surface, pos, text, colour)
        SCORE_FONT.render_to(win, (int(WIN_WIDTH / 2) - SCORE_FONT_WIDTH * 2, 40), str(self.score[0]), COLOUR_GREY)
        # Draws player 2's score
        SCORE_FONT.render_to(win, (int(WIN_WIDTH / 2) + SCORE_FONT_WIDTH, 40), str(self.score[1]), COLOUR_GREY)

    def check_winner(self) -> bool:
        # When somebody has reached 5 points (won the game)
        if max(self.score[0], self.score[1]) == 5:
            return True
        else:
            # Enables the game loop to be run again
            self.run = True
            return False


def main() -> None:
    # Creates the game window
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    # Sets the name of the game window
    pygame.display.set_caption("Pong")

    # Creates objects for the game loop
    game = Game()

    # Loops until somebody has scored 5 points
    while not game.check_winner() and not game.exit:
        # Creates objects for both players (starting x, starting y)
        player1 = Player(PLAYER_OFFSET, int((WIN_HEIGHT - PLAYER_HEIGHT) / 2))
        player2 = Player(WIN_WIDTH - PLAYER_WIDTH - PLAYER_OFFSET, int((WIN_HEIGHT - PLAYER_HEIGHT) / 2))

        # Creates object for the ball
        ball = Ball()

        # Game loop will run until QUIT event
        game.game_loop(win, player1, player2, ball)
        print(game.score)


if __name__ == '__main__':
    main()
