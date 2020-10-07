from math import cos, sin

# ImportError thrown when pygame is not installed
try:
    import pygame
    pygame.init()
# When pygame is not installed, it will install it using pip
except ImportError:
    from sys import executable
    from subprocess import check_call
    check_call([executable, "-m", "pip", "install", "pygame"])
    import pygame
    pygame.init()

# Constants for the window
WIN_WIDTH = 800
WIN_HEIGHT = 600

# Constants for the background
SCREEN_COLOUR = (0, 0, 0)  # Black
LINE_COLOUR = (100, 100, 100)  # Grey
LINE_X = int(WIN_WIDTH / 2)

# Constants for the players
PLAYER_WIDTH = 10
PLAYER_HEIGHT = 75
PLAYER_VELOCITY = 10
PLAYER_COLOUR = (255, 255, 255)  # White

# Constants for the ball
BALL_RADIUS = 5
BALL_VELOCITY = 5
BALL_COLOUR = (255, 255, 255)  # White
PI = 3.14159


class Player:
    def __init__(self, x, y):
        # Starting x,y for player1
        self.x = x
        self.y = y

    def draw(self, win):
        # Draws a white rectangle at specified co-ords
        pygame.draw.rect(win, PLAYER_COLOUR, (self.x, self.y, PLAYER_WIDTH, PLAYER_HEIGHT))

    def move_up(self):
        # When moving up would move player off the screen
        # Only move to top of screen
        if self.y - PLAYER_VELOCITY < 0:
            self.y = 0
        else:
            self.y -= PLAYER_VELOCITY

    def move_down(self):
        # When moving down would move player off the screen
        # Only move to bottom of screen
        if self.y + PLAYER_HEIGHT + PLAYER_VELOCITY > WIN_HEIGHT:
            self.y = WIN_HEIGHT - PLAYER_HEIGHT
        else:
            self.y += PLAYER_VELOCITY


class Ball:
    def __init__(self):
        # Starting x,y of the ball
        self.x = int(WIN_WIDTH / 2)
        self.y = int(WIN_HEIGHT / 2)

    def draw(self, win):
        # Draws a white circle
        pygame.draw.circle(win, BALL_COLOUR, (self.x, self.y), BALL_RADIUS)

    # TODO: NOT WORKING!
    def move(self, angle):
        if PI/2 > angle >= 0:
            self.x += int(BALL_VELOCITY * cos(angle))
            self.y -= int(BALL_VELOCITY * sin(angle))
        elif PI > angle >= PI/2:
            self.x -= int(BALL_VELOCITY * cos(angle))
            self.y -= int(BALL_VELOCITY * sin(angle))
        elif 3*PI/2 > angle >= PI:
            self.x -= int(BALL_VELOCITY * cos(angle))
            self.y += int(BALL_VELOCITY * sin(angle))
        else:
            self.x += int(BALL_VELOCITY * cos(angle))
            self.y += int(BALL_VELOCITY * sin(angle))



def main():
    # Creates the game window
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    # Sets the name of the game window
    pygame.display.set_caption("Pong")

    # Creates objects for both players
    player1 = Player(10, 10)
    player2 = Player(WIN_WIDTH - PLAYER_WIDTH - 10, 10)

    # Creates objects for the ball
    ball = Ball()

    # Main game loop will run until QUIT event
    run = True
    while run:
        # The set delay between each tick/frame
        # Game has a frame time of 40ms so 25fps
        pygame.time.delay(40)

        # Gets list of events in that tick
        for event in pygame.event.get():
            # Ends game loop when QUIT event is triggered
            if event.type == pygame.QUIT:
                run = False

        # Gets a list of all the keys pressed in that tick
        keys = pygame.key.get_pressed()

        # Player 1 movement
        if keys[pygame.K_w]:
            player1.move_up()
        if keys[pygame.K_s]:
            player1.move_down()

        # Player 2 movement
        if keys[pygame.K_UP]:
            player2.move_up()
        if keys[pygame.K_DOWN]:
            player2.move_down()

        # Ball movement
        ball.move(3)
        # TODO: TRY DIFFERENT VALUES

        # Draws a black background
        win.fill(SCREEN_COLOUR)
        # Draws the centre line
        pygame.draw.line(win, LINE_COLOUR, (LINE_X, 0), (LINE_X, WIN_HEIGHT))
        # Draws the players
        player1.draw(win)
        player2.draw(win)
        # Draws the ball
        ball.draw(win)

        # Refreshes the display
        pygame.display.update()


if __name__ == '__main__':
    main()
