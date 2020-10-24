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
    mine_kb = []
    mines_left = 0
    # Content is stored in knowledge in this format:
    # [Var,Value] -> Var = Value
    # to look up just a var make sure to look up by len ==2

    flagged_cells = []

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
        self.mines_left = self.environment_obj.total_mines

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
    # returns a list of hidden cells in passed_list
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

    # def process_current_cell(self, i, j):
    # ## Functionality: checks current_cell neighbors and determine which cell is a hidden cell, which cell is already
    # ## visited and what cell is a mine
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
    #         obj.clue = self.environment_obj.get_clue(self.array_board, i,
    #                                                  j)  # assigns clue (clue is number of mines in adjacent neighbors
    #
    #         if obj.clue==0:
    #             self.environment_obj.color_cell('', i, j, 0)  # This code marks the cell on GUI boards
    #         else:
    #             self.environment_obj.color_cell(str(obj.clue), i, j, 0)  # This code marks the cell on GUI boards
    #
    #         current_neighbors = self.get_neighbors_current_cell(i, j)  # gets a list of neighbors of current cells
    #
    #         # In adjacent cells, returns a value for neighbors that are already visited/revealed
    #         # Returns just a value not cell indexs that are visited
    #         visited = self.get_visited_cells(current_neighbors)
    #
    #         obj.safe_n = visited
    #
    #         # In adjacent cells, returns a value for neighbors that are hidden/unrevealed cells - Returns just a value
    #         # not cell indexs that are hidden
    #         hidden = self.get_hidden_cells(current_neighbors)
    #         obj.cells_still_unexplored_in_neighbors = hidden
    #
    #         # In adjacent cells, returns a value for neighbors that are mines - Returns just a value not cell indexs
    #         # that are flagged or mines
    #         mines = self.get_mines_in_neighbor_cells(current_neighbors)
    #         obj.appearing_mines_in_neighbors = mines
    #
    #         obj.print_cell_info()  # To print each cell info
    #
    #         # code below is for the basic algorithm from the description
    #         a = self.mine_estimate(obj.clue, mines,
    #                                hidden)  # this checks the mine code from basic algorithm in the description
    #         if a:
    #             self.flag_cells(current_neighbors)
    #         else:
    #             self.safe_estimator(obj.clue, visited, hidden)
    #             ret_list = self.flag_cells_as_safe(current_neighbors)
    #
    #             cell_to_delete = [i, j]
    #             self.delete_var(cell_to_delete) # Removes revealed cell from KB
    #
    #             return ret_list
    #
    #     return []

    def flag_cells_csp(self, current_neighbors):
        # If a cell is flagged then this function will flag the cell
        neighbor = self.get_hidden_cells_list(current_neighbors)
        for i in current_neighbors:
            print(i)
            obj = self.get_cur_cell_instance(i)
            #obj.status = 1  # whether or not it is a mine or safe
            obj.set_cell_status(1)
            if i not in self.mine_cells:
                self.mine_cells.append(i)
            if i in self.traverse_cells:
                self.unvisited_cells.remove(i)
            if i in self.traverse_cells:
                self.traverse_cells.remove(i)
            # color = (255, 255, 255)
            index_i = i[0]
            index_j = i[1]
            self.environment_obj.color_cell('', index_i, index_j, 'flag')
        #return neighbor

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

    # Returns a list of unrevealed neighbor cells
    def flag_cells_as_safe(self, current_neighbors):
        # returns a list of hidden cells in current_neighbors
        neighbor = self.get_hidden_cells_list(current_neighbors)
        # for i in neighbor:
        #     obj = self.get_cur_cell_instance(i)
        #     obj.status = 1  # whether or not it is a mine or safe
        #     obj.status = 0  # whether or not it is a mine or safe
        return neighbor

    # This  adds new list safe neighbors that needs to be explored to an already existing list with cells
    # Adds new unrevealed cells to a list which already contains cells that need to be explored
    def cell_traverse_list(self, list_cells):
        if len(list_cells) > 0:
            for i in list_cells:
                if i not in self.traverse_cells:
                    self.traverse_cells.append(i)

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
            for i in range(0,9):
                if ([var_1, [i]] in self.knowledge_base):
                    return False

        if eq_length == 2:
            for i in range(0, 9):
                if ([var_1, var_2, [i]] in self.knowledge_base):
                    return False

        if eq_length == 3:
            for i in range(0, 9):
                if ([var_1, var_2, var_3, [i]] in self.knowledge_base):
                    return False
        return True

    # This cupdates already existing vars and eqs in the knowledge base
    def update_duplicate(self, var_list, eq_length, new_clue):  # var_list will have [ var1_var2_var3 ]
        print()
        # print("IM HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE IN DUPLICATE #$##############################")
        # var_1 = var_2 = var_3 = 0
        # if len(var_list) == 1:
        #     var_1 = var_list[0]
        #
        # if len(var_list) == 2:
        #     var_1 = var_list[0]
        #     var_2 = var_list[1]
        #
        # if len(var_list) == 3:
        #     var_1 = var_list[0]
        #     var_2 = var_list[1]
        #     var_3 = var_list[2]
        #
        # if eq_length == 1:
        #     for i in range(0,9):
        #         if ([var_1, [i]] in self.knowledge_base):
        #             self.knowledge_base.remove( [var_1, [i]] )
        #             clue = new_clue[0]
        #             eq = [var_1, [clue]]
        #             self.knowledge_base.append(eq)
        #
        # if eq_length == 2:
        #     for i in range(0, 9):
        #         if ([var_1, var_2, [i]] in self.knowledge_base):
        #             self.knowledge_base.remove( [var_1, var_2, [i]] )
        #             clue = new_clue[0]
        #             eq = [var_1, var_2, [clue]]
        #             self.knowledge_base.append(eq)
        #
        # if eq_length == 3:
        #     for i in range(0, 9):
        #         if ([var_1, var_2, var_3, [i]] in self.knowledge_base):
        #             self.knowledge_base.remove( [var_1, var_2, var_3, [i]] )
        #             clue = new_clue[0]
        #             eq = [var_1, var_2, var_3, [clue]]
        #             self.knowledge_base.append(eq)
        # return True

    # orignal form_equation

    # Functionality: takes in a list from current_cell that has to be determine and creates equation of
    # the form a+b+c=clue, a = clue etc in the knowledge base

