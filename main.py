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

from math import cos, sin, atan
from random import randint, uniform
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
FPS_FONT_SIZE = 20
FPS_FONT_Y = 2
FPS_FONT_X = 3
FPS_FONT = pygame.freetype.SysFont("Courier New Bold", FPS_FONT_SIZE)

# Constants for the players
PLAYER_WIDTH = 10
PLAYER_HEIGHT = 75
PLAYER_VELOCITY = 475
PLAYER_OFFSET = 30

# Constants for the ball
BALL_RADIUS = 5
BALL_VELOCITY = 450
BALL_ANGLE_MAX = atan(225/800)  # ~0.27 rad
BALL_ANGLE_MIN = atan(40/800)  # ~0.05 rad
PI = 3.14159  # Allows calculations using radians


class Player:
    def __init__(self, x, y):
        # Starting x,y for player1
        self.x = x
        self.y = y

    def draw(self, win) -> None:
        # Draws a player (surface, colour, (x, y, width, height))
        pygame.draw.rect(win, COLOUR_WHITE, (int(self.x), int(self.y), PLAYER_WIDTH, PLAYER_HEIGHT))

    def move_up(self, game) -> None:
        # When moving up would move player off the screen
        # Only move to top of screen
        if int(self.y - PLAYER_VELOCITY * game.delta_time) < 0:
            self.y = 0
        else:
            self.y -= (PLAYER_VELOCITY * game.delta_time)

    def move_down(self, game) -> None:
        # When moving down would move player off the screen
        # Only move to bottom of screen
        if (self.y + PLAYER_HEIGHT + PLAYER_VELOCITY * game.delta_time) > WIN_HEIGHT:
            self.y = WIN_HEIGHT - PLAYER_HEIGHT
        else:
            self.y += (PLAYER_VELOCITY * game.delta_time)


class Ball:
    def __init__(self):
        # Starting x,y of the ball
        self.x = int(WIN_WIDTH / 2)
        self.y = int(WIN_HEIGHT / 2)

        self.angle = self.generate_start_angle()

    def draw(self, win) -> None:
        # Draws a white circle (surface, colour, pos, radius)
        pygame.draw.circle(win, COLOUR_WHITE, (int(self.x), int(self.y)), BALL_RADIUS)

    def move(self, game, player1, player2) -> None:
        next_x = self.x + (BALL_VELOCITY * cos(self.angle) * game.delta_time)
        next_y = self.y - (BALL_VELOCITY * sin(self.angle) * game.delta_time)

        # Hitting top/bottom
        if next_y <= 0 or next_y >= WIN_HEIGHT:
            self.angle = -self.angle
            self.move(game, player1, player2)

        # Hitting player 1
        elif player1.x <= next_x <= player1.x + PLAYER_WIDTH and player1.y <= self.y <= player1.y + PLAYER_HEIGHT:
            self.x = player1.x + PLAYER_WIDTH
            self.angle = PI - self.angle
            self.move(game, player1, player2)

        # Hitting player 2
        elif player2.x <= next_x <= player2.x + PLAYER_WIDTH and player2.y <= self.y <= player2.y + PLAYER_HEIGHT:
            self.x = player2.x
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

    @staticmethod
    def generate_start_angle() -> float:
        # Randomly chooses an angle in the interval [BALL_ANGLE_MAX, BALL_ANGLE_MIN]
        # These constants were defined using the method linked below
        # https://www.desmos.com/calculator/1hmuyvwcvv

        # Quadrants are labeled 1-4 going anticlockwise starting in (+, +)
        quadrant = randint(1, 4)

        if quadrant == 1:
            return uniform(BALL_ANGLE_MIN, BALL_ANGLE_MAX)
        elif quadrant == 2:
            return PI - uniform(BALL_ANGLE_MIN, BALL_ANGLE_MAX)
        elif quadrant == 3:
            return PI + uniform(BALL_ANGLE_MIN, BALL_ANGLE_MAX)
        else:
            return -uniform(BALL_ANGLE_MIN, BALL_ANGLE_MAX)


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

        # Initiates game's clock for measuring fps
        game_clock = pygame.time.Clock()

        while self.run:
            # Sets max frame rate
            # 1s / 0.015s = 66fps
            pygame.time.delay(15)
            game_clock.tick()

            # Delta time used for consistent movement across frames
            # ~0.015s (the set delay for each frame)
            self.get_delta_time()

            # Skips ticks with exceptionally high delta times (>4x expected)
            # Typically caused by moving the window
            if self.delta_time > 0.06:
                continue

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
            # Draws the fps
            self.draw_fps(win, game_clock)
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

    @staticmethod
    def draw_fps(win, clock) -> None:
        # Gets the fps, casts to int and renders to the screen
        FPS_FONT.render_to(win, (FPS_FONT_X, FPS_FONT_Y), str(int(clock.get_fps())).zfill(3) + "fps", COLOUR_GREY)


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
        player1 = Player(PLAYER_OFFSET, ((WIN_HEIGHT - PLAYER_HEIGHT) / 2))
        player2 = Player((WIN_WIDTH - PLAYER_WIDTH - PLAYER_OFFSET), ((WIN_HEIGHT - PLAYER_HEIGHT) / 2))

        # Creates object for the ball
        ball = Ball()

        # Game loop will run until QUIT event
        game.game_loop(win, player1, player2, ball)


if __name__ == '__main__':
    main()
