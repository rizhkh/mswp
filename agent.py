import numpy as np
from collections import deque
import random
from mswp.boardenvironment import environment

class agnt:

    visited_cells = []  # just stores index of cells that are visited
    mine_cells = [] # list of cells that are mines and they have been revealed - not hidden on board anymore
    clear_cells = []
    list_of_cells_explored_stored_info = [] # This would store the object of each cell that is visited - we use this list to access all stored information

    environment_obj = None
    board_array_agent = np.zeros((0, 0), dtype=int)
    array_stp = np.zeros((0, 0), dtype=int) # array val from startprm

    class cell:

        current_position = None
        status = None
        clue = None
        safe_n = None
        appearing_mines_in_neighbors = None
        cells_still_unexplored_in_neighbors = None

        def __init__(self, index, status, mines_surrounding_it_clue, safe_neighbors, mines_indentified_around, hidden_cells_around):
            self.current_position = index
            self.status = status
            self.clue = mines_surrounding_it_clue
            self.safe_n = safe_neighbors
            self.appearing_mines_in_neighbors = mines_indentified_around
            self.cells_still_unexplored_in_neighbors = hidden_cells_around


    def __init__(self, arr):
        self.array_stp = np.copy(arr)
        print()

    # This lets agent use environment methods to get cell values and use various other information for its knowledge base that agent should know
    def set_environment_obj(self, obj):
        self.environment_obj = obj


    # Returns number of visited cells in neighbors of current cell
    def get_visited_cells(self, list):
        val = 0
        for i in list:
            if i in self.visited_cells:
                val += 1
        return val

    # Returns number of hidden cells in neighbors of current cell
    def get_hidden_cells(self, list):
        val = 0
        for i in list:
            if i not in self.visited_cells:
                val += 1
        return val

    # Returns number of mine cells as neighbors of current cell
    def get_mines_in_neighbor_cells(self, list):
        val = 0
        for i in list:
            if i in self.mine_cells:
                val += 1
        return val

    # Returns list of neighbors of current cell being processed
    def get_neighbors_current_cell(self,i,j):
        current_neighbors = []
        # Up direction
        if ( (i - 1) >= 0 and (i - 1) < self.row) and (j >= 0 and j < self.col):
            current_neighbors.append([i-1, j])

        # Down direction
        if ( (i + 1) >= 0 and (i + 1) < self.row) and (j >= 0 and j < self.col):
            current_neighbors.append([i + 1, j])

        # Left direction
        if (i>= 0 and i<self.row) and ( (j - 1) >= 0 and (j - 1) < self.col):
            current_neighbors.append([i, j - 1])

        # Right direction
        if (i>= 0 and i<self.row) and ( (j + 1) >= 0 and (j + 1) < self.col):
            current_neighbors.append([i, j + 1])

        # Top-Left direction
        if ( (i - 1) >= 0 and (i - 1) < self.row) and ( (j - 1) >= 0 and (j - 1) < self.col):
            current_neighbors.append([i - 1, j - 1])

        # Top-Right direction
        if ( (i - 1) >= 0 and (i - 1) < self.row) and ( (j + 1) >= 0 and (j + 1) < self.col):
            current_neighbors.append([i - 1, j + 1])

        # Bottom-Left direction
        if ( (i + 1) >= 0 and (i + 1) < self.row) and ( (j - 1) >= 0 and (j - 1) < self.col):
            current_neighbors.append([i + 1, j - 1])

        # Bottom-Right direction
        if ( (i + 1) >= 0 and (i + 1) < self.row) and ( (j + 1) >= 0 and (j + 1) < self.col):
            current_neighbors.append([i + 1, j + 1])

        #current_neighbors = [ [i-1,j], [i+1, j], [i, j-1], [i, j+1], [i-1, j-1], [i-1, j+1], [i+1, j-1], [i+1, j+1] ]
        return  current_neighbors



    # for a given cell, the total number of mines (the clue) minus the number of revealed mines is the number of
    # hidden neighbors, every hidden neighbor is a mine.
    # [MINES] = number of hidden neighbors / (total number of mines(clue) - number of revealed mines (in neighbor or complete map?))
    def check_mine(self, clue, tot_mines):
        hidden_neighbor_mine = clue - tot_mines
        #number of hidden neighbors = clue - total revealed mines
        if hidden_neighbor_mine <= 0:
            return 0
        return hidden_neighbor_mine

    # If, for a given cell, the total number of safe neighbors (8 - clue) minus the number of revealed safe neighbors is
    # the number of hidden neighbors, every hidden neighbor is safe.
    # [Safe] = number of hidden neighbors / ( the total number of safe neighbors (8 - clue) - the number of revealed safe neighbors)
    def check_safe(self, clue, tot_rev_neighbors):
        tot_safe_neighbor = 8 -clue
        hidden_neighbor_safe = tot_safe_neighbor - tot_rev_neighbors
        #number of hidden neighbors = total number of safe neighbors (8 - clue) - total revealed neighbors
        if hidden_neighbor_safe <= 0:
            return 0
        return hidden_neighbor_safe

    # if clue==0 reveal all neighboring cells on the board
    # then go to each cell one by one and reveal clue and store information
    # make sure you are keeping track of neighboring cells in queue - dfs

    # Functionality: checks current_cell neighbors and determine which cell is a hidden cell, which cell is already visited and what cell is a mine
    def process_current_cell(self,i,j):
        status = self.environment_obj.get_cell_value( self.array_stp, i, j)

        if status != 1:
            current_neighbors = self.get_neighbors_current_cell(i,j)    # gets a list of neighbors of current cells
            visited = self.get_visited_cells(current_neighbors) # check which neighbors are already visited - cells from current_neighbors in visited cells
            hidden = self.get_hidden_cells(current_neighbors) # check which neighbors are hidden - cells from current_neighbors not in visited_cells
            mines = self.get_mines_in_neighbor_cells(current_neighbors) # check which neighbors are mine cells - cells current_neighbors that are revealed mines

            # Note: make sure to init the cell class for the very first cell and make sure you are not overwriting the same object
            # you will be using those objects by index e.g iterate a list: when index matches it pulls up all the information for that index

            # Read description and add the code



    # Now add a func that stores all information of that cell - and in the next move if that cell is a neighbor
    # you can use that information