######################Orignal#############################

    # def form_equation(self, passed_list, clue, current_cell):
    #     clue = [clue]
    #     # passed_list is the list of hidden neighbor cells
    #     # current_cell position is being passed to make equations of the neighboring cells as current_cell is the cell in being queried
    #
    #     # a b c
    #     # d   f
    #     # g h i
    #
    #     # adds single index with clue e.g a = val , b = val etc
    #     for index in passed_list:
    #         # checks if any neighbor is already visited - if it has been revealed then we remove it from the list before
    #         # processing it
    #         if index in self.visited_cells:
    #             passed_list.remove(index)
    #         # if [ index , clue] not in self.knowledge_base:  # checks if neighbor list does not exist in knowledge base
    #         status = self.check_duplicate([index], 1)
    #         # if status is false call the update value method
    #         if status:
    #             self.knowledge_base.append([index, clue])
    #         else:
    #             self.update_duplicate(index, 1, clue)
    #
    #
    #     i = current_cell[0]
    #     j = current_cell[1]
    #
    #     # a b c
    #     # d   f
    #     # g h i
    #
    #     top_left = [i - 1, j - 1]
    #     top = [i - 1, j]
    #     top_right = [i - 1, j + 1]
    #
    #     mid_left = [i, j - 1]
    #     mid_right = [i, j + 1]
    #
    #     bottom_left = [i + 1, j - 1]
    #     bottom = [i + 1, j]
    #     bottom_right = [i + 1, j + 1]
    #
    #     # Top row
    #     if (top_left in passed_list) and (top in passed_list):  # a + b
    #         equation = [top_left, top, clue]
    #         if equation not in self.knowledge_base:
    #             status = self.check_duplicate([top_left, top], 2)
    #             if status:
    #                 self.knowledge_base.append(equation)
    #             else:
    #                 self.update_duplicate([top_left, top], 2, clue)
    #
    #     if (top in passed_list) and (top_right in passed_list):  # b + c
    #         equation = [top, top_right, clue]
    #         if equation not in self.knowledge_base:
    #             if equation not in self.knowledge_base:
    #                 status = self.check_duplicate([top, top_right], 2)
    #                 if status:
    #                     self.knowledge_base.append(equation)
    #                 else:
    #                     self.update_duplicate([top, top_right], 2, clue)
    #
    #     # if a+b+c exists then a+b exist and b+c exists
    #     if (top_left in passed_list) and (top in passed_list) and (top_right in passed_list):  # a + b + c
    #         equation = [top_left, top, top_right, clue]
    #         if equation not in self.knowledge_base:
    #             status = self.check_duplicate([top_left, top, top_right], 3)
    #             if status:
    #                 self.knowledge_base.append(equation)
    #             else:
    #                 self.update_duplicate([top_left, top, top_right], 3, clue)
    #
    #     # bottom row
    #     if (bottom_left in passed_list) and (bottom in passed_list):  # a + b
    #         equation = [bottom_left, bottom, clue]
    #         if equation not in self.knowledge_base:
    #             status = self.check_duplicate([bottom_left, bottom], 2)
    #             if status:
    #                 self.knowledge_base.append(equation)
    #             else:
    #                 self.update_duplicate([bottom_left, bottom], 2, clue)
    #
    #             # self.knowledge_base.append(equation)
    #             # self.knowledge_base.append('bottom row # a + b')
    #
    #     if (bottom in passed_list) and (bottom_right in passed_list):  # b + c
    #         equation = [bottom, bottom_right, clue]
    #         if equation not in self.knowledge_base:
    #             status = self.check_duplicate([bottom, bottom_right], 2)
    #             if status:
    #                 self.knowledge_base.append(equation)
    #             else:
    #                 self.update_duplicate([bottom, bottom_right], 2, clue)
    #
    #             # self.knowledge_base.append(equation)
    #             # self.knowledge_base.append('bottom row # b + c')
    #
    #     if (bottom_left in passed_list) and (bottom in passed_list) and (bottom_right in passed_list):  # a + b + c
    #         equation = [bottom_left, bottom, bottom_right, clue]
    #         if equation not in self.knowledge_base:
    #             status = self.check_duplicate([bottom_left, bottom, bottom_right], 3)
    #             if status:
    #                 self.knowledge_base.append(equation)
    #             else:
    #                 self.update_duplicate([bottom_left, bottom, bottom_right], 3, clue)
    #             # self.knowledge_base.append(equation)
    #             # self.knowledge_base.append('bottom row # a + b + c')
    #
    #     # left col
    #     if (top_left in passed_list) and (mid_left in passed_list):  # a + d
    #         equation = [top_left, mid_left, clue]
    #         if equation not in self.knowledge_base:
    #             status = self.check_duplicate([top_left, mid_left], 2)
    #             if status:
    #                 self.knowledge_base.append(equation)
    #             else:
    #                 self.update_duplicate([top_left, mid_left], 2, clue)
    #
    #             # self.knowledge_base.append(equation)
    #             # self.knowledge_base.append('left col # a + d')
    #
    #     if (mid_left in passed_list) and (bottom_left in passed_list):  # d + g
    #         equation = [mid_left, bottom_left, clue]
    #         if equation not in self.knowledge_base:
    #             status = self.check_duplicate([mid_left, bottom_left], 2)
    #             if status:
    #                 self.knowledge_base.append(equation)
    #             else:
    #                 self.update_duplicate([mid_left, bottom_left], 2, clue)
    #             # self.knowledge_base.append(equation)
    #             # self.knowledge_base.append('left col # d + g')
    #
    #     if (top_left in passed_list) and (mid_left in passed_list) and (bottom_left in passed_list):  # a + d + g
    #         equation = [top_left, mid_left, bottom_left, clue]
    #         if equation not in self.knowledge_base:
    #             status = self.check_duplicate([top_left, mid_left, bottom_left], 3)
    #             if status:
    #                 self.knowledge_base.append(equation)
    #             else:
    #                 self.update_duplicate([top_left, mid_left, bottom_left], 3, clue)
    #             # self.knowledge_base.append(equation)
    #             # self.knowledge_base.append('left col # a + d + g')
    #
    #     # right row
    #     if (top_right in passed_list) and (mid_right in passed_list):  # c + f
    #         equation = [top_right, mid_right, clue]
    #         if equation not in self.knowledge_base:
    #             status = self.check_duplicate([top_right, mid_right], 2)
    #             if status:
    #                 self.knowledge_base.append(equation)
    #             else:
    #                 self.update_duplicate([top_right, mid_right], 2, clue)
    #             # self.knowledge_base.append(equation)
    #             # self.knowledge_base.append('right col # c + f')
    #
    #     if (mid_right in passed_list) and (bottom_right in passed_list):  # f + i
    #         equation = [mid_right, bottom_right, clue]
    #         if equation not in self.knowledge_base:
    #             status = self.check_duplicate([mid_right, bottom_right], 2)
    #             if status:
    #                 self.knowledge_base.append(equation)
    #             else:
    #                 self.update_duplicate([mid_right, bottom_right], 2, clue)
    #             # self.knowledge_base.append(equation)
    #             # self.knowledge_base.append('right col # f + i')
    #
    #     if (top_right in passed_list) and (mid_right in passed_list) and (bottom_right in passed_list):  # c + f + i
    #         equation = [top_right, mid_right, bottom_right, clue]
    #         if equation not in self.knowledge_base:
    #             status = self.check_duplicate([top_right, mid_right, bottom_right], 3)
    #             if status:
    #                 self.knowledge_base.append(equation)
    #             else:
    #                 self.update_duplicate([top_right, mid_right, bottom_right], 3, clue)
    #             # self.knowledge_base.append(equation)
    #             # self.knowledge_base.append('right col # c + f + i')
    #
    #     #form_equation
    #     # for i in self.knowledge_base:
    #     #     print(i) # , " - Length : " , len(i) )
    #
    #     print('----')


