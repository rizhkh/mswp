import pygame as pygame
import numpy as np
from collections import deque
import random


class environment:
    box_height = 0
    box_width = 0
    list_of_all_rects = []


    row = 10
    col = 10
    total_mines = 20
    mines = total_mines




    m = None    # empty object
    maze_array = []
    screen = None
    q = deque() # where list of active nodes are stored
    q_visited = []
    q_list_of_visited_nodes = []    #[[1,1]]
    start_i = 10    # starting index i for current node (parent node)
    start_j = 10    # starting index j for current node (parent node)

    def __init__(self , scrn, arr, obj, bh, bw):
        self.font = pygame.font.SysFont('Arial', 12)
        self.m = obj    #Copy the ref address in an empty obj -> point towards the orignal address
        self.screen = scrn
        self.maze_array = np.copy(arr)  # (obj.get_arr())
        self.box_height = bh
        self.box_width = bw

    # Returns value of cell in 2d array
    def get_cell_value(self,arr,i,j):
        return arr[i][j]


    # Functionality: Check neighbors and returns total numbers of mines present in neighbors - returns clue
    # Returns number of mines in neighbors - Clue
    def get_clue(self, arr,i,j):
        val = 0
        counter = 0

        if (i>= 0 and i<self.row) and (j>= 0 and j<self.col):
            v = self.get_cell_value(arr,i,j)
            val = val + v
            #arr[i][j] = 1

        # Up direction
        if ( (i - 1) >= 0 and (i - 1) < self.row) and (j >= 0 and j < self.col):
            v = self.get_cell_value(arr, i-1, j)
            val = val + v
            #arr[i - 1][j] = 1 # up

        # Down direction
        if ( (i + 1) >= 0 and (i + 1) < self.row) and (j >= 0 and j < self.col):
            v = self.get_cell_value(arr, i+1, j)
            val = val + v
            #arr[i + 1][j] = 1 # down

        # Left direction
        if (i>= 0 and i<self.row) and ( (j - 1) >= 0 and (j - 1) < self.col):
            v = self.get_cell_value(arr, i, j-1)
            val = val + v
            #arr[i][j - 1] = 1 # left

        # Right direction
        if (i>= 0 and i<self.row) and ( (j + 1) >= 0 and (j + 1) < self.col):
            v = self.get_cell_value(arr, i, j+1)
            val = val + v
            #arr[i][j + 1] = 1 # right

        # Top-Left direction
        if ( (i - 1) >= 0 and (i - 1) < self.row) and ( (j - 1) >= 0 and (j - 1) < self.col):
            v = self.get_cell_value(arr, i-1, j-1)
            val = val + v
            #arr[i - 1][j - 1] = 1 # top left

        # Top-Right direction
        if ( (i - 1) >= 0 and (i - 1) < self.row) and ( (j + 1) >= 0 and (j + 1) < self.col):
            v = self.get_cell_value(arr, i-1, j+1)
            val = val + v
            #arr[i - 1][j + 1] = 1  # top right

        # Bottom-Left direction
        if ( (i + 1) >= 0 and (i + 1) < self.row) and ( (j - 1) >= 0 and (j - 1) < self.col):
            v = self.get_cell_value(arr, i+1, j-1)
            val = val + v
            #arr[i + 1][j - 1] = 1 # bottom left

        # Bottom-Right direction
        if ( (i + 1) >= 0 and (i + 1) < self.row) and ( (j + 1) >= 0 and (j + 1) < self.col):
            v = self.get_cell_value(arr, i+1, j+1)
            val = val + v
            #arr[i + 1][j + 1] = 1  # bottom right
        return val

    # Note: Keep track of each location where the mine is placed
    #Functionality: This randomly adds mines on the board
    def add_mines_randomly(self, arr):

        i = 0
        j = 0

        #while i < len(arr):
        while self.mines > 0 :
            if j == len(arr):
                i += 1
                j = 0
            if i == len(arr):
                i=0

            rnum = random.randint(0, 3)
            if rnum == 0 and self.mines != 0:
                arr[i][j] = 1
                self.mines -= 1
            j += 1

        # for i in range(0, len(arr) ):
        #     for j in range(i, len(arr) ):
        #         rnum = random.randint(0, 3)
        #         if rnum==0 and self.mines!=0:
        #             arr[i][j] = 1
        #             self.mines =- 1

        return arr


# Code below is for environmnet GUI

    def board_generator(self, screen, color, row_x , col_y):
        A = pygame.draw.rect(screen, color, [col_y, row_x, self.box_width, self.box_height])   # row_x=row and col_y=col is the position where the box will be displayed
        self.list_of_all_rects.append([row_x,col_y])
        return A

    def draw_cells_map(self, arr,screen, color):
        pl = 6
        for i in range(0, self.row):
            for j in range(0, self.col):
                #if self.board_array[i,j] == 0:
                #if arr[i, j] == 0:
                self.board_generator(screen, color, i * (self.box_width+1), j * (self.box_height+1))

    def generate_board(self, arr):
        #self.board_array = np.full((self.row, self.col),int(0))
        self.draw_cells_map( arr,self.screen , (187,187,187)) # Draws out the GUI from the stored array values

    def color_cell(self, message,row_x , col_y, status):
        row_x = row_x * 20
        col_y = col_y * 20

        if status == 0:
            #Note: Make sure to add the other 2d array values here to store the value - currently this only has the canvas gui aspect functionality to it
            Grid_box_Object = pygame.draw.rect(self.screen, (150, 150, 150), [col_y, row_x, self.box_width, self.box_height])   # row_x=row and col_y=col is the position where the box will be displayed
            text = self.font.render(message, True, (255, 255, 255))
            self.screen.blit(text, Grid_box_Object.midtop)
            pygame.display.flip()
        if status == 'flag':
            img = pygame.image.load('flag.png').convert()
            img = pygame.transform.scale(img, (18, 18))
            Grid_box_Object = pygame.draw.rect(self.screen, (255, 0, 0), [col_y, row_x, self.box_width, self.box_height])   # row_x=row and col_y=col is the position where the box will be displayed
            self.screen.blit(img, Grid_box_Object)#, Grid_box_Object.midtop)
            pygame.display.flip()
        if status == 1:
            img = pygame.image.load('mine.png').convert()
            img = pygame.transform.scale(img, (18, 18))
            Grid_box_Object = pygame.draw.rect(self.screen, (255, 0, 0), [col_y, row_x, self.box_width, self.box_height])   # row_x=row and col_y=col is the position where the box will be displayed
            self.screen.blit(img, Grid_box_Object)#, Grid_box_Object.midtop)
            pygame.display.flip()

        return Grid_box_Object

    def get_all_rects(self):
        return self.list_of_all_rects