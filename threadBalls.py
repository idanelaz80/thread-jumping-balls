import threading
import pygame
import random
import time

WIDTH = 800
HEIGHT = 600

class Ball:

    def __init__(self):
        self.radius = 10  # רדיוס קבוע של 10 פיקסלים

        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(self.radius, HEIGHT - self.radius)
        self.numJumps = random.randint(1, 15)

        self.color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )

    def jump(self):
        while self.numJumps > 0:
            time.sleep(0.5)
            self.x = random.randint(self.radius, WIDTH - self.radius)
            self.y = random.randint(self.radius, HEIGHT - self.radius)
            self.numJumps -= 1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)


numBalls = int(input("Enter amount of balls: "))

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

balls = []
for i in range(numBalls):
    b = Ball()
    balls.append(b)
    t = threading.Thread(target=b.jump, daemon=True)
    t.start()
    print(f"{i+1} balls created")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for b in balls:
        if b.numJumps == 0:
            balls.remove(b)
            print(f"{len(balls)} balls remaining")

    screen.fill((0, 0, 0))
    for b in balls:
        b.draw(screen)
    pygame.display.flip()
    clock.tick(60)
    if len(balls) == 0:
        running = False

pygame.quit()