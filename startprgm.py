import pygame as pygame
import numpy as np
#import random
#import alg
import time
from alg import *
from ast import literal_eval
from route import *
from sys import exit
from collections import deque

# To comment blocks of code press ctrl + /

class start:
    PYGAMEWIDTH = 300  # 600   # Do not change this: This is window sizing
    PYGAMEHEIGHT = 300  # Do not change this: This is window sizing
    row = 20  # row
    col = 20  # col
    box_width = 19
    box_height = 19
    maze_array = np.zeros((0, 0), dtype=int)
    screen = None

    list_of_all_rects = []

    def __init__(self, sc_py):
        self.font = pygame.font.SysFont('Arial', 12)
        self.screen = sc_py

# Functionality: Sets Value to border(top,bottom,left,right) to apply physicality - center for the real maze is
# still empty
    def get_arr(self):
        return self.maze_array

    # Functionality: Displays boxes on the screen
    def maze_generator(self,display, color, row_x , col_y):
        A = pygame.draw.rect(display, color, [col_y, row_x, self.box_width, self.box_height])   # row_x=row and col_y=col is the position where the box will be displayed
        #self.list_of_all_rects.append(A)
        self.list_of_all_rects.append([row_x,col_y])
        return A

    def rect_clicked(self,color, row_x , col_y):
        A = pygame.draw.rect(self.screen, color, [col_y, row_x, self.box_width, self.box_height])   # row_x=row and col_y=col is the position where the box will be displayed
        pygame.display.flip()
        return A

    def get_all_rects(self):
        return self.list_of_all_rects

    # def add_text_Box(self,screen):
    #     return screen.blit(self.font.render('1', True, (255, 255, 255)), (0,0,0))

    # Functionality: This function draws the maze on the pygame canvas/screen
    def draw_maze(self,screen, color):
        pl = 6
        for i in range(0,self.row):
            for j in range(0,self.col):
                if self.maze_array[i,j] == 8:
                    Grid_box_Object = self.maze_generator(screen, color, i * (self.box_width+1), j * (self.box_height+1))
                    # A = self.add_text_Box(screen)

                    text = self.font.render('1', True, (255, 255, 255))
                    screen.blit(text, Grid_box_Object.midtop)
                if self.maze_array[i, j] == 1:
                    self.maze_generator(screen, (255,255,255), i * (self.box_width + 1), j * (self.box_height + 1)) # +1 is to add a border shade to the cells

    # This is to color the moving routes
    def m_pattern(self, i, j, color, status):
        self.set_maze_pattern(self.screen, i, j, color, status)

    # Functionality: Sets the canvas color for cells and values for the array indices
    def set_maze_pattern(self, screen, i, j , color, status):
        if status == 'blocked':
            self.maze_array[i, j] = 8
            self.maze_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            #pygame.display.flip()
        if status == 'start':
            self.maze_array[i, j] = 1
            self.maze_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            #pygame.display.flip()
        else:
            self.maze_array[i, j] = 1
            self.maze_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            #pygame.display.flip()


    # This is to color the moving routes
    def player_movement(self, i, j, color, status):
        self.set_player_movement(self.screen, i, j, color, status)

    # Functionality: Sets the player movement values on the array
    def set_player_movement(self, screen, i, j , color, status):
        if status == 'blocked':
            self.maze_array[i, j] = 8
            self.maze_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            pygame.display.flip()
        if status == 'start':
            self.maze_array[i, j] = 1
            self.maze_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            pygame.display.flip()
        if status == 'fire':
            self.maze_array[i, j] = 1111
            self.maze_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            pygame.display.flip()
        if status == 'back track':
            self.maze_array[i, j] = 1
            self.maze_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            pygame.display.flip()
        if status == 'player':
            self.maze_array[i, j] = 2
            self.maze_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            pygame.display.flip()
        else:
            self.maze_array[i, j] = 4
            self.maze_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            pygame.display.flip()
        time.sleep(0.05) # PLAYER

    #Functionality: maps values to 2d maze
    def map_values(self):
        for i in range(1, self.row-1):
            for j in range(1, self.col-1):
                if self.maze_array[i][j]==0:
                    self.maze_array[i][j] = 1
                    #self.maze_generator(self.screen, (0, 128, 0), i * (self.box_width + 1), j * (self.box_height + 1))

    def generate_maze(self, obj):
        self.maze_array = np.full((self.row, self.col),int(8))
        self.map_values() # To map values on 2d array maze map
        self.draw_maze(self.screen , (187,187,187)) # Draws out the GUI from the stored array values


    def start_algorithm(self, obj, choice, flammability_rate):
        ThingsToAppearOnScreen_Display = self.screen
        self.maze_array = np.zeros((self.row, self.col), dtype=int)
        pygame.display.set_caption("MineSweeper", "MS")
        pygame.display.flip()
        a = mazeGen(ThingsToAppearOnScreen_Display, self.get_arr() , obj)   # MY OWN CLASS
        self.generate_maze(a)   # This function draws the maze
        pygame.display.flip()
