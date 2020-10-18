import numpy as np
from collections import deque
import random
from mswp.boardenvironment import environment
from mswp.cellInformation import cell
import time


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
    # all_cells = dict() #np.zeros((0, 0), dtype=int) # this list is total cells on the board
    all_cells = []  # this list is total cells on the board  # This would store the object of each cell that is visited - we use this list to access all stored information
    visited_cells = []  # just stores index of cells that are visited
    mine_cells = []  # list of cells that are mines and they have been revealed - not hidden on board anymore

    unvisited_cells = []

    traverse_cells = [] # list of cells that needs to be processed / traversed

    knowledge_base = []
    # Content is stored in knowledge in this format:
    # [Var,Value] -> Var = Value
    # to look up just a var make sure to look up by len ==2

    kb = dict()

    # to look up just a var in equation make sure to look up by len > 2
    # then look inside the list list as these are nested lists
    # [Var,Var,Value] - > Var + Var = Val
    # [Var,Var,Var,Value]  - > Var + Var + Var = Val

    environment_obj = None

    board_array_agent = np.zeros((0, 0), dtype=int)
    array_board = np.zeros((0, 0), dtype=int)  # array val from startprm

    box_height = 0
    box_width = 0
    row = 0
    col = 0

    def __init__(self, arr, row_dimension, col_dimenison, bh, bw):
        self.array_board = np.copy(arr)
        # self.all_cells = np.copy(arr)
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
        for i in range(0, self.row):
            for j in range(0, self.col):
                self.unvisited_cells.append([i, j])
                index = [i, j]
                status = 'un-visited'
                mines_surrounding_it_clue = 0
                safe_neighbors = 0
                mines_indentified_around = 0
                hidden_cells_around = len(self.get_neighbors_current_cell(i, j))
                obj = cell(index, status, mines_surrounding_it_clue, safe_neighbors, mines_indentified_around,
                           hidden_cells_around)
                key = [i, j]
                self.all_cells.append([key, obj])

    # This function is an example function on how to access object from list - cell objects
    def print_value_cell(self):
        key = [4, 4]
        for i in range(0, len(self.all_cells)):
            a = self.all_cells[i]
            if a[0] == key:
                obj = a[1]
                # obj = self.all_cells[i][1].get_current_position()
                # obj= self.all_cells[ [key,1] ]
                print(obj.get_current_position())
                print("works")

    # returns the object instance of the current cell from the list where it is stored - Used in process curr cell to get the object of cell we are processing and update info
    def get_cur_cell_instance(self, key):
        for i in range(0, len(self.all_cells)):
            a = self.all_cells[i]
            if a[0] == key:
                obj = a[1]
                return obj

    # Returns list of neighbors of current cell being processed
    def get_neighbors_current_cell(self, i, j):
        current_neighbors = []
        # Up direction
        if ((i - 1) >= 0 and (i - 1) < self.row) and (j >= 0 and j < self.col):
            current_neighbors.append([i - 1, j])

        # Down direction
        if ((i + 1) >= 0 and (i + 1) < self.row) and (j >= 0 and j < self.col):
            current_neighbors.append([i + 1, j])

        # Left direction
        if (i >= 0 and i < self.row) and ((j - 1) >= 0 and (j - 1) < self.col):
            current_neighbors.append([i, j - 1])

        # Right direction
        if (i >= 0 and i < self.row) and ((j + 1) >= 0 and (j + 1) < self.col):
            current_neighbors.append([i, j + 1])

        # Top-Left direction
        if ((i - 1) >= 0 and (i - 1) < self.row) and ((j - 1) >= 0 and (j - 1) < self.col):
            current_neighbors.append([i - 1, j - 1])

        # Top-Right direction
        if ((i - 1) >= 0 and (i - 1) < self.row) and ((j + 1) >= 0 and (j + 1) < self.col):
            current_neighbors.append([i - 1, j + 1])

        # Bottom-Left direction
        if ((i + 1) >= 0 and (i + 1) < self.row) and ((j - 1) >= 0 and (j - 1) < self.col):
            current_neighbors.append([i + 1, j - 1])

        # Bottom-Right direction
        if ((i + 1) >= 0 and (i + 1) < self.row) and ((j + 1) >= 0 and (j + 1) < self.col):
            current_neighbors.append([i + 1, j + 1])

        # current_neighbors = [ [i-1,j], [i+1, j], [i, j-1], [i, j+1], [i-1, j-1], [i-1, j+1], [i+1, j-1], [i+1, j+1] ]
        return current_neighbors

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
                ret_list.append(i)
        return ret_list

    # Returns number of mine cells as neighbors of current cell
    def get_mines_in_neighbor_cells(self, list):
        val = 0
        for i in list:
            if i in self.mine_cells:
                val += 1
        return val

    def mine_estimate(self, clue, tot_mines, hidden_neighbor_mine):
        #print(clue, " , ", (hidden_neighbor_mine + tot_mines))
        #if (clue - hidden_neighbor_mine) == (tot_mines):
        #if (clue-tot_mines) == (hidden_neighbor_mine):
        if clue == (hidden_neighbor_mine + tot_mines): # use this one
            return True
        return False

    def safe_estimator(self, clue, tot_rev_neighbors, hidden_neighbor_mine):
        #if ((8 - clue) - tot_rev_neighbors) == (hidden_neighbor_mine):
        if (8 - clue) == (hidden_neighbor_mine + tot_rev_neighbors):   # use this one
            return True
        return False


    # Functionality: checks current_cell neighbors and determine which cell is a hidden cell, which cell is already visited and what cell is a mine
    def process_current_cell(self, i, j):
        print("-----")
        print(self.array_board)
        status = self.environment_obj.get_cell_value(self.array_board, i, j)
        obj = self.get_cur_cell_instance([i, j])
        # obj.current_position    # index in 2d array or matrix
        # obj.status  # whether or not it is a mine or safe
        # obj.clue    # if safe, the number of mines surrounding it indicated by the clue
        # obj.safe_n  # already revealed cells that are not flagged
        # obj.appearing_mines_in_neighbors    # number of flagged cells around it or mines
        # obj.cells_still_unexplored_in_neighbors # number of unexplored neighbors around it

        if status == 1:
            self.environment_obj.color_cell("", i, j, 1)  # This code marks the cell on GUI board
            self.mine_cells.append([i, j])
            if [i, j] in self.unvisited_cells:
                self.unvisited_cells.remove([i, j])

        if status != 1:
            self.visited_cells.append([i, j])  # adds current processed cell in list of visited cells if its safe
            if [i, j] in self.unvisited_cells:
                self.unvisited_cells.remove([i, j])  # removing index from unvisited cells
            obj.status = 0  # identifies the index as safe by marking it 0

            obj.clue = self.environment_obj.get_clue(self.array_board, i, j)    # assigns clue (clue is number of mines in adjacent neighbors

            self.environment_obj.color_cell(str(obj.clue), i, j, 0) # This code marks the cell on GUI boards

            current_neighbors = self.get_neighbors_current_cell(i, j) # gets a list of neighbors of current cells

            visited = self.get_visited_cells(current_neighbors) # In adjacent cells, returns a value for neighbors that are already visited/revealed - Returns just a value not cell indexs that are visited
            obj.safe_n = visited

            hidden = self.get_hidden_cells(current_neighbors)# In adjacent cells, returns a value for neighbors that are hidden/unrevealed cells - Returns just a value not cell indexs that are hidden
            obj.cells_still_unexplored_in_neighbors = hidden

            mines = self.get_mines_in_neighbor_cells(current_neighbors)# In adjacent cells, returns a value for neighbors that are mines - Returns just a value not cell indexs that are flagged or mines
            obj.appearing_mines_in_neighbors = mines

            obj.print_cell_info()   # To print each cell info

            # code below is for the basic algorithm from the description
            a = self.mine_estimate(obj.clue, mines, hidden) # this checks the mine code from basic algorithm in the description
            if a == True:
                self.flag_cells(current_neighbors)
            else:
                a = self.safe_estimator(obj.clue, visited, hidden)
                ret_list = self.flag_cells_as_safe(current_neighbors)
                return ret_list

        return []


    # If a cell is flagged then this function will flag the cell
    def flag_cells(self, current_neighbors):
        neighbor = self.get_hidden_cells_list(current_neighbors)
        for i in neighbor:
            obj = self.get_cur_cell_instance(i)
            obj.status = 1  # whether or not it is a mine or safe
            self.mine_cells.append(i)
            self.unvisited_cells.remove( i )
            if i in self.traverse_cells:
                self.traverse_cells.remove( i )
            color = (255, 255, 255)
            index_i = i[0]
            index_j = i[1]
            self.environment_obj.color_cell('', index_i, index_j, 'flag')
        return neighbor

    # Returns a list of safe neighbors to traverse - it is used in process_current_cell function and it returns the list to that function
    def flag_cells_as_safe(self, current_neighbors):
        neighbor = self.get_hidden_cells_list(current_neighbors)
        for i in neighbor:
            obj = self.get_cur_cell_instance(i)
            obj.status = 1  # whether or not it is a mine or safe
            obj.status = 0  # whether or not it is a mine or safe
        return neighbor


    # Functionality: This function takes a list, and uses process_current_cell to process each cell
    def traverse_board(self, list_cells):
        print("About to start traverse_board")
        # this will make sure all cells from the board are either flagged, or marked safe or as mine
        while self.unvisited_cells:
            print(self.traverse_cells)
            time.sleep(0.2)
            self.cell_traverse_list(list_cells)
            if self.traverse_cells:
                index = self.traverse_cells.pop(0)
                index_board_i = index[0]
                index_board_j = index[1]
                list_cells = self.process_current_cell(index_board_i, index_board_j)
            else:
                self.traverse_cells.append( self.unvisited_cells.pop() )


        if not self.unvisited_cells:
            print("EXITING $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

    # This funcadds new list safe neighbors that needs to be explored to an already existing list with cells
    def cell_traverse_list(self,list_cells):
        if len(list_cells) > 0:
            for i in list_cells:
                if i not in self.traverse_cells:
                    self.traverse_cells.append(i)



    # we will use the idea that any cells A + B + C = 0 (A,B,C are all different cells) are non mine cells
    # A + B + C = 3 will give us mine variables
    # a + b + b = total variables which is 3
    # it can be a + b = 2
    # and if not figurable then we simply move on to the next mine leaving this mine for future checking
    # Knowledge base:
    # we will be storing each equations and cell positions in the knowledge base so they can be used, changed and so on
    # whenever a mine is found go back in knowledge base and check if any flagged mine is next to it.
    # then compute for it to check

    # funcs i need: function that checks number of revealed cells.
    # func that returns index of revealed cells with clue values - neighbor cells


    # you require two list to process cells - one list that contains all neighbors and one list that contains only current neighbors to process
    # you need to have a function that returns list of current neighbors in descending order so first it determines safe/mine on that
    # if not determinable then move to the next one and so on

    # This checks that there are no duplicates in the knowledge base for the equations that are formed
    def check_duplicate(self, var_list, eq_length): # var_list will have [ var1_var2_var3 ]

        # Note: For future reference: if you are seeing problem, try the update duplicate feature
        # check_duplicate(self, var_list, eq_length, CLUE)
        # if a duplicate is found, remove the duplicate or update it with new clue

        if len(var_list) == 1:
            var_1 = var_list[0]
            # print("bbbbbbbbb", var_list)
            # print(var_1)

        if len(var_list) == 2:
            var_1 = var_list[0]
            var_2 = var_list[1]
            # print("bbbbbbbbb", var_list)
            # print(var_1)
            # print(var_2)

        if len(var_list) == 3:
            var_1 = var_list[0]
            var_2 = var_list[1]
            var_3 = var_list[2]
            # print("bbbbbbbbb", var_list)
            # print(var_1)
            # print(var_2)
            # print(var_3)


        # if one var eq_length = 1
        # if two var eq_length = 2
        # if three var eq_length = 3



        if eq_length == 1:
            if ( [var_1, 0] in self.knowledge_base) :
                return False
            if ( [var_1, 1] in self.knowledge_base) :
                return False
            if ( [var_1, 2] in self.knowledge_base) :
                return False
            if ( [var_1, 3] in self.knowledge_base) :
                return False
            if ( [var_1, 4] in self.knowledge_base) :
                return False
            if ( [var_1, 5] in self.knowledge_base) :
                return False
            if ( [var_1, 6] in self.knowledge_base) :
                return False
            if ( [var_1, 7] in self.knowledge_base) :
                return False
            if ( [var_1, 8] in self.knowledge_base) :
                return False
            # if ([var_1, 0] not in self.knowledge_base) and \
            #         ([var_1, 1] not in self.knowledge_base) and \
            #         ([var_1, 2] not in self.knowledge_base) and \
            #         ([var_1, 3] not in self.knowledge_base) and \
            #         ([var_1, 4] not in self.knowledge_base) and \
            #         ([var_1, 5] not in self.knowledge_base) and \
            #         ([var_1, 6] not in self.knowledge_base) and \
            #         ([var_1, 7] not in self.knowledge_base) and \
            #         ([var_1, 8] not in self.knowledge_base):
            #     return True

        if eq_length == 2:
            if ( [var_1, var_2, 0] in self.knowledge_base) :
                return False
            if ( [var_1, var_2, 1] in self.knowledge_base) :
                return False
            if ( [var_1, var_2, 2] in self.knowledge_base) :
                return False
            if ( [var_1, var_2, 3] in self.knowledge_base) :
                return False
            if ( [var_1, var_2, 4] in self.knowledge_base) :
                return False
            if ( [var_1, var_2, 5] in self.knowledge_base) :
                return False
            if ( [var_1, var_2, 5] in self.knowledge_base) :
                return False
            if ( [var_1, var_2, 5] in self.knowledge_base) :
                return False
            if ( [var_1, var_2, 8] in self.knowledge_base) :
                return False
            # if ([var_1, var_2, 0] not in self.knowledge_base) and \
            #         ( [var_1, var_2, 1] not in self.knowledge_base) and \
            #         ( [var_1, var_2, 2] not in self.knowledge_base) and \
            #         ( [var_1, var_2, 3] not in self.knowledge_base) and \
            #         ( [var_1, var_2, 4] not in self.knowledge_base) and \
            #         ( [var_1, var_2, 5] not in self.knowledge_base) and \
            #         ( [var_1, var_2, 6] not in self.knowledge_base) and \
            #         ( [var_1, var_2, 7] not in self.knowledge_base) and \
            #         ( [var_1, var_2, 8] not in self.knowledge_base):
            #     return True

        if eq_length == 3:
            if ( [var_1, var_2, var_3, 0] in self.knowledge_base) :
                return False
            if ( [var_1, var_2, var_3, 1] in self.knowledge_base) :
                return False
            if ( [var_1, var_2, var_3, 2] in self.knowledge_base) :
                return False
            if ( [var_1, var_2, var_3, 3] in self.knowledge_base) :
                return False
            if ( [var_1, var_2, var_3, 4]in self.knowledge_base) :
                return False
            if ( [var_1, var_2, var_3, 5] in self.knowledge_base) :
                return False
            if ( [var_1, var_2, var_3, 6] in self.knowledge_base) :
                return False
            if ( [var_1, var_2, var_3, 7] in self.knowledge_base) :
                return False
            if ( [var_1, var_2, var_3, 8] in self.knowledge_base) :
                return False

            # if ([var_1, var_2, 0] not in self.knowledge_base) and \
            #         ( [var_1, var_2, var_3, 1] not in self.knowledge_base) and \
            #         ( [var_1, var_2, var_3, 2] not in self.knowledge_base) and \
            #         ( [var_1, var_2, var_3, 3] not in self.knowledge_base) and \
            #         ( [var_1, var_2, var_3, 4] not in self.knowledge_base) and \
            #         ( [var_1, var_2, var_3, 5] not in self.knowledge_base) and \
            #         ( [var_1, var_2, var_3, 6] not in self.knowledge_base) and \
            #         ( [var_1, var_2, var_3, 7] not in self.knowledge_base) and \
            #         ( [var_1, var_2, var_3, 8] not in self.knowledge_base):
            #     return True
        return True


    # Functionality: takes in a list from current_cell that has to be determine and creates equation of the form a+b+c=clue, a = clue etc in the knowledge base
    def form_equation(self, list, clue, current_cell):
        # current_cell position is being passed to make equations

        # a b c
        # d   f
        # g h i

        cur_cell_i = current_cell[0]
        cur_cell_j = current_cell[1]

        #adds single index with clue e.g a = val , b = val etc
        print("aaaaaaaaaaaaaaaaaa", list)
        for index in list:
            if index in self.visited_cells: # checks if any neighbor is already visited - if it has been revealed then we remove it from the list before processing it
                list.remove(index)
            #if [ index , clue] not in self.knowledge_base:  # checks if neighbor list does not exist in knowledge base
            status = self.check_duplicate( [ index ], 1)
            if status:
                self.knowledge_base.append([index, clue])
            # if ( [index, 0] not in self.knowledge_base ) and \
            #         ([index, 1] not in self.knowledge_base) and \
            #         ([index, 2] not in self.knowledge_base) and\
            #         ([index, 3] not in self.knowledge_base) and \
            #         ([index, 4] not in self.knowledge_base) and \
            #         ([index, 5] not in self.knowledge_base) and \
            #         ([index, 6] not in self.knowledge_base) and \
            #         ([index, 7] not in self.knowledge_base) and \
            #         ([index, 8] not in self.knowledge_base):
            #     self.knowledge_base.append( [ index , clue] )

        i = current_cell[0]
        j = current_cell[1]

        # a b c
        # d   f
        # g h i

        top_left = [ i - 1, j - 1 ]
        top = [ i - 1, j ]
        top_right = [ i - 1, j + 1 ]

        mid_left = [ i, j - 1 ]
        mid_right = [ i, j + 1 ]

        bottom_left = [ i + 1, j - 1 ]
        bottom = [ i + 1, j ]
        bottom_right = [ i + 1, j + 1 ]

        # Top row
        if ( top_left in list ) and ( top in list ):   # a + b
            equation = [top_left, top, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate( [top_left, top], 2)
                if status:
                    self.knowledge_base.append(equation)
                #self.knowledge_base.append(equation)
                #self.knowledge_base.append('top row a + b')

        if ( top in list ) and ( top_right in list ):   # b + c
            equation = [top, top_right, clue]
            if equation not in self.knowledge_base:
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([top, top_right], 2)
                    if status:
                        self.knowledge_base.append(equation)
                #self.knowledge_base.append(equation)
                #self.knowledge_base.append('top row b + c')

        if ( top_left in list ) and ( top in list ) and ( top_right in list ):   # a + b + c
            equation = [ top_left , top, top_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_left, top, top_right], 3)
                if status:
                    self.knowledge_base.append(equation)
                #self.knowledge_base.append(equation)
                #self.knowledge_base.append('top row # a + b + c')

        # bottom row
        if ( bottom_left in list ) and ( bottom in list ):   # a + b
            equation = [ bottom_left, bottom, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([bottom_left, bottom], 2)
                if status:
                    self.knowledge_base.append(equation)
                #self.knowledge_base.append(equation)
                #self.knowledge_base.append('bottom row # a + b')

        if ( bottom in list ) and ( bottom_right in list ):   # b + c
            equation = [ bottom, bottom_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([bottom, bottom_right], 2)
                if status:
                    self.knowledge_base.append(equation)
                #self.knowledge_base.append(equation)
                #self.knowledge_base.append('bottom row # b + c')

        if ( bottom_left in list ) and ( bottom in list ) and ( bottom_right in list ):   # a + b + c
            equation = [ bottom_left , bottom, bottom_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([bottom_left, bottom, bottom_right], 3)
                if status:
                    self.knowledge_base.append(equation)
                #self.knowledge_base.append(equation)
                #self.knowledge_base.append('bottom row # a + b + c')

        # left col
        if ( top_left in list ) and ( mid_left in list ):   # a + d
            equation = [ top_left, mid_left, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_left, mid_left], 2)
                if status:
                    self.knowledge_base.append(equation)
                #self.knowledge_base.append(equation)
                #self.knowledge_base.append('left col # a + d')

        if ( mid_left in list ) and ( bottom_left in list ):   # d + g
            equation = [ mid_left, bottom_left, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([mid_left, bottom_left], 2)
                if status:
                    self.knowledge_base.append(equation)
                #self.knowledge_base.append(equation)
                #self.knowledge_base.append('left col # d + g')

        if ( top_left in list ) and ( mid_left in list ) and ( bottom_left in list ):   # a + d + g
            equation = [ top_left, mid_left, bottom_left, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_left, mid_left, bottom_left], 3)
                if status:
                    self.knowledge_base.append(equation)
                #self.knowledge_base.append(equation)
                #self.knowledge_base.append('left col # a + d + g')

        # right row
        if ( top_right in list ) and ( mid_right in list ):   # c + f
            equation = [ top_right, mid_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_right, mid_right], 2)
                if status:
                    self.knowledge_base.append(equation)
                #self.knowledge_base.append(equation)
                #self.knowledge_base.append('right col # c + f')

        if ( mid_right in list ) and ( bottom_right in list ):   # f + i
            equation = [ mid_right, bottom_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([mid_right, bottom_right], 2)
                if status:
                    self.knowledge_base.append(equation)
                #self.knowledge_base.append(equation)
                #self.knowledge_base.append('right col # f + i')

        if ( top_right in list ) and ( mid_right in list ) and ( bottom_right in list ):   # c + f + i
            equation = [ top_right, mid_right, bottom_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_right, mid_right, bottom_right], 3)
                if status:
                    self.knowledge_base.append(equation)
                #self.knowledge_base.append(equation)
                #self.knowledge_base.append('right col # c + f + i')

        for i in self.knowledge_base:
            print(i)

        print('----')

    # Functionality: When a cell has been revealed - go through knowledge base and delete the var from equations
    def delete_var(self, list, clue, delete_cell):
        print()


    # Functionality: checks current_cell neighbors and determine which cell is a hidden cell, which cell is already visited and what cell is a mine
    def process_current_cell_csp(self, i, j):
        print("-----")
        print(self.array_board)
        status = self.environment_obj.get_cell_value(self.array_board, i, j)
        obj = self.get_cur_cell_instance([i, j])
        # obj.current_position    # index in 2d array or matrix
        # obj.status  # whether or not it is a mine or safe
        # obj.clue    # if safe, the number of mines surrounding it indicated by the clue
        # obj.safe_n  # already revealed cells that are not flagged
        # obj.appearing_mines_in_neighbors    # number of flagged cells around it or mines
        # obj.cells_still_unexplored_in_neighbors # number of unexplored neighbors around it

        if status == 1:
            self.environment_obj.color_cell("", i, j, 1)  # This code marks the cell on GUI board
            self.mine_cells.append([i, j])
            if [i, j] in self.unvisited_cells:
                self.unvisited_cells.remove([i, j])

        if status != 1:
            self.visited_cells.append([i, j])  # adds current processed cell in list of visited cells if its safe
            if [i, j] in self.unvisited_cells:
                self.unvisited_cells.remove([i, j])  # removing index from unvisited cells
            obj.status = 0  # identifies the index as safe by marking it 0

            obj.clue = self.environment_obj.get_clue(self.array_board, i, j)    # assigns clue (clue is number of mines in adjacent neighbors

            self.environment_obj.color_cell(str(obj.clue), i, j, 0) # This code marks the cell on GUI boards

            current_neighbors = self.get_neighbors_current_cell(i, j) # gets a list of neighbors of current cells

            visited = self.get_visited_cells(current_neighbors) # In adjacent cells, returns a value for neighbors that are already visited/revealed - Returns just a value not cell indexs that are visited
            obj.safe_n = visited

            hidden = self.get_hidden_cells(current_neighbors)# In adjacent cells, returns a value for neighbors that are hidden/unrevealed cells - Returns just a value not cell indexs that are hidden
            obj.cells_still_unexplored_in_neighbors = hidden

            mines = self.get_mines_in_neighbor_cells(current_neighbors)# In adjacent cells, returns a value for neighbors that are mines - Returns just a value not cell indexs that are flagged or mines
            obj.appearing_mines_in_neighbors = mines

            obj.print_cell_info()   # To print each cell info

            # code below is for the basic algorithm from the description
            a = self.mine_estimate(obj.clue, mines, hidden) # this checks the mine code from basic algorithm in the description
            if a == True:
                self.flag_cells(current_neighbors)
            else:
                a = self.safe_estimator(obj.clue, visited, hidden)
                ret_list = self.flag_cells_as_safe(current_neighbors)
                return ret_list

        return []

    def csp_solver(self):
        print()

###################### CODE FOR BASIC ALGORITHM MIGHT HAVE TO COME BACK TO IT FOR GRAPH GENERATION REPORT

    # # Functionality: checks current_cell neighbors and determine which cell is a hidden cell, which cell is already visited and what cell is a mine
    # def process_current_cell(self, i, j):
    #     print("-----")
    #     print(self.array_board)
    #     status = self.environment_obj.get_cell_value(self.array_board, i, j)
    #     obj = self.get_cur_cell_instance([i, j])
    #     # obj.current_position    # index in 2d array or matrix
    #     # obj.status  # whether or not it is a mine or safe
    #     # obj.clue    # if safe, the number of mines surrounding it indicated by the clue
    #     # obj.safe_n  # already revealed cells that are not flagged
    #     # obj.appearing_mines_in_neighbors    # number of flagged cells around it or mines
    #     # obj.cells_still_unexplored_in_neighbors # number of unexplored neighbors around it
    #
    #     if status == 1:
    #         self.environment_obj.color_cell("", i, j, 1)  # This code marks the cell on GUI board
    #         self.mine_cells.append([i, j])
    #         if [i, j] in self.unvisited_cells:
    #             self.unvisited_cells.remove([i, j])
    #
    #     if status != 1:
    #         self.visited_cells.append([i, j])  # adds current processed cell in list of visited cells if its safe
    #         if [i, j] in self.unvisited_cells:
    #             self.unvisited_cells.remove([i, j])  # removing index from unvisited cells
    #         obj.status = 0  # identifies the index as safe by marking it 0
    #
    #         obj.clue = self.environment_obj.get_clue(self.array_board, i, j)    # assigns clue (clue is number of mines in adjacent neighbors
    #
    #         self.environment_obj.color_cell(str(obj.clue), i, j, 0) # This code marks the cell on GUI boards
    #
    #         current_neighbors = self.get_neighbors_current_cell(i, j) # gets a list of neighbors of current cells
    #
    #         visited = self.get_visited_cells(current_neighbors) # In adjacent cells, returns a value for neighbors that are already visited/revealed - Returns just a value not cell indexs that are visited
    #         obj.safe_n = visited
    #
    #         hidden = self.get_hidden_cells(current_neighbors)# In adjacent cells, returns a value for neighbors that are hidden/unrevealed cells - Returns just a value not cell indexs that are hidden
    #         obj.cells_still_unexplored_in_neighbors = hidden
    #
    #         mines = self.get_mines_in_neighbor_cells(current_neighbors)# In adjacent cells, returns a value for neighbors that are mines - Returns just a value not cell indexs that are flagged or mines
    #         obj.appearing_mines_in_neighbors = mines
    #
    #         obj.print_cell_info()   # To print each cell info
    #
    #         # code below is for the basic algorithm from the description
    #         a = self.mine_estimate(obj.clue, mines, hidden) # this checks the mine code from basic algorithm in the description
    #         if a == True:
    #             self.flag_cells(current_neighbors)
    #         else:
    #             a = self.safe_estimator(obj.clue, visited, hidden)
    #             ret_list = self.flag_cells_as_safe(current_neighbors)
    #             return ret_list
    #
    #     return []
    #
    #
    # # If a cell is flagged then this function will flag the cell
    # def flag_cells(self, current_neighbors):
    #     neighbor = self.get_hidden_cells_list(current_neighbors)
    #     for i in neighbor:
    #         obj = self.get_cur_cell_instance(i)
    #         obj.status = 1  # whether or not it is a mine or safe
    #         self.mine_cells.append(i)
    #         self.unvisited_cells.remove( i )
    #         if i in self.traverse_cells:
    #             self.traverse_cells.remove( i )
    #         color = (255, 255, 255)
    #         index_i = i[0]
    #         index_j = i[1]
    #         self.environment_obj.color_cell('', index_i, index_j, 'flag')
    #     return neighbor
    #
    # # Returns a list of safe neighbors to traverse - it is used in process_current_cell function and it returns the list to that function
    # def flag_cells_as_safe(self, current_neighbors):
    #     neighbor = self.get_hidden_cells_list(current_neighbors)
    #     for i in neighbor:
    #         obj = self.get_cur_cell_instance(i)
    #         obj.status = 1  # whether or not it is a mine or safe
    #         obj.status = 0  # whether or not it is a mine or safe
    #     return neighbor
    #
    #
    # # Functionality: This function takes a list, and uses process_current_cell to process each cell
    # def traverse_board(self, list_cells):
    #     print("About to start traverse_board")
    #     # this will make sure all cells from the board are either flagged, or marked safe or as mine
    #     while self.unvisited_cells:
    #         print(self.traverse_cells)
    #         time.sleep(0.2)
    #         self.cell_traverse_list(list_cells)
    #         if self.traverse_cells:
    #             index = self.traverse_cells.pop(0)
    #             index_board_i = index[0]
    #             index_board_j = index[1]
    #             list_cells = self.process_current_cell(index_board_i, index_board_j)
    #         else:
    #             self.traverse_cells.append( self.unvisited_cells.pop() )
    #
    #
    #     if not self.unvisited_cells:
    #         print("EXITING $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    #
    # # This funcadds new list safe neighbors that needs to be explored to an already existing list with cells
    # def cell_traverse_list(self,list_cells):
    #     if len(list_cells) > 0:
    #         for i in list_cells:
    #             if i not in self.traverse_cells:
    #                 self.traverse_cells.append(i)
