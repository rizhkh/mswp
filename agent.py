import numpy as np
from collections import deque
import random


class agnt:
    row = 10
    col = 10

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


    # THIS FUNCTION IS WRITTEN SO IT CAN BE USED: FOR A BASIC STRUCTURE WHEN YOU CLICK A SLOT ALL SURROUNDING CELLS ARE GIVEN 1 VALUE
    def explore_board_after_click(self, arr,i,j):
        if (i>= 0 and i<self.row) and (j>= 0 and j<self.col):
            arr[i][j] = 9

        if ( (i - 1) >= 0 and (i - 1) < self.row) and (j >= 0 and j < self.col):
            arr[i - 1][j] = 1 # up

        if ( (i + 1) >= 0 and (i + 1) < self.row) and (j >= 0 and j < self.col):
            arr[i + 1][j] = 1 # down

        if (i>= 0 and i<self.row) and ( (j - 1) >= 0 and (j - 1) < self.col):
            arr[i][j - 1] = 1 # left

        if (i>= 0 and i<self.row) and ( (j + 1) >= 0 and (j + 1) < self.col):
            arr[i][j + 1] = 1 # right

        if ( (i - 1) >= 0 and (i - 1) < self.row) and ( (j - 1) >= 0 and (j - 1) < self.col):
            arr[i - 1][j - 1] = 1 # top left

        if ( (i - 1) >= 0 and (i - 1) < self.row) and ( (j + 1) >= 0 and (j + 1) < self.col):
            arr[i - 1][j + 1] = 1  # top right

        if ( (i + 1) >= 0 and (i + 1) < self.row) and ( (j - 1) >= 0 and (j - 1) < self.col):
            arr[i + 1][j - 1] = 1 # bottom left

        if ( (i + 1) >= 0 and (i + 1) < self.row) and ( (j + 1) >= 0 and (j + 1) < self.col):
            arr[i + 1][j + 1] = 1  # bottom right

        print(arr)
        return arr
