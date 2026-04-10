import pygame
import os
import random

pygame.init()

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dino Game Clean")

BASE_DIR = os.path.dirname(__file__)

def load(path):
    return pygame.image.load(os.path.join(BASE_DIR, path))

RUNNING = [load("Assets/Dino/DinoRun1.png"), load("Assets/Dino/DinoRun2.png")]
JUMPING = load("Assets/Dino/DinoJump.png")
DUCKING = [load("Assets/Dino/DinoDuck1.png"), load("Assets/Dino/DinoDuck2.png")]

SMALL_CACTUS = [load("Assets/Cactus/SmallCactus1.png"), load("Assets/Cactus/SmallCactus2.png"), load("Assets/Cactus/SmallCactus3.png")]
LARGE_CACTUS = [load("Assets/Cactus/LargeCactus1.png"), load("Assets/Cactus/LargeCactus2.png"), load("Assets/Cactus/LargeCactus3.png")]

BIRD = [load("Assets/Bird/Bird1.png"), load("Assets/Bird/Bird2.png")]
CLOUD = load("Assets/Other/Cloud.png")
BG = load("Assets/Other/Track.png")

POINT_SOUND = pygame.mixer.Sound(os.path.join(BASE_DIR, "Assets/sfx/100points.wav"))
GAMEOVER_SOUND = pygame.mixer.Sound(os.path.join(BASE_DIR, "Assets/sfx/lose.wav"))
JUMP_SOUND = pygame.mixer.Sound(os.path.join(BASE_DIR, "Assets/sfx/jump.wav"))

JUMP_SOUND.set_volume(0.4)
POINT_SOUND.set_volume(0.5)
GAMEOVER_SOUND.set_volume(0.6)

clock = pygame.time.Clock()
font = pygame.font.Font("Assets/PressStart2P-Regular.ttf", 20)

class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.image = RUNNING[0]
        self.rect = self.image.get_rect()
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL

        self.running = True
        self.jumping = False
        self.ducking = False

    def update(self, keys):
        if (keys[pygame.K_UP] or keys[pygame.K_SPACE]) and not self.jumping:
            JUMP_SOUND.play()
            self.running = False
            self.jumping = True
            self.ducking = False
        elif keys[pygame.K_DOWN] and not self.jumping:
            self.running = False
            self.ducking = True
        elif not self.jumping:
            self.running = True
            self.ducking = False

        if self.running:
            self.run()
        elif self.ducking:
            self.duck()
        elif self.jumping:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

    def run(self):
        self.image = RUNNING[self.step_index // 5]
        self.rect.y = self.Y_POS
        self.step_index += 1

    def duck(self):
        self.image = DUCKING[self.step_index // 5]
        self.rect.y = self.Y_DUCK
        self.step_index += 1

    def jump(self):
        self.image = JUMPING
        self.rect.y -= self.jump_vel * 4
        self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.jumping = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Obstacle:
    def __init__(self, images):
        self.images = images
        self.type = random.randint(0, len(images)-1)
        self.image = self.images[self.type]
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self, speed):
        self.rect.x -= speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class SmallCactus(Obstacle):
    def __init__(self):
        super().__init__(SMALL_CACTUS)
        self.rect.y = 325

class LargeCactus(Obstacle):
    def __init__(self):
        super().__init__(LARGE_CACTUS)
        self.rect.y = 300

class Bird(Obstacle):
    def __init__(self):
        super().__init__(BIRD)
        self.rect.y = 250
        self.index = 0

    def draw(self, screen):
        if self.index >= 10:
            self.index = 0
        screen.blit(self.images[self.index // 5], self.rect)
        self.index += 1

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self, speed):
        self.x -= speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

def main():
    player = Dinosaur()
    cloud = Cloud()
    obstacles = []

    game_speed = 20
    x_bg = 0
    y_bg = 380
    points = 0

    start_time = pygame.time.get_ticks()
    last_point_sound = 0
    points = 0
    running = True

    def score():
        nonlocal points,last_point_sound, game_speed
        current_time = pygame.time.get_ticks()
        points = (current_time - start_time) // 100
        milestone = points // 100
        if milestone > last_point_sound:
            game_speed += 3
            POINT_SOUND.play()
            last_point_sound = milestone
        text = font.render(f"Points: {points}", True, (0, 0, 0))
        SCREEN.blit(text, (850, 40))

    def background():
        nonlocal x_bg
        width = BG.get_width()
        SCREEN.blit(BG, (x_bg, y_bg))
        SCREEN.blit(BG, (x_bg + width, y_bg))
        if x_bg <= -width:
            x_bg = 0
        x_bg -= game_speed

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

        SCREEN.fill((255, 255, 255))
        keys = pygame.key.get_pressed()

        player.update(keys)
        player.draw(SCREEN)

        if len(obstacles) == 0:
            choice = random.randint(0, 2)
            if choice == 0:
                obstacles.append(SmallCactus())
            elif choice == 1:
                obstacles.append(LargeCactus())
            else:
                obstacles.append(Bird())

        for obstacle in list(obstacles):
            obstacle.update(game_speed)
            obstacle.draw(SCREEN)

            if obstacle.rect.x < -obstacle.rect.width:
                obstacles.remove(obstacle)

            if player.rect.colliderect(obstacle.rect):
                GAMEOVER_SOUND.play()
                return points

        background()
        cloud.update(game_speed)
        cloud.draw(SCREEN)

        score()

        clock.tick(30)
        pygame.display.update()

def menu():
    global last_score
    death_count = 0

    while True:
        SCREEN.fill((255, 255, 255))
        font_big = pygame.font.Font("Assets/PressStart2P-Regular.ttf", 30)

        if death_count == 0:
         text = "Press any key to start"
        else:
         text = f"Game Over! Score: {last_score}"

        label = font_big.render(text, True, (0, 0, 0))
        label_rect = label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(label, label_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                last_score = main()
                death_count += 1

last_score = 0
menu()
