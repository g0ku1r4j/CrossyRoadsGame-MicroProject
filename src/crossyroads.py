import pygame
import random
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # Temporary folder used by PyInstaller
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# initialize pygame module
pygame.init()

# screen dimensions
WIDTH = 800
HEIGHT = 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Crossy Road Game")

# colors
WHITE = (255, 255, 255)
LIGHT_GREEN = (144, 238, 144)  # softer green for a more appealing look
DARK_GRAY = (50, 50, 50)  # road color
RED = (255, 0, 0)

# game clock
clock = pygame.time.Clock()

# player settings
PLAYER_SIZE = 40
PLAYER_SPEED = 10

# load assets with transparency
player_image = pygame.image.load(resource_path("assets/player.png")).convert_alpha()
player_image = pygame.transform.scale(player_image, (PLAYER_SIZE, PLAYER_SIZE))

# load food images (acting as cars) - unhealthy food
bad_food_images = [pygame.image.load(resource_path("assets/doritos.png")).convert_alpha(),
                   pygame.image.load(resource_path("assets/oreo.png")).convert_alpha(),
                   pygame.image.load(resource_path("assets/burger.png")).convert_alpha()]
# load food images (acting as cars) - healthy food
good_food_images = [pygame.image.load(resource_path("assets/strawberry.png")).convert_alpha(),
                     pygame.image.load(resource_path("assets/lemon.png")).convert_alpha(),
                     pygame.image.load(resource_path("assets/cheese.png")).convert_alpha()]

# resize food images to fit the correct dimensions
bad_food_images = [pygame.transform.scale(img, (40, 50)) for img in bad_food_images]
good_food_images = [pygame.transform.scale(img, (40, 50)) for img in good_food_images]

# font
font = pygame.font.SysFont(None, 40)

'''
Player class uses Sprite - Sprite makes it easier to handle objects on the screen 
that needs to collide/move on the screen. So Player is now a child class of the 
Sprite class in pygame
'''
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect() # set the image as a rectangle
        self.rect.center = (WIDTH // 2, HEIGHT - 50)

    def update(self, keys):
        # move left if LEFT key is pressed and player is not at the left edge
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        # move right if RIGHT key is pressed and player is not at the right edge
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += PLAYER_SPEED
        # same for top - TOP key
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= PLAYER_SPEED
        # same for bottom - BOTTOM key
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += PLAYER_SPEED

# Moving obstacle class (cars)
class Car(pygame.sprite.Sprite):
    def __init__(self, good=True, y_position=None):
        super().__init__()
        # choose a random image based on whether it's a good or bad food
        self.image = random.choice(good_food_images if good else bad_food_images)
        self.rect = self.image.get_rect()
        # set the vertical position (y) — either passed or chosen randomly
        self.rect.y = (y_position) if y_position else random.randint(0, HEIGHT - self.rect.height)
        # start the object off-screen: either from left or right: right, start at WIDTH (screen edge) ; left, start at -width (just off screen)
        self.rect.x = -self.rect.width if random.choice([True, False]) else WIDTH
        # speed is randomly set to a value between 5 and 10
        self.speed = random.randint(5, 10) * (-1 if self.rect.x == WIDTH else 1)
        self.good = good

    def update(self):
        self.rect.x += self.speed
        # move horizontally based on speed
        if self.rect.right < 0 or self.rect.left > WIDTH:
            # if it's completely off-screen, send it back to the opposite side to re-enter
            self.rect.x = -self.rect.width if self.speed > 0 else WIDTH

# main game function
def game_loop():
    player = Player()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    # define y-positions for road lanes
    road_lanes = [HEIGHT // 5 + 30, 2 * HEIGHT // 5 + 30, 3 * HEIGHT // 5 + 30, 4 * HEIGHT // 5 + 30]  # move lanes 10px down
    
    # spawn moving obstacles (cars) - creating group for moving objects
    cars = pygame.sprite.Group()
    for lane in road_lanes:
        for _ in range(2):  # two cars per lane
            cars.add(Car(good=random.choice([True, False]), y_position=lane))
    all_sprites.add(cars)

    # initialise score
    score = 0
    game_over = False

    while not game_over:
        SCREEN.fill(LIGHT_GREEN)
        
        # draw multiple road lanes
        for lane in road_lanes:
            pygame.draw.rect(SCREEN, DARK_GRAY, (0, lane - 20, WIDTH, 40))
        
        # check for events - closing the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
        
        keys = pygame.key.get_pressed()
        player.update(keys)
        cars.update()
        
        # collision detection
        for car in pygame.sprite.spritecollide(player, cars, False):
            if car.good:
                score += 5
                car.kill()  # remove good food once collected
            else:
                game_over = True
        
        # display score
        score_text = font.render(f"Score: {score}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))

        # check if player crossed the road
        if player.rect.top <= 0:
            player.rect.center = (WIDTH // 2, HEIGHT - 50)  # reset player position

        # draw all sprites
        all_sprites.draw(SCREEN)

        pygame.display.update()

        # control the game speed
        clock.tick(30)

    # display Game Over message with score
    SCREEN.fill(WHITE)
    game_over_text = font.render(f"Game Over - Score: {score}", True, RED)
    SCREEN.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2 - 20))
    pygame.display.update()
    pygame.time.wait(2000)  # wait for 2 seconds before quitting the game
    pygame.quit()

# run the game loop
game_loop()