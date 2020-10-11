import pygame as pygame
import startprgm
import numpy as np
import time
from ast import literal_eval
from route import *


if __name__ == '__main__':
    pygame.init()  # initializes the pygame object - Required to run the window on screen
    resolution = (420, 420)  # screen resolution
    flags = pygame.DOUBLEBUF
    ThingsToAppearOnScreen_Display = pygame.display.set_mode(resolution,flags)  # This sets the width and height of the screen that pops up
    m = startprgm.start(ThingsToAppearOnScreen_Display)
    flamability_rate = 0.6

    m.start_algorithm(m, 'Own', flamability_rate) # StrategyOne , StrategyTwo, Own

    window_display_status = True


    mls = m.get_all_rects()
    # Keeps the window running unless specifically you hit the x to close it
    while window_display_status:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                window_display_status = False
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in mls:
                    print(i)
                print(event.pos)