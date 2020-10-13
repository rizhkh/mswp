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
    #board_array = np.zeros((0, 0), dtype=object)
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
        obj = self.agent_class  # do not remove this - obj variable is being passed the reference of global obj this way the refernce is copied in start_algorithm
        # and we dont have pass any obj in main.py

        # we are dividing by 20 due do GUI dimension for pycharm - its a scaling issue in GUI
        index_board_i= int(i/20)
        index_board_j= int(j/20)
        #print("index: " , index_board_i , ",", index_board_j)
        val = obj.explore_board_after_click(self.board_array , index_board_i, index_board_j)
        self.highlight_board(index_board_i,index_board_j)
        #self.scan_board()


    # THIS JUST COLORS ALL SURROUNDING CELLS  WITH VAL 1
    def scan_board(self):
        for i in range( 0, self.row ):
            for j in range( 0, self.col ):
                if self.board_array[i][j] == 1:
                    canvas_arr_i =  i * 20
                    canvas_arr_j = j * 20
                    color = (150,150,150)
                    self.rect_clicked( '1',color , canvas_arr_i, canvas_arr_j) # note: read startprgm rect_click why we ahve j and i instead of i and j
                else:
                    canvas_arr_i =  i * 20
                    canvas_arr_j = j * 20
                    color = (150,150,150)
                    self.rect_clicked( '2',color , canvas_arr_i, canvas_arr_j) # note: read startprgm rect_click why we ahve j and i instead of i and j


    # my thought process - in agent.py this will call explore_board_after_click and that will return number of surrounding cells with mines
    # this func will highlight them
    # Functionality: This func prints the number of cells in neighbors are mines or if its a mine
    def highlight_board(self,i,j):
        canvas_arr_i = i * 20  # the reason it is being multiplied is because the cell size is set to 20 - if its the orignal value then it causes GUI problems
        canvas_arr_j = j * 20
        status = self.agent_class.get_cell_value(self.board_array,i,j)
        if status != 1:
            color = (150, 150, 150)
            val = self.agent_class.explore_board_after_click(self.board_array,i,j)
            self.rect_clicked( str(val) , color, canvas_arr_i,canvas_arr_j)
        elif status == 1:
            color = (255, 0, 0)
            self.rect_clicked('', color, canvas_arr_i, canvas_arr_j)



    # Function to change color of cell after clicked and shows number on it
    def rect_clicked(self, message,color, row_x , col_y):
        #Note: Make sure to add the other 2d array values here to store the value - currently this only has the canvas gui aspect functionality to it
        Grid_box_Object = pygame.draw.rect(self.screen, color, [col_y, row_x, self.box_width, self.box_height])   # row_x=row and col_y=col is the position where the box will be displayed
        text = self.font.render(message, True, (255, 255, 255))
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
                if self.board_array[i,j] == 0:
                    self.board_generator(screen, color, i * (self.box_width+1), j * (self.box_height+1))
                # if self.board_array[i, j] == 1:
                #     self.board_generator(screen, (255,255,255), i * (self.box_width + 1), j * (self.box_height + 1)) # +1 is to add a border shade to the cells

    def generate_board(self, obj):
        self.board_array = np.full((self.row, self.col),int(0))
        self.draw_cells_map(self.screen , (187,187,187)) # Draws out the GUI from the stored array values


    def start_algorithm(self, obj, choice, flammability_rate):
        ThingsToAppearOnScreen_Display = self.screen
        self.board_array = np.zeros((self.row, self.col), dtype=int)
        pygame.display.set_caption("MineSweeper", "MS")
        pygame.display.flip()
        a = None

        self.agent_class = agnt(self.screen, self.board_array, obj)
        #agent_obj = agnt(self.screen, self.board_array, obj)
        #a = mazeGen(ThingsToAppearOnScreen_Display, self.get_arr() , obj)   # MY OWN CLASS
        self.generate_board(a)   # This function draws the maze
        self.board_array = self.agent_class.add_mines_randomly(self.board_array)
        print(self.board_array)
        pygame.display.flip()
