import pygame as pygame
import numpy as np
#import random
#import alg
import time
from ast import literal_eval
from route import *
from sys import exit
from collections import deque

# To comment blocks of code press ctrl + /
from mswp.agent import agnt


class start:
    PYGAMEWIDTH = 300  # 600   # Do not change this: This is window sizing
    PYGAMEHEIGHT = 300  # Do not change this: This is window sizing
    row = 10  # row
    col = 10  # col
    box_width = 19
    box_height = 19
    board_array = np.zeros((0, 0), dtype=int)
    screen = None

    list_of_all_rects = []

    recent_clicked_rect_x = None
    recent_clicked_rect_y = None

    agent_class = None


    def __init__(self, sc_py):
        self.font = pygame.font.SysFont('Arial', 12)
        self.screen = sc_py

# Functionality: Sets Value to border(top,bottom,left,right) to apply physicality - center for the real maze is
# still empty

    # def init_agent_class(self, obj):
    #

    def get_arr(self):
        return self.board_array

    # Functionality: Displays boxes on the screen
    def board_generator(self,display, color, row_x , col_y):
        A = pygame.draw.rect(display, color, [col_y, row_x, self.box_width, self.box_height])   # row_x=row and col_y=col is the position where the box will be displayed
        self.list_of_all_rects.append([row_x,col_y])
        return A


    # EVERYTHING GOES HERE WHEN A CLICK IS DONES
    def perform_action_clicked(self,obj,i,j):
        obj = self.agent_class
        # we are dividing by 20 due do GUI dimension for pycharm - its a scaling issue in GUI
        index_board_i= int(i/20)
        index_board_j= int(j/20)
        print("index: " , index_board_i , ",", index_board_j)
        arr = obj.explore_board_after_click(self.board_array , index_board_i, index_board_j)
        self.board_array = arr
        color = (150, 150, 150)
        #self.rect_clicked(color, j, i)
        self.scan_board()
        #self.board_array = arr


    # THIS JUST COLORS ALL SURROUNDING CELLS  WITH VAL 1
    def scan_board(self):
        for i in range( 0, self.row ):
            for j in range( 0, self.col ):
                if self.board_array[i][j] == 1:
                    canvas_arr_i =  i * 20
                    canvas_arr_j = j * 20
                    color = (150,150,150)
                    self.rect_clicked( color , canvas_arr_i, canvas_arr_j) # note: read startprgm rect_click why we ahve j and i instead of i and j

    # Function to change color of cell after clicked and shows number on it
    def rect_clicked(self,color, row_x , col_y):
        #Note: Make sure to add the other 2d array values here to store the value - currently this only has the canvas gui aspect functionality to it
        Grid_box_Object = pygame.draw.rect(self.screen, color, [col_y, row_x, self.box_width, self.box_height])   # row_x=row and col_y=col is the position where the box will be displayed
        text = self.font.render('1', True, (255, 255, 255))
        self.screen.blit(text, Grid_box_Object.midtop)
        pygame.display.flip()
        self.set_clicked_rect( row_x , col_y)
        return Grid_box_Object

    def set_clicked_rect(self, row_x , col_y):
        self.recent_clicked_rect_x = row_x
        self.recent_clicked_rect_y = col_y

    def get_clicked_rect(self):
        return [self.recent_clicked_rect_x , self.recent_clicked_rect_y]

    def get_all_rects(self):
        return self.list_of_all_rects

    # Functionality: This function draws the maze on the pygame canvas/screen
    def draw_cells_map(self,screen, color):
        pl = 6
        for i in range(0, self.row):
            for j in range(0, self.col):
                if self.board_array[i,j] == 8:
                    self.board_generator(screen, color, i * (self.box_width+1), j * (self.box_height+1))
                if self.board_array[i, j] == 1:
                    self.board_generator(screen, (255,255,255), i * (self.box_width + 1), j * (self.box_height + 1)) # +1 is to add a border shade to the cells

    # This is to color the moving routes
    def m_pattern(self, i, j, color, status):
        self.set_maze_pattern(self.screen, i, j, color, status)

    # Functionality: Sets the canvas color for cells and values for the array indices
    def set_maze_pattern(self, screen, i, j , color, status):
        if status == 'blocked':
            self.board_array[i, j] = 8
            self.board_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            #pygame.display.flip()
        if status == 'start':
            self.board_array[i, j] = 1
            self.board_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            #pygame.display.flip()
        else:
            self.board_array[i, j] = 1
            self.board_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            #pygame.display.flip()


    # This is to color the moving routes
    def player_movement(self, i, j, color, status):
        self.set_player_movement(self.screen, i, j, color, status)

    # Functionality: Sets the player movement values on the array
    def set_player_movement(self, screen, i, j , color, status):
        if status == 'blocked':
            self.board_array[i, j] = 8
            self.board_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            pygame.display.flip()
        if status == 'start':
            self.board_array[i, j] = 1
            self.board_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            pygame.display.flip()
        if status == 'fire':
            self.board_array[i, j] = 1111
            self.board_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            pygame.display.flip()
        if status == 'back track':
            self.board_array[i, j] = 1
            self.board_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            pygame.display.flip()
        if status == 'player':
            self.board_array[i, j] = 2
            self.board_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            pygame.display.flip()
        else:
            self.board_array[i, j] = 4
            self.board_generator(screen, color, i * (self.box_width + 1), j * (self.box_height + 1))
            pygame.display.flip()
        time.sleep(0.05) # PLAYER

    #Functionality: maps values to 2d maze
    def map_values(self):
        for i in range(1, self.row-1):
            for j in range(1, self.col-1):
                if self.board_array[i][j]==0:
                    self.board_array[i][j] = 1
                    #self.maze_generator(self.screen, (0, 128, 0), i * (self.box_width + 1), j * (self.box_height + 1))

    def generate_board(self, obj):
        self.board_array = np.full((self.row, self.col),int(8))
        self.map_values() # To map values on 2d array maze map
        self.draw_cells_map(self.screen , (187,187,187)) # Draws out the GUI from the stored array values


    def start_algorithm(self, obj, choice, flammability_rate):
        ThingsToAppearOnScreen_Display = self.screen
        self.board_array = np.zeros((self.row, self.col), dtype=int)
        pygame.display.set_caption("MineSweeper", "MS")
        pygame.display.flip()
        a = None

        self.agent_class = agnt(self.screen, self.board_array, obj)
        #a = mazeGen(ThingsToAppearOnScreen_Display, self.get_arr() , obj)   # MY OWN CLASS
        self.generate_board(a)   # This function draws the maze
        pygame.display.flip()
