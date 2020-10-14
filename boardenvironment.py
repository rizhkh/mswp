import numpy as np
from collections import deque
import random


class environment:
    row = 10
    col = 10
    total_mines = 10
    mines = total_mines




    m = None    # empty object
    maze_array = []
    screen = None
    q = deque() # where list of active nodes are stored
    q_visited = []
    q_list_of_visited_nodes = []    #[[1,1]]
    start_i = 10    # starting index i for current node (parent node)
    start_j = 10    # starting index j for current node (parent node)

    def __init__(self , scrn, arr, obj):
        self.m = obj    #Copy the ref address in an empty obj -> point towards the orignal address
        self.screen = scrn
        self.maze_array = np.copy(arr)  # (obj.get_arr())

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
        print(arr)
        print("************")
        for i in range(0, len(arr) ):
            for j in range(i, len(arr) ):
                rnum = random.randint(0, 3)
                if rnum==0 and self.mines!=0:
                    arr[i][j] = 1
                    self.mines =- 1

        return arr

