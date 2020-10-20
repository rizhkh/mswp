import numpy as np
# import collections
# import random
# from mswp.boardenvironment import environment
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


class Agnt:
    # all_cells = dict() #np.zeros((0, 0), dtype=int) # this list is total cells on the board
    all_cells = []  # this list is total cells on the board  # This would store the object of each cell that is visited
    # we use this list to access all stored information
    visited_cells = []  # just stores index of cells that are visited
    mine_cells = []  # list of cells that are mines and they have been revealed - not hidden on board anymore

    unvisited_cells = []

    traverse_cells = []  # list of cells that needs to be processed / traversed

    knowledge_base = []
    # Content is stored in knowledge in this format:
    # [Var,Value] -> Var = Value
    # to look up just a var make sure to look up by len ==2

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

    # This lets agent use environment methods to get cell values and use various other information for its knowledge
    # base that agent should know
    def set_environment_obj(self, obj):
        self.environment_obj = obj

    # this function runs just once in the start and this is to initialize an object and set value of 0 for all
    # unrevealed cells
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

    # returns the object instance of the current cell from the list where it is stored - Used in process curr cell to
    # get the object of cell we are processing and update info
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
    def get_visited_cells(self, passed_list):
        val = 0
        for i in passed_list:
            if i in self.visited_cells:
                val += 1
        return val

    # Returns number of hidden cells in neighbors of current cell
    def get_hidden_cells(self, passed_list):
        val = 0
        for i in passed_list:
            if (i not in self.visited_cells) and (i not in self.mine_cells):
                val += 1
        return val

    # Returns list of hidden cells that are neighbors of current cell
    def get_hidden_cells_list(self, passed_list):
        ret_list = []
        for i in passed_list:
            if (i not in self.visited_cells) and (i not in self.mine_cells):
                ret_list.append(i)
        return ret_list

    # Returns number of mine cells as neighbors of current cell
    def get_mines_in_neighbor_cells(self, passed_list):
        val = 0
        for i in passed_list:
            if i in self.mine_cells:
                val += 1
        return val

    def mine_estimate(self, clue, tot_mines, hidden_neighbor_mine):
        # print(clue, " , ", (hidden_neighbor_mine + tot_mines))
        # if (clue - hidden_neighbor_mine) == (tot_mines):
        # if (clue-tot_mines) == (hidden_neighbor_mine):
        if clue == (hidden_neighbor_mine + tot_mines):  # use this one
            return True
        return False

    def safe_estimator(self, clue, tot_rev_neighbors, hidden_neighbor_mine):
        # if ((8 - clue) - tot_rev_neighbors) == (hidden_neighbor_mine):
        if (8 - clue) == (hidden_neighbor_mine + tot_rev_neighbors):  # use this one
            return True
        return False

    def process_current_cell(self, i, j):
    ## Functionality: checks current_cell neighbors and determine which cell is a hidden cell, which cell is already
    ## visited and what cell is a mine
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

            obj.clue = self.environment_obj.get_clue(self.array_board, i,
                                                     j)  # assigns clue (clue is number of mines in adjacent neighbors

            self.environment_obj.color_cell(str(obj.clue), i, j, 0)  # This code marks the cell on GUI boards

            current_neighbors = self.get_neighbors_current_cell(i, j)  # gets a list of neighbors of current cells

            # In adjacent cells, returns a value for neighbors that are already visited/revealed
            # Returns just a value not cell indexs that are visited
            visited = self.get_visited_cells(current_neighbors)

            obj.safe_n = visited

            # In adjacent cells, returns a value for neighbors that are hidden/unrevealed cells - Returns just a value
            # not cell indexs that are hidden
            hidden = self.get_hidden_cells(current_neighbors)
            obj.cells_still_unexplored_in_neighbors = hidden

            # In adjacent cells, returns a value for neighbors that are mines - Returns just a value not cell indexs
            # that are flagged or mines
            mines = self.get_mines_in_neighbor_cells(current_neighbors)
            obj.appearing_mines_in_neighbors = mines

            obj.print_cell_info()  # To print each cell info

            # code below is for the basic algorithm from the description
            a = self.mine_estimate(obj.clue, mines,
                                   hidden)  # this checks the mine code from basic algorithm in the description
            if a:
                self.flag_cells(current_neighbors)
            else:
                self.safe_estimator(obj.clue, visited, hidden)
                ret_list = self.flag_cells_as_safe(current_neighbors)

                cell_to_delete = [i, j]
                self.delete_var(cell_to_delete)

                return ret_list

        return []


    def flag_cells(self, current_neighbors):
        # If a cell is flagged then this function will flag the cell
        neighbor = self.get_hidden_cells_list(current_neighbors)
        for i in neighbor:
            obj = self.get_cur_cell_instance(i)
            obj.status = 1  # whether or not it is a mine or safe
            self.mine_cells.append(i)
            self.unvisited_cells.remove(i)
            if i in self.traverse_cells:
                self.traverse_cells.remove(i)
            # color = (255, 255, 255)
            index_i = i[0]
            index_j = i[1]
            self.environment_obj.color_cell('', index_i, index_j, 'flag')
        return neighbor

    # Returns a list of safe neighbors to traverse - it is used in process_current_cell function and it returns the
    # list to that function
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

                # Inference method will go here - it will determine here if flag or safe
                flag_or_safe_val = 0
                list_cells = self.process_current_cell_csp(index_board_i, index_board_j, flag_or_safe_val)
                if list_cells:  # If not empty()
                    val = self.get_clue(self.board_array, index_board_i, index_board_j)
                    self.form_equation(list_cells, val, [index_board_i, index_board_j])
            else:
                self.traverse_cells.append(self.unvisited_cells.pop())

        if not self.unvisited_cells:
            print("EXITING $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

    # This funcadds new list safe neighbors that needs to be explored to an already existing list with cells
    def cell_traverse_list(self, list_cells):
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
    def check_duplicate(self, var_list, eq_length):  # var_list will have [ var1_var2_var3 ]
        var_1 = var_2 = var_3 = 0
        # note: eq_length is the length of the list format e.g ['A'] - length 1, [A,B] - length 2 and so on

        if len(var_list) == 1:
            var_1 = var_list[0]

        if len(var_list) == 2:
            var_1 = var_list[0]
            var_2 = var_list[1]

        if len(var_list) == 3:
            var_1 = var_list[0]
            var_2 = var_list[1]
            var_3 = var_list[2]

        if eq_length == 1:
            if ([var_1, 0] in self.knowledge_base):
                return False
            if ([var_1, 1] in self.knowledge_base):
                return False
            if ([var_1, 2] in self.knowledge_base):
                return False
            if ([var_1, 3] in self.knowledge_base):
                return False
            if ([var_1, 4] in self.knowledge_base):
                return False
            if ([var_1, 5] in self.knowledge_base):
                return False
            if ([var_1, 6] in self.knowledge_base):
                return False
            if ([var_1, 7] in self.knowledge_base):
                return False
            if ([var_1, 8] in self.knowledge_base):
                return False

        if eq_length == 2:
            if ([var_1, var_2, 0] in self.knowledge_base):
                return False
            if ([var_1, var_2, 1] in self.knowledge_base):
                return False
            if ([var_1, var_2, 2] in self.knowledge_base):
                return False
            if ([var_1, var_2, 3] in self.knowledge_base):
                return False
            if ([var_1, var_2, 4] in self.knowledge_base):
                return False
            if ([var_1, var_2, 5] in self.knowledge_base):
                return False
            if ([var_1, var_2, 5] in self.knowledge_base):
                return False
            if ([var_1, var_2, 5] in self.knowledge_base):
                return False
            if ([var_1, var_2, 8] in self.knowledge_base):
                return False

        if eq_length == 3:
            if ([var_1, var_2, var_3, 0] in self.knowledge_base):
                return False
            if ([var_1, var_2, var_3, 1] in self.knowledge_base):
                return False
            if ([var_1, var_2, var_3, 2] in self.knowledge_base):
                return False
            if ([var_1, var_2, var_3, 3] in self.knowledge_base):
                return False
            if ([var_1, var_2, var_3, 4] in self.knowledge_base):
                return False
            if ([var_1, var_2, var_3, 5] in self.knowledge_base):
                return False
            if ([var_1, var_2, var_3, 6] in self.knowledge_base):
                return False
            if ([var_1, var_2, var_3, 7] in self.knowledge_base):
                return False
            if ([var_1, var_2, var_3, 8] in self.knowledge_base):
                return False
        return True

    # helper function for update_duplicate to update duplicate vars
    def duplicate_funct(self, var, clue, length):
        if length == 1:
            self.knowledge_base.remove(var)
            var[1] = clue
            self.knowledge_base.append(var)

        if length == 2:
            self.knowledge_base.remove(var)
            var[2] = clue
            self.knowledge_base.append(var)

        if length == 3:
            self.knowledge_base.remove(var)
            var[3] = clue
            self.knowledge_base.append(var)
        return True

    # This cupdates already existing vars and eqs in the knowledge base
    def update_duplicate(self, var_list, eq_length, new_clue):  # var_list will have [ var1_var2_var3 ]
        var_1 = var_2 = var_3 = 0
        if len(var_list) == 1:
            var_1 = var_list[0]

        if len(var_list) == 2:
            var_1 = var_list[0]
            var_2 = var_list[1]

        if len(var_list) == 3:
            var_1 = var_list[0]
            var_2 = var_list[1]
            var_3 = var_list[2]

        if eq_length == 1:
            if ([var_1, 0] in self.knowledge_base):
                self.duplicate_funct([var_1, 0], new_clue, 1)

            if ([var_1, 1] in self.knowledge_base):
                self.duplicate_funct([var_1, 1], new_clue, 1)

            if ([var_1, 2] in self.knowledge_base):
                self.duplicate_funct([var_1, 2], new_clue, 1)

            if ([var_1, 3] in self.knowledge_base):
                self.duplicate_funct([var_1, 3], new_clue, 1)

            if ([var_1, 4] in self.knowledge_base):
                self.duplicate_funct([var_1, 4], new_clue, 1)

            if ([var_1, 5] in self.knowledge_base):
                self.duplicate_funct([var_1, 5], new_clue, 1)

            if ([var_1, 6] in self.knowledge_base):
                self.duplicate_funct([var_1, 6], new_clue, 1)

            if ([var_1, 7] in self.knowledge_base):
                self.duplicate_funct([var_1, 7], new_clue, 1)

            if ([var_1, 8] in self.knowledge_base):
                self.duplicate_funct([var_1, 8], new_clue, 1)

        if eq_length == 2:
            if ([var_1, var_2, 0] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, 0], new_clue, 2)

            if ([var_1, var_2, 1] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, 1], new_clue, 2)

            if ([var_1, var_2, 2] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, 2], new_clue, 2)

            if ([var_1, var_2, 3] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, 3], new_clue, 2)

            if ([var_1, var_2, 4] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, 4], new_clue, 2)

            if ([var_1, var_2, 5] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, 5], new_clue, 2)

            if ([var_1, var_2, 5] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, 6], new_clue, 2)

            if ([var_1, var_2, 5] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, 7], new_clue, 2)

            if ([var_1, var_2, 8] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, 8], new_clue, 2)

        if eq_length == 3:
            if ([var_1, var_2, var_3, 0] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, var_3, 0], new_clue, 3)

            if ([var_1, var_2, var_3, 1] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, var_3, 1], new_clue, 3)

            if ([var_1, var_2, var_3, 2] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, var_3, 2], new_clue, 3)

            if ([var_1, var_2, var_3, 3] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, var_3, 3], new_clue, 3)

            if ([var_1, var_2, var_3, 4] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, var_3, 4], new_clue, 3)

            if ([var_1, var_2, var_3, 5] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, var_3, 5], new_clue, 3)

            if ([var_1, var_2, var_3, 6] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, var_3, 6], new_clue, 3)

            if ([var_1, var_2, var_3, 7] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, var_3, 7], new_clue, 3)

            if ([var_1, var_2, var_3, 8] in self.knowledge_base):
                self.duplicate_funct([var_1, var_2, var_3, 8], new_clue, 3)
        return True

    # Functionality: takes in a list from current_cell that has to be determine and creates equation of
    # the form a+b+c=clue, a = clue etc in the knowledge base
    def form_equation(self, passed_list, clue, current_cell):
        clue = [clue]
        # passed_list is the list of hidden neighbor cells
        # current_cell position is being passed to make equations of the neighboring cells as current_cell is the cell in being queried

        # a b c
        # d   f
        # g h i

        # adds single index with clue e.g a = val , b = val etc
        for index in passed_list:
            # checks if any neighbor is already visited - if it has been revealed then we remove it from the list before
            # processing it
            if index in self.visited_cells:
                passed_list.remove(index)
            # if [ index , clue] not in self.knowledge_base:  # checks if neighbor list does not exist in knowledge base
            status = self.check_duplicate([index], 1)
            # if status is false call the update value method
            if status:
                self.knowledge_base.append([index, clue])
            else:
                self.update_duplicate(index, 1, clue)


        i = current_cell[0]
        j = current_cell[1]

        # a b c
        # d   f
        # g h i

        top_left = [i - 1, j - 1]
        top = [i - 1, j]
        top_right = [i - 1, j + 1]

        mid_left = [i, j - 1]
        mid_right = [i, j + 1]

        bottom_left = [i + 1, j - 1]
        bottom = [i + 1, j]
        bottom_right = [i + 1, j + 1]

        # Top row
        if (top_left in passed_list) and (top in passed_list):  # a + b
            equation = [top_left, top, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_left, top], 2)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([top_left, top], 2, clue)

                # self.knowledge_base.append(equation)
                # self.knowledge_base.append('top row a + b')

        if (top in passed_list) and (top_right in passed_list):  # b + c
            equation = [top, top_right, clue]
            if equation not in self.knowledge_base:
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([top, top_right], 2)
                    if status:
                        self.knowledge_base.append(equation)
                    else:
                        self.update_duplicate([top, top_right], 2, clue)
                # self.knowledge_base.append(equation)
                # self.knowledge_base.append('top row b + c')

        if (top_left in passed_list) and (top in passed_list) and (top_right in passed_list):  # a + b + c
            equation = [top_left, top, top_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_left, top, top_right], 3)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([top_left, top, top_right], 3, clue)

                # self.knowledge_base.append(equation)
                # self.knowledge_base.append('top row # a + b + c')

        # bottom row
        if (bottom_left in passed_list) and (bottom in passed_list):  # a + b
            equation = [bottom_left, bottom, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([bottom_left, bottom], 2)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([bottom_left, bottom], 2, clue)

                # self.knowledge_base.append(equation)
                # self.knowledge_base.append('bottom row # a + b')

        if (bottom in passed_list) and (bottom_right in passed_list):  # b + c
            equation = [bottom, bottom_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([bottom, bottom_right], 2)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([bottom, bottom_right], 2, clue)

                # self.knowledge_base.append(equation)
                # self.knowledge_base.append('bottom row # b + c')

        if (bottom_left in passed_list) and (bottom in passed_list) and (bottom_right in passed_list):  # a + b + c
            equation = [bottom_left, bottom, bottom_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([bottom_left, bottom, bottom_right], 3)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([bottom_left, bottom, bottom_right], 3, clue)
                # self.knowledge_base.append(equation)
                # self.knowledge_base.append('bottom row # a + b + c')

        # left col
        if (top_left in passed_list) and (mid_left in passed_list):  # a + d
            equation = [top_left, mid_left, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_left, mid_left], 2)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([top_left, mid_left], 2, clue)

                # self.knowledge_base.append(equation)
                # self.knowledge_base.append('left col # a + d')

        if (mid_left in passed_list) and (bottom_left in passed_list):  # d + g
            equation = [mid_left, bottom_left, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([mid_left, bottom_left], 2)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([mid_left, bottom_left], 2, clue)
                # self.knowledge_base.append(equation)
                # self.knowledge_base.append('left col # d + g')

        if (top_left in passed_list) and (mid_left in passed_list) and (bottom_left in passed_list):  # a + d + g
            equation = [top_left, mid_left, bottom_left, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_left, mid_left, bottom_left], 3)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([top_left, mid_left, bottom_left], 3, clue)
                # self.knowledge_base.append(equation)
                # self.knowledge_base.append('left col # a + d + g')

        # right row
        if (top_right in passed_list) and (mid_right in passed_list):  # c + f
            equation = [top_right, mid_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_right, mid_right], 2)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([top_right, mid_right], 2, clue)
                # self.knowledge_base.append(equation)
                # self.knowledge_base.append('right col # c + f')

        if (mid_right in passed_list) and (bottom_right in passed_list):  # f + i
            equation = [mid_right, bottom_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([mid_right, bottom_right], 2)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([mid_right, bottom_right], 2, clue)
                # self.knowledge_base.append(equation)
                # self.knowledge_base.append('right col # f + i')

        if (top_right in passed_list) and (mid_right in passed_list) and (bottom_right in passed_list):  # c + f + i
            equation = [top_right, mid_right, bottom_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_right, mid_right, bottom_right], 3)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([top_right, mid_right, bottom_right], 3, clue)
                # self.knowledge_base.append(equation)
                # self.knowledge_base.append('right col # c + f + i')

        #form_equation
        # for i in self.knowledge_base:
        #     print(i) # , " - Length : " , len(i) )

        print('----')

    # Helper function for delete var
    def delete_var_helper(self, equation, cell):
        if cell in equation:
            for var in equation:
                if cell == var:
                    equation.remove(var)
                    return equation
            # status = isinstance(index, list)
            # # One thing to consider - when you delete var you also delete the single variable assignment not just
            # # from the equation e.g A = 0
            # if status:
            #     i = index[0]
            #     j = index[1]
            #     if i == cell[0] and j == cell[1]:  # when a variable to delete is found in equation delete
            #         equation.remove(index)
            #         return equation
        return []

    # Functionality: When a cell has been revealed - go through knowledge base and delete the var from equations
    def delete_var(self, cell_to_delete):
        # iterates through every single thing in knowledge base to remove that variable from every equation
        for index in self.knowledge_base:   # index is the equations in knowledge base
            ret_list = self.delete_var_helper(index, cell_to_delete)
            if len(ret_list) == 1:
                self.knowledge_base.remove(index)
            if len(ret_list) > 2:
                # print("Returned list is :                   " ,  ret_list)
                self.knowledge_base.remove(index)
                self.knowledge_base.append(ret_list)
            # if len(ret_list) > 1:
            #     # print("Returned list is :                   " ,  ret_list)
            #     self.knowledge_base.remove(index)
            #     self.knowledge_base.append(ret_list)

        # # not sure If i need this piece of code:
        # if [0] in self.knowledge_base:
        #     self.knowledge_base.remove([0])
        # if [1] in self.knowledge_base:
        #     self.knowledge_base.remove([1])
        # if [2] in self.knowledge_base:
        #     self.knowledge_base.remove([2])
        # if [3] in self.knowledge_base:
        #     self.knowledge_base.remove([3])
        # if [4] in self.knowledge_base:
        #     self.knowledge_base.remove([4])
        # if [5] in self.knowledge_base:
        #     self.knowledge_base.remove([5])
        # if [6] in self.knowledge_base:
        #     self.knowledge_base.remove([6])
        # if [7] in self.knowledge_base:
        #     self.knowledge_base.remove([7])
        # if [8] in self.knowledge_base:
        #     self.knowledge_base.remove([8])

    # Functionality: checks current_cell neighbors and determine which cell is a hidden cell, which cell is already
    # visited and what cell is a mine
    def process_current_cell_csp(self, i, j):#, status):
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

            obj.clue = self.environment_obj.get_clue(self.array_board, i,
                                                     j)  # assigns clue (clue is number of mines in adjacent neighbors

            self.environment_obj.color_cell(str(obj.clue), i, j, 0)  # This code marks the cell on GUI boards

            current_neighbors = self.get_neighbors_current_cell(i, j)  # gets a list of neighbors of current cells

            # In adjacent cells, returns a value for neighbors that are already visited/revealed - Returns just a value
            # not cell indexs that are visited
            visited = self.get_visited_cells(
                current_neighbors)
            obj.safe_n = visited

            # In adjacent cells, returns a value for neighbors that are hidden/unrevealed cells - Returns just a value
            # not cell indexs that are hidden
            hidden = self.get_hidden_cells(
                current_neighbors)
            obj.cells_still_unexplored_in_neighbors = hidden

            # In adjacent cells, returns a value for neighbors that are mines - Returns just a value not cell indexs
            # that are flagged or mines
            mines = self.get_mines_in_neighbor_cells(
                current_neighbors)
            obj.appearing_mines_in_neighbors = mines

            obj.print_cell_info()  # To print each cell info

            # code below is for the basic algorithm from the description
            a = self.mine_estimate(obj.clue, mines,
                                   hidden)  # this checks the mine code from basic algorithm in the description
            if a == True:
                self.flag_cells(current_neighbors)
            else:
                a = self.safe_estimator(obj.clue, visited, hidden)
                ret_list = self.flag_cells_as_safe(current_neighbors)
                return ret_list

        return []

    # this func helps subset look at equation and return value of a+b or b+c from a+b+c equation
    def subset_helper(self, var_1,var_2):
        #print(" in subset helper -------")
        # a + b + c = 2 => (a+b) + c and a+b = 1 we can deduce that c would be flagged as c=1
        if len(var_2) > 1:
            eq_0 = [var_1, var_2, [0]]
            eq_1 = [var_1, var_2, [1]]
            eq_2 = [var_1, var_2, [2]]
            eq_3 = [var_1, var_2, [3]]
            eq_4 = [var_1, var_2, [4]]
            eq_5 = [var_1, var_2, [5]]
            eq_6 = [var_1, var_2, [6]]
            eq_7 = [var_1, var_2, [7]]
            eq_8 = [var_1, var_2, [8]]
            val = None

            if ( eq_0 in self.knowledge_base ):
                val = eq_0[-1]
                val = val[0]
                print("-------------------- true for eq0 : ",eq_0, "| Val is : ", val )

            if ( eq_1 in self.knowledge_base ):
                val = eq_1[-1]
                val = val[0]
                print("-------------------- true for eq 1 : ",eq_1, "| Val is : ", val )

            if ( eq_2 in self.knowledge_base ):
                val = eq_2[-1]
                val = val[0]
                print("-------------------- true for eq 2 : ",eq_2, "| Val is : ", val )

            if (eq_3 in self.knowledge_base):
                val = eq_3[-1]
                val = val[0]
                print("-------------------- true for eq 3 : ",eq_3, "| Val is : ", val )

            if ( eq_4 in self.knowledge_base ):
                val = eq_4[-1]
                val = val[0]
                print("-------------------- true for eq 4 : ",eq_4, "| Val is : ", val )

            if ( eq_5 in self.knowledge_base ):
                val = eq_5[-1]
                val = val[0]
                print("-------------------- true for eq 5 : ",eq_5, "| Val is : ", val )

            if (eq_6 in self.knowledge_base):
                val = eq_6[-1]
                val = val[0]
                print("-------------------- true for eq 6: ",eq_6, "| Val is : ", val )

            if ( eq_7 in self.knowledge_base ):
                val = eq_7[-1]
                val = val[0]
                print("-------------------- true for eq 7: ",eq_7, "| Val is : ", val )

            if( eq_8 in self.knowledge_base ):
                val = eq_8[-1]
                val = val[0]
                print("-------------------- true for eq 8: ",eq_8, "| Val is : ", val )
            return val
        return None

    def subset(self, passed_list, val):  # note: we are only for solving subset for 3 eqs for now
        if len(passed_list)>2:
            val = val[0]
            var_1 = passed_list[0]
            var_2 = passed_list[1]

            if len(passed_list) >= 4:
                ret_val = self.subset_helper(var_1,var_2) # returned value will be compared to value of complete equation
            print("Value from subset helper: " , ret_val)

            if ret_val != None:
                print("This equattion is being passed to subset ", passed_list)
                var_3 = val - ret_val
                if var_3 != 0:
                    sum = var_3 + ret_val
                    if sum == val:
                        return passed_list[2]
            else:
                var_2 = passed_list[1]
                var_3 = passed_list[2]
                ret_val = self.subset_helper(var_2, var_3)
                if ret_val != None:
                    print("This equattion is being passed to subset ", passed_list)
                    var_1 = val - ret_val
                    if var_1 != 0:
                        sum = var_1 + ret_val
                        if sum == val:
                            return passed_list[1]
        return False

    def equation_solver_csp(self, passed_list, length,passed_cell):
        # passed list is just the list with equations of neighbor cells of current cell to determine if safe or not
        # NOTE: SOLVE THIS: I AM GETTING VARIABLES THAT SHARE NEIGHBORS WITH OTHERS - GET EQUATIONS THAT ONLY SHARE
        var_that_are_true = []
        check = 0
        # note : index is the whole equation e.g [a,b,1] etc

        for index in passed_list:
            clue = index[-1]
            if len(index) >= 4: # a + b + c
                ret_val = self.subset(index, clue)
                print(ret_val)
                if ret_val != False:
                    print("Subset ============================")
                    print(ret_val)
                    var_that_are_true.append(index)
                    passed_list.remove(index)
                else:
                    print(" ret_val ====== FALSE")
                    sum = 3
                    if sum == clue[0]:
                        var_that_are_true.append(index)
                        passed_list.remove(index)
                        # just remove the true equation from passed list so it does not have to be solved again
                    else:
                        check = 1
        if check == 1:
            for index in passed_list:
                clue = index[-1]
                if len(index) == 3:
                    sum = 2
                    if sum == clue[0]:
                        var_that_are_true.append(index)
                        passed_list.remove(index)
        return var_that_are_true # MAKE SURE TO CHANGE THIS TO var_that_are_true ***********************************


    def csp_solver(self, neighbor_list,passed_cell):
        hidden_neighbors = self.get_hidden_cells_list(neighbor_list)

        final_list = []

        # print("current cell:", passed_cell)
        # for index in hidden_neighbors:  # iterate cell by cell e.g index is [0,1] then [0,2] then [0,3] etc
        #     ret_list = self.search_knowledge_base(index, hidden_neighbors)    # each hidden neighbor cell is prcoessed here
        #     print("equations from kb for each neighbor: " , ret_list)
        #     list_ans = self.equation_solver_csp(ret_list , len(hidden_neighbors), passed_cell)
        #     for i in list_ans:
        #         for j in i:
        #             if len(j) > 1:
        #                 if j not in final_list:
        #                     final_list.append(j)
        #     if final_list:
        #         #print("current cell : ", passed_cell)
        #         #print("var that should be flagged: ", final_list, " | length (hidden neigbors): ", len(hidden_neighbors))
        #         # print("^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        #         # print(final_list)
        #         # print(hidden_neighbors)
        #         # print("^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        #         for i in final_list:
        #             if i in hidden_neighbors:
        #                 hidden_neighbors.remove(i)


        print("current cell:", passed_cell)

        # Gets the csp equations
        eq_of_neighbor_cells = []  # This list contains csp eq from kb of required cells
        for index in hidden_neighbors:  # iterate cell by cell e.g index is [0,1] then [0,2] then [0,3] etc
            self.search_knowledge_base(index, hidden_neighbors , eq_of_neighbor_cells)    # each hidden neighbor cell is prcoessed here

        self.skb_helper(hidden_neighbors , eq_of_neighbor_cells)    # removes eq that have var not neighbors
        #print("equations from kb for each neighbor: " , eq_of_neighbor_cells)

        # Solves the CSP equations
        list_ans = self.equation_solver_csp(eq_of_neighbor_cells , len(hidden_neighbors), passed_cell)
        for i in list_ans:  # This for loop removes val from end of csp equation e.g [a,b,0] -> [a,b]
            for j in i:
                if len(j) > 1:
                    if j not in final_list:
                        final_list.append(j)

        if final_list:
            # for i in final_list:
            #     if i in hidden_neighbors:
            #         hidden_neighbors.remove(i)
            for i in final_list:
                if i in hidden_neighbors:
                    final_list.remove(i)

        print("Safe cell : ", hidden_neighbors)
        print(hidden_neighbors)
        self.flag_cells(final_list)

    # returns csp equations with required cell in it
    def search_knowledge_base(self, cell, listOfNeighbors, used_list):
        for i in self.knowledge_base:
            if cell in i:
                if i not in used_list:
                    used_list.append(i)

    def skb_helper(self, hidden_neigh, used_list):
        for i in used_list:
            if len(i)>2:
                for j in i:
                    if len(j)>1:
                        if j not in hidden_neigh:
                            if i in used_list:
                                used_list.remove(i)

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