###################################################


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

        ############ TOP ROW #############################

        # if a+b+c exists then a+b exist and b+c exists
        if (top_left in passed_list) and (top in passed_list) and (top_right in passed_list):
            # make a+b+c = clue , then a+b = clue-1 and b+c = clue -1 whereas for a+b and b+c clue != 0
            equation = [top_left, top, top_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_left, top, top_right], 3)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([top_left, top, top_right], 3, clue)

            c = clue[0]-1   # so it is easier in subsets (a+B+C) -> a+b or B+c would be clue - 1
            c = [c]
            equation = [top_left, top, c]    # a + b
            if (equation not in self.knowledge_base) and c[0] >= 0 :
                status = self.check_duplicate([top_left, top], 2)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([top_left, top], 2, c)

            equation = [top, top_right, c]
            if (equation not in self.knowledge_base) and c[0] >= 0 :    #b+c
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([top, top_right], 2)
                    if status:
                        self.knowledge_base.append(equation)
                    else:
                        self.update_duplicate([top, top_right], 2, c)

        else:
            if (top_left in passed_list) and (top in passed_list):  # a + b
                equation = [top_left, top, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([top_left, top], 2)
                    if status:
                        self.knowledge_base.append(equation)
                    else:
                        self.update_duplicate([top_left, top], 2, clue)

            if (bottom in passed_list) and (bottom_right in passed_list):  # b + c
                equation = [bottom, bottom_right, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([bottom, bottom_right], 2)
                    if status:
                        self.knowledge_base.append(equation)
                    else:
                        self.update_duplicate([bottom, bottom_right], 2, clue)

        ##### BOTTOM ROW ######

        if (bottom_left in passed_list) and (bottom in passed_list) and (bottom_right in passed_list):
            # a + b + c then a+b=clue-1 and b+c=clue-1
            equation = [bottom_left, bottom, bottom_right, clue]  # a + b + c
            if equation not in self.knowledge_base:
                status = self.check_duplicate([bottom_left, bottom, bottom_right], 3)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([bottom_left, bottom, bottom_right], 3, clue)

            c = clue[0]-1
            c = [c]
            equation = [bottom_left, bottom, c]
            if (equation not in self.knowledge_base) and c[0] >= 0 :  # a + b
                status = self.check_duplicate([bottom_left, bottom], 2)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([bottom_left, bottom], 2, c)

            equation = [bottom, bottom_right, c]
            if (equation not in self.knowledge_base) and c[0] >= 0 :  # b + c
                status = self.check_duplicate([bottom, bottom_right], 2)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([bottom, bottom_right], 2, c)

        else:
            if (top in passed_list) and (top_right in passed_list):  # b + c
                equation = [top, top_right, clue]
                if equation not in self.knowledge_base:
                    if equation not in self.knowledge_base:
                        status = self.check_duplicate([top, top_right], 2)
                        if status:
                            self.knowledge_base.append(equation)
                        else:
                            self.update_duplicate([top, top_right], 2, clue)

            if (bottom_left in passed_list) and (bottom in passed_list):  # a + b
                equation = [bottom_left, bottom, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([bottom_left, bottom], 2)
                    if status:
                        self.knowledge_base.append(equation)
                    else:
                        self.update_duplicate([bottom_left, bottom], 2, clue)

        ######## LEFT COL ###########

        if (top_left in passed_list) and (mid_left in passed_list) and (bottom_left in passed_list):
            equation = [top_left, mid_left, bottom_left, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_left, mid_left, bottom_left], 3)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([top_left, mid_left, bottom_left], 3, clue)

            c = clue[0] - 1
            c = [c]
            equation = [top_left, mid_left, c]  # a + d
            if (equation not in self.knowledge_base) and c[0] >= 0 :
                status = self.check_duplicate([top_left, mid_left], 2)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([top_left, mid_left], 2, c)

            equation = [mid_left, bottom_left, c]    # d + g
            if (equation not in self.knowledge_base) and c[0] >= 0 :
                status = self.check_duplicate([mid_left, bottom_left], 2)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([mid_left, bottom_left], 2, c)

        else:
            if (top_left in passed_list) and (mid_left in passed_list):  # a + d
                equation = [top_left, mid_left, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([top_left, mid_left], 2)
                    if status:
                        self.knowledge_base.append(equation)
                    else:
                        self.update_duplicate([top_left, mid_left], 2, clue)

            if (mid_left in passed_list) and (bottom_left in passed_list):  # d + g
                equation = [mid_left, bottom_left, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([mid_left, bottom_left], 2)
                    if status:
                        self.knowledge_base.append(equation)
                    else:
                        self.update_duplicate([mid_left, bottom_left], 2, clue)

        ############ RIGHT ROW ################

        if (top_right in passed_list) and (mid_right in passed_list) and (bottom_right in passed_list):  # c + f + i
            equation = [top_right, mid_right, bottom_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_right, mid_right, bottom_right], 3)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([top_right, mid_right, bottom_right], 3, clue)

            c = clue[0] - 1
            c = [c]
            equation = [top_right, mid_right, c]
            if (equation not in self.knowledge_base) and c[0] >= 0 :
                status = self.check_duplicate([top_right, mid_right], 2)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([top_right, mid_right], 2, c)

            equation = [mid_right, bottom_right, c]
            if (equation not in self.knowledge_base) and c[0] >= 0 :
                status = self.check_duplicate([mid_right, bottom_right], 2)
                if status:
                    self.knowledge_base.append(equation)
                else:
                    self.update_duplicate([mid_right, bottom_right], 2, c)

        else:
            if (top_right in passed_list) and (mid_right in passed_list):  # c + f
                equation = [top_right, mid_right, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([top_right, mid_right], 2)
                    if status:
                        self.knowledge_base.append(equation)
                    # else:
                    #     self.update_duplicate([top_right, mid_right], 2, clue)

            if (mid_right in passed_list) and (bottom_right in passed_list):  # f + i
                equation = [mid_right, bottom_right, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([mid_right, bottom_right], 2)
                    if status:
                        self.knowledge_base.append(equation)
                    # else:
                    #     self.update_duplicate([mid_right, bottom_right], 2, clue)

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
        return []

    # Functionality: When a cell has been revealed - go through knowledge base and delete the var from equations
    def delete_var(self, cell_to_delete):
        # iterates through every single thing in knowledge base to remove that variable from every equation
        for index in self.knowledge_base:   # index is the equations in knowledge base
            ret_list = self.delete_var_helper(index, cell_to_delete)
            if len(ret_list) == 1:  # This deletes just the val in [a,0] when [0] only exists
                self.knowledge_base.remove(index)
            if len(ret_list) > 2:
                if index != ret_list:
                    self.knowledge_base.remove(index)
                    self.knowledge_base.append(ret_list)

    # This confirms variable is removed from remaining csp equations
    def var_removed_confirmed(self, passed_cell):
        # Delete revealed variables from csp equation in knowledge base
        for index in self.knowledge_base:
            if passed_cell in index:
                self.delete_var(passed_cell)

    def remove_mine_from_kb(self,i,j):
        var_0 = var_1 = var_2 = 0
        for i in self.knowledge_base:
            if [i, j] in i:
                clue = i[-1]
                clue = clue[0]

                if len(i) == 2:  # (a,0)
                    self.knowledge_base.remove(i)

                if len(i) == 3:  # (a,b,0)
                    if i[0] == [i, j]:  # (mine,b,0)
                        var_0 = i[1]
                    else:  # (a,mine,0)
                        var_0 = i[0]
                    self.knowledge_base.remove(i)
                    if clue != 0:
                        clue = clue - 1
                    eq = [var_0, [clue]]
                    self.knowledge_base.append(eq)

                if len(i) == 4:  # (a,b,c,0)
                    eq = None
                    if clue != 0:
                        clue = clue - 1
                    if i[0] == [i, j]:  # (mine, b, c, 0)
                        var_1 = i[1]
                        var_2 = i[2]
                        eq = [var_1, var_2, [clue]]
                    if i[1] == [i, j]:  # (a, mine, c, 0)
                        var_0 = i[0]
                        var_2 = i[2]
                        eq = [var_0, var_2, [clue]]
                    if i[2] == [i, j]:  # (a, b, mine, 0)
                        var_0 = i[0]
                        var_1 = i[1]
                        eq = [var_0, var_1, [clue]]
                    self.knowledge_base.remove(i)
                    self.knowledge_base.append(eq)

    # Functionality: checks current_cell neighbors and determine which cell is a hidden cell, which cell is already
    # visited and what cell is a mine
    def constraint_cell_processing(self, i, j):#, status):
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
            self.mines_left = self.mines_left - 1

            self.remove_mine_from_kb(i,j)

            # for i in self.knowledge_base:
            #     if [i,j] in i:
            #         clue = i[-1]
            #         clue = clue[0]
            #
            #         if len(i) == 2: # (a,0)
            #             self.knowledge_base.remove(i)
            #
            #         if len(i) == 3: # (a,b,0)
            #             if i[0] == [i,j]: # (mine,b,0)
            #                 var_0 = i[1]
            #             else:   # (a,mine,0)
            #                 var_0 = i[0]
            #             self.knowledge_base.remove(i)
            #             if clue != 0:
            #                     clue = clue - 1
            #             eq = [var_0 , [clue]]
            #             self.knowledge_base.append(eq)
            #
            #         if len(i) == 4: # (a,b,c,0)
            #             eq = None
            #             if clue != 0:
            #                     clue = clue - 1
            #             if i[0] == [i,j]: # (mine, b, c, 0)
            #                 var_1 = i[1]
            #                 var_2 = i[2]
            #                 eq = [ var_1, var_2, [clue]]
            #             if i[1] == [i, j]:  # (a, mine, c, 0)
            #                 var_0 = i[0]
            #                 var_2 = i[2]
            #                 eq = [var_0, var_2, [clue]]
            #             if i[2] == [i, j]:  # (a, b, mine, 0)
            #                 var_0 = i[0]
            #                 var_1 = i[1]
            #                 eq = [var_0, var_1, [clue]]
            #             self.knowledge_base.remove(i)
            #             self.knowledge_base.append(eq)

            if [i, j] in self.unvisited_cells:
                self.unvisited_cells.remove([i, j])

            # keep a separate knowledge base that stores only indexes of mines
            # on every neighbor check make sure to check in the mine kb to remove that index from mines to be checked
            # keep a mine counter when everytime you find a mine or flag a cell you decrement the counter and
            # keep a check of how many mines are left in the map

            # if cell is a mine
            # go in kb and remove from csp equations
            # subtract -1 from clue in csp equations
            # if clue is zero and eq length is 3 (a+b)

            # and if it is single var ar remove it from kb


        if status != 1:
            self.visited_cells.append([i, j])  # adds current processed cell in list of visited cells if its safe
            if [i, j] in self.unvisited_cells:
                self.unvisited_cells.remove([i, j])  # removing index from unvisited cells
            obj.status = 0  # identifies the index as safe by marking it 0

            obj.clue = self.environment_obj.get_clue(self.array_board, i,j)
            # assigns clue (clue is number of mines in adjacent neighbors

            if obj.clue==0:
                self.environment_obj.color_cell('', i, j, 0)  # This code marks the cell on GUI boards
            else:
                self.environment_obj.color_cell(str(obj.clue), i, j, 0)  # This code marks the cell on GUI boards

            current_neighbors = self.get_neighbors_current_cell(i, j)  # gets a list of neighbors of current cells

            # gets a count of number of cells visited around current cell
            visited = self.get_visited_cells(current_neighbors)
            obj.safe_n = visited

            # gets a count of number of cells unrevealed around current cell
            hidden = self.get_hidden_cells(current_neighbors)
            obj.cells_still_unexplored_in_neighbors = hidden

            # gets a count of number of cells as mines around current cell
            mines = self.get_mines_in_neighbor_cells(current_neighbors)
            obj.appearing_mines_in_neighbors = mines

            # obj.print_cell_info()  # To print each cell info

            #self.safe_estimator(obj.clue, visited, hidden)

            # I need to get get a list of hidden cells from neighbors
            # Returns unrevealed neighbor cells of the list current_neighbors
            ret_list = self.flag_cells_as_safe(current_neighbors)

            cell_to_delete = [i, j]
            self.delete_var(cell_to_delete) # Removes revealed cell from KB
            return ret_list


        return []

    # VERY VERY VERY IMPORTANT 786
# Try this approach: - dont discard the clue from the very start
# keep a stack of cells to visit and a stack of cells that you think are mines
# open few cells but dont flag anything
# but once you have around 5-6 cells opened then try to go back to the stack of cells you think are mines
# and recalculate for them if they are mines and then start flagging mines.
#     At that point of the program you should have a pretty long stack of cells you think are mines so you should
# be able to get something - Note: do not just pick the cell from the suspicious list and mark them - take the cell
# and then re-evaluate that cell by going through the KB again and seeing if it can be determined that cell is mine or not

    # returns csp equation from knowledge base of desired length
    def get_info(self, val, equation_length):
        # if equation_length == 2 (a,0) , if == 3 (a,b,0), if == 4 (a,b,c,0)
        # val passed should be in the form [i,j]
        print(val)
        for index in self.knowledge_base:
            if val in index:
                if len(index) == equation_length:
                    return index


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

            for i in range(0,9):
                eq = [var_1, var_2, [i]]
                if eq in self.knowledge_base:
                    val = eq[-1]
                    val = val[0]
                    # print("-------------------- true for eq : eq[", i, "] | Val is : ", val)
                    break
            # if ( eq_0 in self.knowledge_base ):
            #     val = eq_0[-1]
            #     val = val[0]
            #     print("-------------------- true for eq0 : ",eq_0, "| Val is : ", val )
            #
            # if ( eq_1 in self.knowledge_base ):
            #     val = eq_1[-1]
            #     val = val[0]
            #     print("-------------------- true for eq 1 : ",eq_1, "| Val is : ", val )
            #
            # if ( eq_2 in self.knowledge_base ):
            #     val = eq_2[-1]
            #     val = val[0]
            #     print("-------------------- true for eq 2 : ",eq_2, "| Val is : ", val )
            #
            # if (eq_3 in self.knowledge_base):
            #     val = eq_3[-1]
            #     val = val[0]
            #     print("-------------------- true for eq 3 : ",eq_3, "| Val is : ", val )
            #
            # if ( eq_4 in self.knowledge_base ):
            #     val = eq_4[-1]
            #     val = val[0]
            #     print("-------------------- true for eq 4 : ",eq_4, "| Val is : ", val )
            #
            # if ( eq_5 in self.knowledge_base ):
            #     val = eq_5[-1]
            #     val = val[0]
            #     print("-------------------- true for eq 5 : ",eq_5, "| Val is : ", val )
            #
            # if (eq_6 in self.knowledge_base):
            #     val = eq_6[-1]
            #     val = val[0]
            #     print("-------------------- true for eq 6: ",eq_6, "| Val is : ", val )
            #
            # if ( eq_7 in self.knowledge_base ):
            #     val = eq_7[-1]
            #     val = val[0]
            #     print("-------------------- true for eq 7: ",eq_7, "| Val is : ", val )
            #
            # if( eq_8 in self.knowledge_base ):
            #     val = eq_8[-1]
            #     val = val[0]
            #     print("-------------------- true for eq 8: ",eq_8, "| Val is : ", val )
            return val
        return None

    def subset(self, passed_list, val):  # note: we are only for solving subset for 3 eqs for now
        # val is the clue val
        if len(passed_list)>2:
            val = val[0]
            var_1 = passed_list[0]
            var_2 = passed_list[1]

            if len(passed_list) >= 4:
                for i in range(0, 9):
                    ret_val = self.subset_helper(var_1,var_2)

                if ret_val != None:
                    if var_1 in passed_list and var_2 in passed_list:
                        print("[This equattion is being passed to subset] ", passed_list)
                        # a+b+c = val
                        # c + (a+b) = val
                        # c = val - (a+b)
                        var_3 = val - ret_val # a+b+c, ret_val = a + b
                        print("Clue val : " , val)
                        print("return val" , ret_val)
                        print("var c ", var_3)
                        sum = var_3 + ret_val
                        # if sum == val:
                        #     return passed_list[2]
                        if var_3 != 0:
                            sum = var_3 + ret_val
                            if sum == val:
                                print("var c : " , passed_list[2])
                                return passed_list[2]
                else:
                    var_2 = passed_list[1]
                    var_3 = passed_list[2]
                    ret_val = self.subset_helper(var_2, var_3)
                    if ret_val != None:

                        if var_2 in passed_list and var_3 in passed_list:
                            print("This equation is being passed to subset ", passed_list)
                            var_1 = val - ret_val
                            print("Clue val : ", val)
                            print("return val", ret_val)
                            print("var a ", var_1)
                            if var_1 != 0:
                                sum = var_1 + ret_val
                                if sum == val:
                                    print("var a : ", passed_list[1])
                                    return passed_list[1]

            if len(passed_list) == 3:   # (a,b,0)
                var_1 = passed_list[0]
                var_2 = passed_list[1]
                rt_list = []
                print( "pasing : " , var_1 , ", " , var_2 )
                val_1 = self.get_info(var_1, 2)
                val_2 = self.get_info(var_2, 2)

                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                print(val_1)
                print(val_2)

                if val_1 != None and val_2 != None:

                    if val_1 != None:
                        print("get_info" , val_1)
                        val_1 = val_1[-1]
                        val_1 = val_1[0]

                    if val_2 != None:
                        print("get_info" , val_2)
                        val_2 = val_2[-1]
                        val_2 = val_2[0]

                    if ( val_1 + val_2 ) == val:
                        if val_1 != 0 :
                            rt_list.append(var_1)
                        if val_2 != 0 :
                            rt_list.append(var_2)
                    return rt_list
                return False
        return False

    def equation_solver_csp(self, passed_list, hidden_neighbors,length,passed_cell):
        # passed list is just the list with equations of neighbor cells of current cell to determine if safe or not
        # NOTE: SOLVE THIS: I AM GETTING VARIABLES THAT SHARE NEIGHBORS WITH OTHERS - GET EQUATIONS THAT ONLY SHARE
        var_that_are_true = []
        check = 0
        # note : index is the whole equation e.g [a,b,1] etc

        print("equation_solver_csp - " , passed_list)

        for index in passed_list:
            clue = index[-1]

            # Equation (a,b,c,0) only in this condition
            if len(index) >= 4: # a + b + c
                # if subset returns false then we go to else condition as current csp equation cannot be solved
                # by subset
                returned_cell = self.subset(index, clue)    # returned_cell is the cell we think is a mine

                if returned_cell != False:  # This condition confirms subsets can be solved
                    print("Subset ============================")
                    print("returned cell from Subset method : ", returned_cell)
                    if returned_cell:
                        var_that_are_true.append(returned_cell)
                    #var_that_are_true.append(returned_cell)
                    print("before removing cell from neighbor list: " , hidden_neighbors)
                    if returned_cell in hidden_neighbors:
                        hidden_neighbors.remove(returned_cell)
                    print("After removing cell from neighbor list: ", hidden_neighbors)

                # else:   # length equation of 3 var cannot be solved in subsets
                #     print(" ret_val ====== FALSE // 3 var eq was not solved by subset solver &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                #     print(returned_cell)
                #
                #     sum = 3 # sum is 3 because (a,b,c) we ahve 3 vars
                #     print(index)
                #     if sum == clue[0]:
                #
                #         var_that_are_true.append(returned_cell)
                #         print("before removing cell from neighbor list: ", passed_list)
                #         if returned_cell in hidden_neighbors:
                #             hidden_neighbors.remove(returned_cell)
                #         print("After removing cell from neighbor list: ", passed_list)
                #     else:
                #         check = 1

            # Eq (a,b,0) is not solvable b
            if len(index) == 3:  # a + b

                print(" Eq length is 3 (a,b,0) - Z Z Z Z Z Z Z Z ZZ Z Z Z Z ZZ Z Z Z   Z Z Z Z ZZ Z Z Z Z ZZ  Z Z Z Z ZZ Z Z Z Z ZZ ")
                returned_cell = self.subset(index, clue)
                print()
                print("Value returned , " , returned_cell)
                if returned_cell:
                    for i in returned_cell: # as im returning a nested list thats why I need the for loop e.g [ [] ] and
                        # others are returning just []
                        var_that_are_true.append(i)
                print("before removing cell from neighbor list: ", hidden_neighbors)
                if returned_cell in hidden_neighbors:
                    hidden_neighbors.remove(returned_cell)
                print("After removing cell from neighbor list: ", hidden_neighbors)

            # if len(index) == 2:  # a + b
            #
            #     print(" Eq length is 1 (a,b,0) - D D D D DD D D D D D DD D D D D D DD D D D D D DD D D D D D DD D D D D D DD D  ")
            #     val_1 = self.get_info(index[0], 2)
            #     val = val_1[-1]
            #     val = val[0]
            #     if val == 1 and clue == 1:
            #         var_that_are_true.append(i)
            #         if returned_cell in hidden_neighbors:
            #             hidden_neighbors.remove(returned_cell)
            #         print("After removing cell from neighbor list: ", hidden_neighbors)

        return var_that_are_true # MAKE SURE TO CHANGE THIS TO var_that_are_true ***********************************


    def csp_solver(self, neighbor_list,passed_cell):
        hidden_neighbors_list = self.get_hidden_cells_list(neighbor_list)   # gets a list of cells for each neighbor

        for index in self.knowledge_base:
            if passed_cell in index:
                self.delete_var(passed_cell)


        # Gets the csp equations
        eq_of_neighbor_cells = []  # This list contains csp eq from kb of required cells
        for index in hidden_neighbors_list:  # iterate cell by cell e.g index is [0,1] then [0,2] then [0,3] etc
            self.search_knowledge_base(index, hidden_neighbors_list , eq_of_neighbor_cells)    # each hidden neighbor cell is prcoessed here

        #self.skb_helper(hidden_neighbors_list , eq_of_neighbor_cells)    # removes eq that have var not in neighbors
        #print("equations from kb for each neighbor: " , eq_of_neighbor_cells)

        # Solves the CSP equations
        print("Neighbor list:" , hidden_neighbors_list)
        print("$$$$$$$$$$$     $$$$$$$$$$$$$$$$       $$$$$$$$$$$$$$$$$$$$$$$$$$")

        cells_to_flag = self.equation_solver_csp(eq_of_neighbor_cells, hidden_neighbors_list , len(hidden_neighbors_list), passed_cell)

        print("$$$$$$$$$$$     $$$$$$$$$$$$$$$$       $$$$$$$$$$$$$$$$$$$$$$$$$$")

        # cells_to_flag_2 = []
        # for i in cells_to_flag:
        #     if [i,[1]] in self.knowledge_base:
        #         print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        #         print("                                                                                    ", i )
        #         cells_to_flag_2.append(i)


        print("neighbors that should be flagged list:", cells_to_flag)
        for i in hidden_neighbors_list:
            for j in self.knowledge_base:
                if [i,[1]] in j:
                    print(" After going through equation_csp_solver - ************************************* " ,  j)

        print("Safe cell : ", hidden_neighbors_list) # this hidden_neighbors contains only neighbors that are deemed safe
        print("hidden neighbors list : ", hidden_neighbors_list)
        print("cells_to_flag from equation_solver_csp : ", cells_to_flag)

        for i in cells_to_flag:
            if i not in self.flagged_cells:
                self.flagged_cells.append( i )



        # note: need to implement a backtracking approach
        # - make a list of cells that needs to be flagged but dont flag them yet you unless you have 3 2 or less hidden neighbors
        # - keep track of those cells that should be flagged but are not flagged right now(List flagged_cells)

        # - click one of the cell you think is safe (from safe list) (list a)
        # - store the neighors of the cell you just clicked in a separate list (list B)
        # - after clicking the mine - go back and pick a cell from flagged_cells list again and determine if its solvable
        # - if solvable - flag or open the cell , if not next step
        # if you still have cells from list a click and check flagged cells until flagged_cells is empty or list a is empty
        # - then go back to the previous cells that were flagged
        # - calculate for them again and see if results change
        # - if results change THEN flag the cell that end up with val 1

        #self.flag_cells_csp(cells_to_flag)

        # if len(hidden_neighbors_list)<3:
        #     self.flag_cells_csp(cells_to_flag_2)
        if cells_to_flag:
            print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            print(cells_to_flag)
            self.flag_cells_csp(cells_to_flag)

        return hidden_neighbors_list

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

    # Functionality: This function takes a list, and uses process_current_cell to process each cell
    def traverse(self, list_cells):
        while self.unvisited_cells:
            time.sleep(0.2)
            self.cell_traverse_list(list_cells) # add passed list to list of cells to be explored
            print("list of cells in line to be explored: ", self.traverse_cells)

            # new cell is selected
            if self.traverse_cells:
                index = self.traverse_cells.pop(0)
                index_board_i = index[0]
                index_board_j = index[1]

                flag_or_safe_val = 0
                list_cells = self.constraint_cell_processing(index_board_i, index_board_j, flag_or_safe_val)

                if list_cells:  # If not empty()
                    val = self.get_clue(self.board_array, index_board_i, index_board_j)
                    self.form_equation(list_cells, val, [index_board_i, index_board_j])


            # in case our list_cells or traverse_cells is empty
            else:
                print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")
                self.traverse_cells.append(self.unvisited_cells.pop())

        print(self.knowledge_base)
        if not self.unvisited_cells:
            print("EXITING $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

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
