import multiprocessing
import random
import time
import math
import pygame
WIDTH = 800
HEIGHT = 600
RADIUS = 10


def random_place():
    """
    choosing a random place inside the screen
    :return: random x and y
    """
    return random.randint(RADIUS, WIDTH - RADIUS), random.randint(RADIUS, HEIGHT - RADIUS)


class Ball:

    def __init__(self, ball_id):
        """
        initializing the ball's values
        :param ball_id: the number of the ball
        :return:
        """
        self.id = ball_id
        self.numJumps = random.randint(5, 50)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def jump(self, check_q, print_q, stop):
        """
        process of a ball - sends a new random place to the checker every half second
        :param check_q: queue to the checker process
        :param print_q: queue to the print process
        :param stop: event that tells the ball to stop
        :return:
        """
        print_q.put(f"ball {self.id} started")
        while self.numJumps > 0 and not stop.is_set():
            x, y = random_place()
            check_q.put((self.id, x, y, self.color))
            self.numJumps -= 1
            time.sleep(0.5)
        check_q.put((self.id, None, None, None))   # the ball finished
        print_q.put(f"ball {self.id} ended")


def is_taken(ball_id, x, y, places):
    """
    checking if (x, y) is too close to another ball
    :param ball_id: the number of the ball
    :param x: the proposed x
    :param y: the proposed y
    :param places: the places of all the balls
    :return: True if the place is taken, otherwise False
    """
    taken = False
    for other_id, (ox, oy, color) in places.items():
        if other_id != ball_id and math.sqrt((x - ox) ** 2 + (y - oy) ** 2) < 2 * RADIUS:
            taken = True
    return taken


def checker(check_q, gui_q, print_q):
    """
    process that checks collisions - if the place is taken it chooses another place
    :param check_q: queue from the balls
    :param gui_q: queue to the main process
    :param print_q: queue to the print process
    :return:
    """
    print_q.put("checker started")
    places = {}
    while True:
        msg = check_q.get()
        if msg is None:
            break
        ball_id, x, y, color = msg
        if x is None:
            del places[ball_id]
        else:
            while is_taken(ball_id, x, y, places):
                x, y = random_place()
            places[ball_id] = (x, y, color)
        gui_q.put(dict(places))
    print_q.put("checker ended")


def printer(print_q):
    """
    the only process that prints
    :param print_q: queue of messages to print
    :return:
    """
    while True:
        msg = print_q.get()
        if msg is None:
            break
        print(msg)


if __name__ == "__main__":


    # getting the amount of balls from the user
    while True:
        numBalls = input("Enter amount of balls: ")
        if numBalls.isdigit() and numBalls != '0':
            numBalls = int(numBalls)
            break
        print("enter a valid number")

    # creating the queues for the communication between the processes
    print_q = multiprocessing.Queue()
    check_q = multiprocessing.Queue()
    gui_q = multiprocessing.Queue()
    stop = multiprocessing.Event()

    # starting the print process and the checker process
    print_p = multiprocessing.Process(target=printer, args=(print_q,))
    check_p = multiprocessing.Process(target=checker, args=(check_q, gui_q, print_q))
    print_p.start()
    check_p.start()
    print_q.put("main started")

    # starting a process for every ball
    balls = []
    for i in range(numBalls):
        p = multiprocessing.Process(target=Ball(i).jump, args=(check_q, print_q, stop))
        p.start()
        balls.append(p)

    # opening the window
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    places = {}
    count = 0
    running = True
    while running:
        # checking if the user closed the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # getting the newest places from the checker
        while not gui_q.empty():
            places = gui_q.get()

        # printing the amount of balls when it changes
        if len(places) != count:
            count = len(places)
            print_q.put(f"{count} balls on screen")

        # drawing the balls
        screen.fill((0, 0, 0))
        for (x, y, color) in places.values():
            pygame.draw.circle(screen, color, (x, y), RADIUS)
        pygame.display.flip()
        clock.tick(60)

        # stopping when all the balls finished
        if not any(p.is_alive() for p in balls) and count == 0:
            running = False

    pygame.quit()

    # stopping the ball processes
    stop.set()
    for p in balls:
        p.join()

    # stopping the checker process
    check_q.put(None)
    while check_p.is_alive():     # emptying the queue so the checker can finish
        while not gui_q.empty():
            gui_q.get()
        check_p.join(0.1)

    # stopping the print process (last)
    print_q.put("main ended")
    print_q.put(None)
    print_p.join()
