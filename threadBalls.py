import threading
import pygame
import random
import time

WIDTH = 800
HEIGHT = 600

class Ball:

    def __init__(self):
        """
        initializing the ball's values
        """
        self.radius = 10  # רדיוס קבוע של 10 פיקסלים

        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(self.radius, HEIGHT - self.radius)
        self.numJumps = random.randint(5, 50)

        self.color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )

    def jump(self):
        """
        moving the ball from a random place to another while decreasing the number of jumps left
        :return:
        """
        while self.numJumps > 0:
            time.sleep(0.5)
            self.x = random.randint(self.radius, WIDTH - self.radius)
            self.y = random.randint(self.radius, HEIGHT - self.radius)
            self.numJumps -= 1

    def draw(self, surface):
        """
        drawing the ball
        :param surface: the screen
        :return:
        """
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)

while True:
    numBalls = input("Enter amount of balls: ")
    if numBalls.isdigit() and numBalls != '0':
        numBalls = int(numBalls)
        break
    else:
        print("enter a valid number")

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