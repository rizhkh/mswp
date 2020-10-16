import numpy as np
from collections import deque
import random
from mswp.boardenvironment import environment
from mswp.cellInformation import cell


# # note
# To access data from cell object try doing this
# a = self.all_cells[index]
# a[0] is in the index
# a[1] is the reference
# obj = a[1]
# obj.method_name()
# or
# a[1].method_name()
# or
# obj = self.all_cells[ [key,1]
# obj.method_name()
# or
# self.all_cells[ [key,1].method_name()
#
# if a[0] == key:
#     obj = a[1]
#     # obj = self.all_cells[i][1].get_current_position()
#     # obj= self.all_cells[ [key,1] ]
#     print(obj.get_current_position())


class agnt:

    #all_cells = dict() #np.zeros((0, 0), dtype=int) # this list is total cells on the board
    all_cells = []  # this list is total cells on the board  # This would store the object of each cell that is visited - we use this list to access all stored information
    visited_cells = []  # just stores index of cells that are visited
    mine_cells = [] # list of cells that are mines and they have been revealed - not hidden on board anymore

    unvisited_cells = []

    environment_obj = None

    board_array_agent = np.zeros((0, 0), dtype=int)
    array_board = np.zeros((0, 0), dtype=int) # array val from startprm

    box_height = 0
    box_width = 0
    row = 0
    col = 0

    def __init__(self, arr, row_dimension, col_dimenison,bh,bw):
        self.array_board = np.copy(arr)
        #self.all_cells = np.copy(arr)
        self.row = row_dimension
        self.col = col_dimenison
        self.init_all_cells()
        self.box_height = bh
        self.box_width = bw

    # This lets agent use environment methods to get cell values and use various other information for its knowledge base that agent should know
    def set_environment_obj(self, obj):
        self.environment_obj = obj

    # this function runs just once in the start and this is to initialize an object and set value of 0 for all unrevealed cells
    def init_all_cells(self):
        for i in range(0, self.row ):
            for j in range ( 0 , self.col):
                self.unvisited_cells.append([i, j])
                index = [i,j]
                status = 'un-visited'
                mines_surrounding_it_clue = 0
                safe_neighbors = 0
                mines_indentified_around = 0
                hidden_cells_around = len( self.get_neighbors_current_cell(i, j) )
                obj = cell( index, status, mines_surrounding_it_clue, safe_neighbors, mines_indentified_around, hidden_cells_around)
                key = [i,j]
                self.all_cells.append( [key,obj] )



    # This function is an example function on how to access object from list - cell objects
    def print_value_cell(self):
        key = [4,4]
        for i in range(0, len( self.all_cells ) ):
            a = self.all_cells[ i ]
            if a[0] == key :
                obj = a[1]
                #obj = self.all_cells[i][1].get_current_position()
                #obj= self.all_cells[ [key,1] ]
                print( obj.get_current_position() )
                print("works")

    # returns the object instance of the current cell from the list where it is stored - Used in process curr cell to get the object of cell we are processing and update info
    def get_cur_cell_instance(self, key):
        for i in range(0, len( self.all_cells ) ):
            a = self.all_cells[ i ]
            if a[0] == key :
                obj = a[1]
                return obj

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
            if (i not in self.visited_cells) and (i not in self.mine_cells):
                val += 1
        return val

    # Returns list of hidden cells that are neighbors of current cell
    def get_hidden_cells_list(self, list):
        ret_list = []
        for i in list:
            if (i not in self.visited_cells) and (i not in self.mine_cells):
                ret_list.append( i )
        return ret_list

    # Returns number of mine cells as neighbors of current cell
    def get_mines_in_neighbor_cells(self, list):
        val = 0
        for i in list:
            if i in self.mine_cells:
                val += 1
        return val

    def mine_estimate(self, clue, tot_mines, hidden_neighbor_mine):
        print("ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")
        print(clue , " , " ,(hidden_neighbor_mine + tot_mines))
        if clue == (hidden_neighbor_mine + tot_mines):
            print("azzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz")
            return True
        return False
        # #number of hidden neighbors = clue - total revealed mines
        # if hidden_neighbor_mine <= 0:
        #     return 0
        # return hidden_neighbor_mine


    def safe_estimator(self, clue, tot_rev_neighbors, hidden_neighbor_mine):
        if (8-clue) == (hidden_neighbor_mine + tot_rev_neighbors):
            return True
        return False
        # tot_safe_neighbor = 8 -clue
        # hidden_neighbor_safe = tot_safe_neighbor - tot_rev_neighbors
        # #number of hidden neighbors = total number of safe neighbors (8 - clue) - total revealed neighbors
        # if hidden_neighbor_safe <= 0:
        #     return 0
        # return hidden_neighbor_safe

    # Functionality: checks current_cell neighbors and determine which cell is a hidden cell, which cell is already visited and what cell is a mine
    def process_current_cell(self,i,j):
        print("-----")
        print(self.array_board)
        status = self.environment_obj.get_cell_value( self.array_board, i, j)
        obj = self.get_cur_cell_instance( [i,j] )
        # obj.current_position    # index in 2d array or matrix
        # obj.status  # whether or not it is a mine or safe
        # obj.clue    # if safe, the number of mines surrounding it indicated by the clue
        # obj.safe_n  # already revealed cells that are not flagged
        # obj.appearing_mines_in_neighbors    # number of flagged cells around it or mines
        # obj.cells_still_unexplored_in_neighbors # number of unexplored neighbors around it

        if status == 1:
            self.mine_cells.append( [i,j] )
            self.unvisited_cells.remove( [i,j] )

        if status != 1:
            self.visited_cells.append( [i,j] ) # adds current processed cell in list of visited cells if its safe

            self.unvisited_cells.remove([i, j]) # removing index from unvisited cells

            # identifies the index as safe by marking it 0
            obj.status = 0

            # assigns clue (clue is number of mines in adjacent neighbors
            obj.clue = self.environment_obj.get_clue(self.array_board , i, j)

            # gets a list of neighbors of current cells
            current_neighbors = self.get_neighbors_current_cell(i,j)

            # In adjacent cells, returns a value for neighbors that are already visited/revealed - Returns just a value not cell indexs that are visited
            visited = self.get_visited_cells(current_neighbors)
            obj.safe_n = visited

            # In adjacent cells, returns a value for neighbors that are hidden/unrevealed cells - Returns just a value not cell indexs that are hidden
            hidden = self.get_hidden_cells(current_neighbors)
            obj.cells_still_unexplored_in_neighbors = hidden

            # In adjacent cells, returns a value for neighbors that are mines - Returns just a value not cell indexs that are flagged or mines
            mines = self.get_mines_in_neighbor_cells(current_neighbors)
            obj.appearing_mines_in_neighbors = mines

            obj.print_cell_info()

            a = self.mine_estimate(obj.clue, mines, hidden)

            if a == True:
                print("ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")
                self.flag_cells(current_neighbors)
                #returning_list = self.flag_cells( current_neighbors )
                #return returning_list
            #
            # else:
            #     a = self.safe_estimator(obj.clue, visited, hidden)
            #     if a == True:

    def flag_cells(self, current_neighbors):
        neighbor = self.get_hidden_cells_list(current_neighbors)
        for i in neighbor:
            obj = self.get_cur_cell_instance( i )
            obj.status = 1  # whether or not it is a mine or safe
            self.mine_cells.append(i)
            color = (255, 255, 255)
            index_i = i[0]
            index_j = i[1]
            self.environment_obj.color_cell('', color, index_i, index_j,'flag')
        return neighbor

    def flag_cells_as_safe(self, current_neighbors):
        neighbor = self.get_hidden_cells_list(current_neighbors)
        for i in neighbor:
            obj = self.get_cur_cell_instance( i )
            obj.status = 1  # whether or not it is a mine or safe
            obj.status = 0  # whether or not it is a mine or safe
        return neighbor



    # Now add a func that stores all information of that cell - and in the next move if that cell is a neighbor
    # you can use that information
