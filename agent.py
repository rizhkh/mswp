import numpy as np
import copy
# import collections
# import random
# from mswp.boardenvironment import environment
from mswp.cellInformation import cell
import time


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
    mine_count = 0
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

    flagged_cells = []
    flagcells_consider = []
    mine_desntiy = 0

    def __init__(self, arr, row_dimension, col_dimenison, bh, bw):
        self.array_board = np.copy(arr)
        # self.all_cells = np.copy(arr)
        self.row = row_dimension
        self.col = col_dimenison
        #self.init_all_cells()
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
                new_obj = copy.copy(a[1])
                print("asdddddddddddddddddddddddd")
                print(new_obj.print_cell_info())
                return new_obj

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
        print("here")
        obj = self.get_cur_cell_instance(current_neighbors)
        # obj.status = 1  # whether or not it is a mine or safe
        obj.set_cell_status(1)
        if current_neighbors not in self.mine_cells:
            self.mine_cells.append(current_neighbors)
        if current_neighbors in self.traverse_cells:
            if current_neighbors in self.unvisited_cells:
                self.unvisited_cells.remove(current_neighbors)
            # self.unvisited_cells.remove(i)
        if current_neighbors in self.traverse_cells:
            self.traverse_cells.remove(current_neighbors)
        # color = (255, 255, 255)
        index_i = current_neighbors[0]
        index_j = current_neighbors[1]
        self.environment_obj.color_cell('', index_i, index_j, 'flag')
        #self.flag_mine(index_i, index_j, 'flag')

        # return neighbor

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
        var_1 = var_2 = var_3 = var_4 = var_5 = var_6 = var_7 = var_8 = 0
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

        if len(var_list) == 5:
            var_1 = var_list[0]
            var_2 = var_list[1]
            var_3 = var_list[2]
            var_4 = var_list[3]
            var_5 = var_list[4]

        for i in range(0, 9):
            if eq_length == 1:
                if [var_1, [i]] in self.knowledge_base:
                    return False

            if eq_length == 2:
                if [var_1, var_2, [i]] in self.knowledge_base:
                    return False

            if eq_length == 3:
                if [var_1, var_2, var_3, [i]] in self.knowledge_base:
                    return False

            if eq_length == 5:
                if [var_1, var_2, var_3, var_4, var_5, [i]] in self.knowledge_base:
                    return False

            if eq_length == 8:
                if [var_1, var_2, var_3, var_4, var_5, var_6, var_7, var_8, [i]] in self.knowledge_base:
                    return False
        # if eq_length == 1:
        #     for i in range(0,9):
        #         if ([var_1, [i]] in self.knowledge_base):
        #             return False
        #
        # if eq_length == 2:
        #     for i in range(0, 9):
        #         if ([var_1, var_2, [i]] in self.knowledge_base):
        #             return False
        #
        # if eq_length == 3:
        #     for i in range(0, 9):
        #         if ([var_1, var_2, var_3, [i]] in self.knowledge_base):
        #             return False

        return True

    # This cupdates already existing vars and eqs in the knowledge base
    #def update_duplicate(self, var_list, eq_length, new_clue):  # var_list will have [ var1_var2_var3 ]
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

    def form_equation(self, passed_list, clue, current_cell):
        clue = [clue]
        # passed_list is the list of hidden neighbor cells current_cell position is being passed to make equations of
        # the neighboring cells as current_cell is the cell in being queried

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
            # else:
            #     self.update_duplicate(index, 1, clue)

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

        # ############ TOP ROW 5 elements #############################
        # # 4 7 8 9 6
        #
        # # if a+b+c exists then a+b exist and b+c exists
        # if (mid_left in passed_list) and (top_left in passed_list) and (top in passed_list) \
        #         and (top_right in passed_list) and (mid_right in passed_list):
        #     # make a+b+c = clue , then a+b = clue-1 and b+c = clue -1 whereas for a+b and b+c clue != 0
        #     equation = [mid_left, top_left, top, top_right, mid_right, clue]
        #     if equation not in self.knowledge_base:
        #         status = self.check_duplicate([mid_left, top_left, top, top_right, mid_right], 5)
        #         if status:
        #             self.knowledge_base.append(equation)
        #
        # ############ Bottomw ROW 5 elements #############################
        # # 4 1 2 3 6
        #
        # # if a+b+c exists then a+b exist and b+c exists
        # if (mid_left in passed_list) and (bottom_left in passed_list) and (bottom in passed_list) \
        #         and (bottom_right in passed_list) and (mid_right in passed_list):
        #     # make a+b+c = clue , then a+b = clue-1 and b+c = clue -1 whereas for a+b and b+c clue != 0
        #     equation = [mid_left, bottom_left, bottom, bottom_right, mid_right, clue]
        #     if equation not in self.knowledge_base:
        #         status = self.check_duplicate([mid_left, bottom_left, bottom, bottom_right, mid_right], 5)
        #         if status:
        #             self.knowledge_base.append(equation)
        #
        # ############ Left ROW 5 elements #############################
        # # 8 7 4 1 2
        #
        # # if a+b+c exists then a+b exist and b+c exists
        # if (top in passed_list) and (top_left in passed_list) and (mid_left in passed_list) \
        #         and (bottom_left in passed_list) and (bottom in passed_list):
        #     # make a+b+c = clue , then a+b = clue-1 and b+c = clue -1 whereas for a+b and b+c clue != 0
        #     equation = [top, top_left, mid_left, bottom_left, bottom, clue]
        #     if equation not in self.knowledge_base:
        #         status = self.check_duplicate([top, top_left, mid_left, bottom_left, bottom], 5)
        #         if status:
        #             self.knowledge_base.append(equation)
        #
        # ############ Right ROW 5 elements #############################
        # # 8 9 6 3 2
        #
        # # if a+b+c exists then a+b exist and b+c exists
        # if (top in passed_list) and (top_right in passed_list) and (mid_right in passed_list) \
        #         and (bottom_right in passed_list) and (bottom in passed_list):
        #     # make a+b+c = clue , then a+b = clue-1 and b+c = clue -1 whereas for a+b and b+c clue != 0
        #     equation = [top, top_right, mid_right, bottom_right, bottom, clue]
        #     if equation not in self.knowledge_base:
        #         status = self.check_duplicate([top, top_right, mid_right, bottom_right, bottom], 5)
        #         if status:
        #             self.knowledge_base.append(equation)

        ############ TOP ROW #############################

        # if a+b+c exists then a+b exist and b+c exists
        if (top_left in passed_list) and (top in passed_list) and (top_right in passed_list):
            # make a+b+c = clue , then a+b = clue-1 and b+c = clue -1 whereas for a+b and b+c clue != 0
            equation = [top_left, top, top_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_left, top, top_right], 3)
                if status:
                    self.knowledge_base.append(equation)
                # else:
                #     self.update_duplicate([top_left, top, top_right], 3, clue)

            c = clue[0] - 1  # so it is easier in subsets (a+B+C) -> a+b or B+c would be clue - 1
            c = [c]
            equation = [top_left, top, c]  # a + b
            if (equation not in self.knowledge_base) and c[0] >= 0:
                status = self.check_duplicate([top_left, top], 2)
                if status:
                    self.knowledge_base.append(equation)
                # else:
                #     self.update_duplicate([top_left, top], 2, c)

            equation = [top, top_right, c]
            if (equation not in self.knowledge_base) and c[0] >= 0:  # b+c
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([top, top_right], 2)
                    if status:
                        self.knowledge_base.append(equation)
                    # else:
                    #     self.update_duplicate([top, top_right], 2, c)

        else:
            if (top_left in passed_list) and (top in passed_list):  # a + b
                equation = [top_left, top, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([top_left, top], 2)
                    if status:
                        self.knowledge_base.append(equation)
                    # else:
                    #     self.update_duplicate([top_left, top], 2, clue)

            if (bottom in passed_list) and (bottom_right in passed_list):  # b + c
                equation = [bottom, bottom_right, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([bottom, bottom_right], 2)
                    if status:
                        self.knowledge_base.append(equation)
                    # else:
                    #     self.update_duplicate([bottom, bottom_right], 2, clue)

        ##### BOTTOM ROW ######

        if (bottom_left in passed_list) and (bottom in passed_list) and (bottom_right in passed_list):
            # a + b + c then a+b=clue-1 and b+c=clue-1
            equation = [bottom_left, bottom, bottom_right, clue]  # a + b + c
            if equation not in self.knowledge_base:
                status = self.check_duplicate([bottom_left, bottom, bottom_right], 3)
                if status:
                    self.knowledge_base.append(equation)
                # else:
                #     self.update_duplicate([bottom_left, bottom, bottom_right], 3, clue)

            c = clue[0] - 1
            c = [c]
            equation = [bottom_left, bottom, c]
            if (equation not in self.knowledge_base) and c[0] >= 0:  # a + b
                status = self.check_duplicate([bottom_left, bottom], 2)
                if status:
                    self.knowledge_base.append(equation)
                # else:
                #     self.update_duplicate([bottom_left, bottom], 2, c)

            equation = [bottom, bottom_right, c]
            if (equation not in self.knowledge_base) and c[0] >= 0:  # b + c
                status = self.check_duplicate([bottom, bottom_right], 2)
                if status:
                    self.knowledge_base.append(equation)
                # else:
                #     self.update_duplicate([bottom, bottom_right], 2, c)

        else:
            if (top in passed_list) and (top_right in passed_list):  # b + c
                equation = [top, top_right, clue]
                if equation not in self.knowledge_base:
                    if equation not in self.knowledge_base:
                        status = self.check_duplicate([top, top_right], 2)
                        if status:
                            self.knowledge_base.append(equation)
                        # else:
                        #     self.update_duplicate([top, top_right], 2, clue)

            if (bottom_left in passed_list) and (bottom in passed_list):  # a + b
                equation = [bottom_left, bottom, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([bottom_left, bottom], 2)
                    if status:
                        self.knowledge_base.append(equation)
                    # else:
                    #     self.update_duplicate([bottom_left, bottom], 2, clue)

        ######## LEFT COL ###########

        if (top_left in passed_list) and (mid_left in passed_list) and (bottom_left in passed_list):
            equation = [top_left, mid_left, bottom_left, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_left, mid_left, bottom_left], 3)
                if status:
                    self.knowledge_base.append(equation)
                # else:
                #     self.update_duplicate([top_left, mid_left, bottom_left], 3, clue)

            c = clue[0] - 1
            c = [c]
            equation = [top_left, mid_left, c]  # a + d
            if (equation not in self.knowledge_base) and c[0] >= 0:
                status = self.check_duplicate([top_left, mid_left], 2)
                if status:
                    self.knowledge_base.append(equation)
                # else:
                #     self.update_duplicate([top_left, mid_left], 2, c)

            equation = [mid_left, bottom_left, c]  # d + g
            if (equation not in self.knowledge_base) and c[0] >= 0:
                status = self.check_duplicate([mid_left, bottom_left], 2)
                if status:
                    self.knowledge_base.append(equation)
                # else:
                #     self.update_duplicate([mid_left, bottom_left], 2, c)

        else:
            if (top_left in passed_list) and (mid_left in passed_list):  # a + d
                equation = [top_left, mid_left, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([top_left, mid_left], 2)
                    if status:
                        self.knowledge_base.append(equation)
                    # else:
                    #     self.update_duplicate([top_left, mid_left], 2, clue)

            if (mid_left in passed_list) and (bottom_left in passed_list):  # d + g
                equation = [mid_left, bottom_left, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([mid_left, bottom_left], 2)
                    if status:
                        self.knowledge_base.append(equation)
                    # else:
                    #     self.update_duplicate([mid_left, bottom_left], 2, clue)

        ############ RIGHT ROW ################

        if (top_right in passed_list) and (mid_right in passed_list) and (bottom_right in passed_list):  # c + f + i
            equation = [top_right, mid_right, bottom_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_right, mid_right, bottom_right], 3)
                if status:
                    self.knowledge_base.append(equation)
                # else:
                #     self.update_duplicate([top_right, mid_right, bottom_right], 3, clue)

            c = clue[0] - 1
            c = [c]
            equation = [top_right, mid_right, c]
            if (equation not in self.knowledge_base) and c[0] >= 0:
                status = self.check_duplicate([top_right, mid_right], 2)
                if status:
                    self.knowledge_base.append(equation)
                # else:
                #     self.update_duplicate([top_right, mid_right], 2, c)

            equation = [mid_right, bottom_right, c]
            if (equation not in self.knowledge_base) and c[0] >= 0:
                status = self.check_duplicate([mid_right, bottom_right], 2)
                if status:
                    self.knowledge_base.append(equation)
                # else:
                #     self.update_duplicate([mid_right, bottom_right], 2, c)

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

        # form_equation
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
        for index in self.knowledge_base:  # index is the equations in knowledge base
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

    def remove_mine_from_kb(self, i, j):
        var_0 = var_1 = var_2 = 0
        for i in self.knowledge_base:
            if [i, j] in i:
                clue = i[-1]
                clue = clue[0]

                if len(i) == 2:  # (a,0)
                    clue = i[-1]
                    clue = clue[0]
                    if clue>1:
                        clue = clue - 1
                        eq = [i[0] , [clue]]
                        self.knowledge_base.remove(i)
                        self.knowledge_base.append(eq)
                    #self.knowledge_base.remove(i)

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

    # this func helps subset look at equation and return value of a+b or b+c from a+b+c equation
    def subset_helper(self, var_1, var_2):
        # print(" in subset helper -------")
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

            for i in range(0, 9):
                eq = [var_1, var_2, [i]]
                if eq in self.knowledge_base:
                    val = eq[-1]
                    val = val[0]
                    # print("-------------------- true for eq : eq[", i, "] | Val is : ", val)
                    break
            return val
        return None

    def subset(self, passed_list, val):  # note: we are only for solving subset for 3 eqs for now
        # val is the clue val
        if len(passed_list) > 2:
            val = val[0]
            var_1 = passed_list[0]
            var_2 = passed_list[1]

            # if len(passed_list) == 6:
            #
            #     for i in range(1,5):
            #         var_a = passed_list[i-1]
            #         var_b = passed_list[i]
            #         ret_val = self.subset_helper(var_a, var_b)
            #         if ret_val != None:
            #             break

            if len(passed_list) >= 4:

                for i in range(0, 9):
                    ret_val = self.subset_helper(var_1, var_2)

                if ret_val != None:
                    if var_1 in passed_list and var_2 in passed_list:
                        clue = passed_list[-1]
                        clue = clue[0]
                        if clue != 0:
                            var_3 = val - ret_val  # a+b+c, ret_val = a + b

                            print("44444444444444444444444444444444444444444444444444444444444444444444444")
                            print(" This is the csp eq :" , passed_list)
                            print( "Clue : " , val , " | " , passed_list[-1] )
                            print(passed_list)
                            print("(", var_1, " + ", var_2, "):", ret_val)

                            # if ret_val == clue: # in this case var_3 is safe
                            #     c_1 = c_2 = None
                            #     for i in self.knowledge_base:
                            #         if len(i) == 2:
                            #             if var_1 in i:
                            #                 c_1 = i[-1]
                            #                 c_1 = c_1[0]
                            #             if var_2 in i:
                            #                 c_2 = i[-1]
                            #                 c_2 = c_2[0]
                            #
                            #     if c_1 == None or c_2 == None:
                            #         a=1
                            #     else:
                            #         sum = c_1 + c_2
                            #         if sum== clue:
                            #             nl = []
                            #             if c_1 == 1:
                            #                 nl.append(c_1)
                            #             if c_2 == 2:
                            #                 nl.append(c_2)
                            #             return nl
                            # else:
                            #     sum = var_3 + ret_val
                            #     # if sum == val:
                            #     #     return passed_list[2]
                            #     if var_3 != 0:
                            #         sum = var_3 + ret_val
                            #         if sum == val:
                            #             print(passed_list[2])
                            #             return passed_list[2]

                            sum = var_3 + ret_val
                            # if sum == val:
                            #     return passed_list[2]
                            if var_3 != 0:
                                sum = var_3 + ret_val
                                if sum == val:
                                    print(passed_list[2])
                                    return passed_list[2]

                else:
                    var_2 = passed_list[1]
                    var_3 = passed_list[2]
                    ret_val = self.subset_helper(var_2, var_3)
                    if ret_val != None:

                        if var_2 in passed_list and var_3 in passed_list:

                            # print("This equation is being passed to subset ", passed_list)

                            var_1 = val - ret_val

                            # print("Clue val : ", val)
                            # print("return val", ret_val)
                            # print("var a ", var_1)

                            if var_1 != 0:
                                sum = var_1 + ret_val
                                if sum == val:
                                    print("var a : ", passed_list[1])
                                    return passed_list[1]

            if len(passed_list) == 3:  # (a,b,0)
                var_1 = passed_list[0]
                var_2 = passed_list[1]
                rt_list = []

                # print( "pasing : " , var_1 , ", " , var_2 )

                val_1 = self.get_info(var_1, 2)
                val_2 = self.get_info(var_2, 2)

                # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                # print(val_1)
                # print(val_2)

                if val_1 != None and val_2 != None:

                    if val_1 != None:
                        # print("get_info" , val_1)

                        val_1 = val_1[-1]
                        val_1 = val_1[0]

                    if val_2 != None:
                        # print("get_info" , val_2)

                        val_2 = val_2[-1]
                        val_2 = val_2[0]

                    if (val_1 + val_2) == val:
                        if val_1 != 0:
                            rt_list.append(var_1)
                        if val_2 != 0:
                            rt_list.append(var_2)
                    return rt_list
                return False
        return False

    def equation_solver_csp(self, passed_list, hidden_neighbors, length, passed_cell):
        # passed list is just the list with equations of neighbor cells of current cell to determine if safe or not
        # NOTE: SOLVE THIS: I AM GETTING VARIABLES THAT SHARE NEIGHBORS WITH OTHERS - GET EQUATIONS THAT ONLY SHARE
        var_that_are_true = []
        check = 0
        # note : index is the whole equation e.g [a,b,1] etc

        # remove one var eq from list
        for i in passed_list:
            if len(i) == 2:
                passed_list.remove(i)

        # print("equation_solver_csp - " , passed_list)

        for index in passed_list:
            clue = index[-1]

            if len(index) == 2:  # a + b

                # print(" Eq length is 1 (a,b,0) - D D D D DD D D D D D DD D D D D D DD D D D D D DD D D D D D DD D D D D D DD D  ")

                val_1 = self.get_info(index[0], 2)
                val = val_1[-1]
                val = val[0]
                if val == 1:
                    var_that_are_true.append(index[0])
                    if index[0] in hidden_neighbors:
                        hidden_neighbors.remove(index[0])
                    # print("After removing cell from neighbor list: ", hidden_neighbors)

            # Eq (a,b,0) is not solvable b
            if len(index) == 3:  # a + b

                # print(" Eq length is 3 (a,b,0) - Z Z Z Z Z Z Z Z ZZ Z Z Z Z ZZ Z Z Z   Z Z Z Z ZZ Z Z Z Z ZZ  Z Z Z Z ZZ Z Z Z Z ZZ ")

                returned_cell = self.subset(index, clue)

                # print()
                # print("Value returned , " , returned_cell)

                if returned_cell:
                    for i in returned_cell:  # as im returning a nested list thats why I need the for loop e.g [ [] ] and
                        # others are returning just []
                        var_that_are_true.append(i)

                # print("before removing cell from neighbor list: ", hidden_neighbors)

                if returned_cell in hidden_neighbors:
                    hidden_neighbors.remove(returned_cell)

                # print("After removing cell from neighbor list: ", hidden_neighbors)

            # Equation (a,b,c,0) only in this condition
            if len(index) >= 4:  # a + b + c

                # print(" Eq length is 4 (a,b,0) - R R R R R R R R R R RR R R  R R R R R R R R R R R R R R RR R R  R R R R  ")
                # if subset returns false then we go to else condition as current csp equation cannot be solved
                # by subset

                returned_cell = self.subset(index, clue)  # returned_cell is the cell we think is a mine

                if returned_cell != False:  # This condition confirms subsets can be solved
                    # print("Subset ============================")
                    # print("returned cell from Subset method : ", returned_cell)

                    if returned_cell:

                        if len(returned_cell) >1:
                            for i in returned_cell:
                                var_that_are_true.append(returned_cell)
                        else:
                            var_that_are_true.append(returned_cell)

                    if len(returned_cell) > 1:
                        for i in returned_cell:
                            if i in hidden_neighbors:
                                hidden_neighbors.remove(i)
                    else:
                        if returned_cell in hidden_neighbors:
                            hidden_neighbors.remove(returned_cell)

        return var_that_are_true


    def update_cell(self, cells_to_flag):
        for i in cells_to_flag:
            for eqs in self.knowledge_base:
                if len(eqs) == 2:
                    if i in eqs:
                        clue = eqs[-1]
                        clue = clue[0]
                        if clue != 0 and clue != 1:
                            self.knowledge_base.remove(eqs)
                            new_eq = [i, [1]]
                            self.knowledge_base.append(new_eq)


    def csp_solver(self, neighbor_list, passed_cell):
        hidden_neighbors_list = self.get_hidden_cells_list(neighbor_list)  # gets a list of cells for each neighbor

        # passed_cell is revealed cell that is being removed from knowledge base after its been revelaed down below
        for index in self.knowledge_base:
            if passed_cell in index:
                self.delete_var(passed_cell)

        # Gets the csp equations
        eq_of_neighbor_cells = []  # This list contains csp eq from kb of required cells

        for index in hidden_neighbors_list:  # iterate cell by cell e.g index is [0,1] then [0,2] then [0,3] etc
            self.search_knowledge_base(index, hidden_neighbors_list,
                                       eq_of_neighbor_cells)  # each hidden neighbor cell is prcoessed here

        # self.skb_helper(hidden_neighbors_list , eq_of_neighbor_cells)    # removes eq that have var not in neighbors

        cells_to_flag = self.equation_solver_csp(eq_of_neighbor_cells, hidden_neighbors_list,
                                                 len(hidden_neighbors_list), passed_cell)

        self.update_cell(cells_to_flag)

        print("current cell : " , passed_cell)
        print("neighbors that should be flagged list:", cells_to_flag)
        for i in hidden_neighbors_list:
            for j in self.knowledge_base:
                if [i, [1]] in j:
                    print(" After going through equation_csp_solver - ************************************* ", j)

        print("Safe cell : ",
              hidden_neighbors_list)  # this hidden_neighbors contains only neighbors that are deemed safe
        print("hidden neighbors list : ", hidden_neighbors_list)
        print("cells_to_flag from equation_solver_csp : ", cells_to_flag)

        # for i in cells_to_flag:
        #     if i not in self.flagged_cells:
        #         self.flagged_cells.append(i)

        # self.flag_cells_csp(cells_to_flag)

        # if len(hidden_neighbors_list)<=3:
        #     self.flag_cells_csp(cells_to_flag)
        cells_to_flag_without_dups = []
        a= []
        if cells_to_flag:
            for i in cells_to_flag:
                if i not in cells_to_flag_without_dups:
                    cells_to_flag_without_dups.append(i)

            for cell in cells_to_flag_without_dups:
                for i in self.knowledge_base:
                    if len(i) == 2:
                        if cell in i:
                            clue = i[-1]
                            if clue[0] == 1:
                                a.append(cell)

            self.flagcells_consider.clear()
            # flagcells_consider will add this list of flagged cells in list of flagged cells in traverse
            for i in cell:
                if cell not in self.flagcells_consider:
                    self.flagcells_consider.append(cell)

            #self.flag_cells_csp(cell)

        return hidden_neighbors_list

    # returns csp equations with required cell in it
    def search_knowledge_base(self, cell, listOfNeighbors, used_list):
        for i in self.knowledge_base:
            if cell in i:
                if i not in used_list:
                    used_list.append(i)

    def skb_helper(self, hidden_neigh, used_list):
        for i in used_list:
            if len(i) > 2:
                for j in i:
                    if len(j) > 1:
                        if j not in hidden_neigh:
                            if i in used_list:
                                used_list.remove(i)

    def highlight_board_agent(self, i, j):
        # status = self.environment_obj.get_cell_value( self.environment_obj.board_array, i, j)
        status = self.environment_obj.get_cell_value(self.array_board, i, j)
        if status != 1:
            # color = (150, 150, 150)
            # val = self.environment_obj.get_clue( self.environment_obj.board_array, i, j)
            val = self.environment_obj.get_clue(self.array_board, i, j)
            if val == 0:
                self.environment_obj.color_cell('', i, j, 0)
            else:
                self.environment_obj.color_cell(str(val), i, j, 0)
        elif status == 1:  # IF THE CELL IS A MINE
            color = (255, 0, 0)
            self.environment_obj.color_cell('', i, j, 1)

    def remove_dup_list(self,passed_list):
        n_list = []
        for i in passed_list:
            if i not in n_list:
                n_list.append(i)
        return n_list


    def flag_mine(self,i,j, status):
        self.environment_obj.color_cell("", i, j, status)  # This code marks the cell on GUI board
        self.mine_cells.append([i, j])  # when a mine is found on revealing cell it is added to mine_cells
        self.mine_count += 1
        self.remove_mine_from_kb(i, j)
        if [i, j] in self.unvisited_cells:
            self.unvisited_cells.remove([i, j])

    # Functionality: checks current_cell neighbors and determine which cell is a hidden cell, which cell is already
    # visited and what cell is a mine
    def constraint_cell_processing(self, i, j):
        print("-----")
        print(self.array_board)
        status = self.environment_obj.get_cell_value(self.array_board, i, j)
        obj = self.get_cur_cell_instance([i, j])

        if status == 1 and self.mine_count < self.mines_left :
            self.flag_mine(i,j,1)

        if status != 1 or self.mine_count >= self.mines_left:
            self.visited_cells.append([i, j])  # adds current processed cell in list of visited cells if its safe
            if [i, j] in self.unvisited_cells:
                self.unvisited_cells.remove([i, j])  # removing index from unvisited cells
            obj.status = 0  # identifies the index as safe by marking it 0

            obj.clue = self.environment_obj.get_clue(self.array_board, i, j)
            # assigns clue (clue is number of mines in adjacent neighbors

            if obj.clue == 0:
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

            # I need to get get a list of hidden cells from neighbors
            # Returns unrevealed neighbor cells of the list current_neighbors
            ret_list = self.flag_cells_as_safe(current_neighbors)

            cell_to_delete = [i, j]
            self.delete_var(cell_to_delete)  # Removes revealed cell from KB
            return ret_list

        return []

    # returns csp equation from knowledge base of desired length
    def get_info(self, val, equation_length):
        # if equation_length == 2 (a,0) , if == 3 (a,b,0), if == 4 (a,b,c,0)
        # val passed should be in the form [i,j]
        for index in self.knowledge_base:
            if val in index:
                if len(index) == equation_length:
                    return index


    # Functionality: This function takes a list, and uses process_current_cell to process each cell
    def traverse(self, list_cells):
        while self.unvisited_cells:
            time.sleep(0)
            self.cell_traverse_list(list_cells)  # add passed list to list of cells to be explored

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

            # VERY VERY VERY IMPORTANT 786
            # Try this approach: - dont discard the clue from the very start
            # keep a stack of cells to visit and a stack of cells that you think are mines
            # open few cells but dont flag anything
            # but once you have around 5-6 cells opened then try to go back to the stack of cells you think are mines
            # and recalculate for them if they are mines and then start flagging mines.
            #     At that point of the program you should have a pretty long stack of cells you think are mines so you should
            # be able to get something - Note: do not just pick the cell from the suspicious list and mark them - take the cell
            # and then re-evaluate that cell by going through the KB again and seeing if it can be determined that cell is mine or not

            if self.traverse_cells:
                index = self.traverse_cells.pop(0)
                index_board_i = index[0]
                index_board_j = index[1]
                clue = -9
                for i in self.knowledge_base:
                    if len(i)==2:
                        if [index_board_i, index_board_j] in i:
                            clue = i[-1]
                            clue = clue[0]
                if clue != 1:
                    list_cells = self.constraint_cell_processing(index_board_i, index_board_j)

                    # check neighbr of neighbor on left right top and above
                    # then get neighbor of current cell
                    # get common cells in all these lists
                    # and check which of those cells are equal to 1 thosea are mines
                    n_list_left = n_list_right = n_list_top = n_list_bottom = []
                    if index_board_i-2 > 0:
                        n_list_left = self.get_neighbors_current_cell(index_board_i - 2, index_board_j)

                    if index_board_i+2 < self.row:
                        n_list_right= self.get_neighbors_current_cell( index_board_i + 2, index_board_j )

                    if index_board_j - 2 > 0:
                        n_list_top = self.get_neighbors_current_cell( index_board_i, index_board_j - 2 )

                    if index_board_j + 2 < self.row:
                        n_list_bottom = self.get_neighbors_current_cell( index_board_i, index_board_j + 2 )
                    common_list = []

                    for i in list_cells:
                        if i in n_list_left and i in n_list_right and i in n_list_top and i in n_list_bottom:
                            if i not in common_list:
                                common_list.append(i)

                        if i in n_list_right:
                            if i not in common_list:
                                common_list.append(i)

                        if i in n_list_top:
                            if i not in common_list:
                                common_list.append(i)

                        if i in n_list_bottom:
                            if i not in common_list:
                                common_list.append(i)


                    fl = []
                    for cell in common_list:
                        for i in self.knowledge_base:
                            if len(i) == 2:
                                if cell in i:
                                    clue = i[-1]
                                    print("IT Exists")
                                    print(i)
                                    print(clue)
                                    clue = clue[0]
                                    if clue==1:
                                        if cell not in fl:
                                            fl.append(cell)

                    print(" TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT ")
                    # print()
                    # print(n_list_left)
                    # print(n_list_right)
                    # print(n_list_top)
                    # print(n_list_bottom)
                    print()
                    print("common list:" , common_list)
                    print( "Mines:>  ", fl)
                    print(" TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT ")

                    #self.flagged_cells.append([ index_i,index_j ])
                    print("--------------------------------------------------------------------------------")


                else:
                    list_cells = []
                    self.flagcells_consider.append( [index_board_i, index_board_j] )

                #adding new flagged cells to an already existing list of cells that need to be flagged
                for i in self.flagcells_consider:
                    if i not in self.flagged_cells:
                        self.flagged_cells.append(i)

                if list_cells:  # If not empty()
                    # val = self.environment_obj.get_clue(self.environment_obj.board_array, index_board_i, index_board_j)
                    val = self.environment_obj.get_clue(self.array_board, index_board_i, index_board_j)

                    self.highlight_board_agent(index_board_i, index_board_j)
                    self.var_removed_confirmed([index_board_i, index_board_j])
                    self.form_equation(list_cells, val, [index_board_i, index_board_j])
                    self.csp_solver(list_cells, [index_board_i, index_board_j])



                # Flags mines here
                if len(self.flagged_cells) >= 4 :
                    fgc = self.flagged_cells.pop(0)
                    index_i = fgc[0]
                    index_j = fgc[1]
                    neigh_list = self.get_neighbors_current_cell(index_i,index_j)
                    for i in neigh_list:
                        if i in self.visited_cells:
                            neigh_list.remove(i)

                    eq_neighbor_cells = []  # This list contains csp eq from kb of required cells

                    for index in neigh_list:  # iterate cell by cell e.g index is [0,1] then [0,2] then [0,3] etc
                        self.search_knowledge_base(index, neigh_list,eq_neighbor_cells)
                    # self.skb_helper(hidden_neighbors_list , eq_of_neighbor_cells)    # removes eq that have var not in neighbors
                    cells_to_flag = self.equation_solver_csp(eq_neighbor_cells, neigh_list,
                                                             len(neigh_list), [index_i,index_j])
                    cells_to_flag = self.remove_dup_list(cells_to_flag)
                    self.update_cell(cells_to_flag)
                    nl = []
                    for i in cells_to_flag:
                        for j in self.knowledge_base:
                            if len(j) == 2:
                                if i in j:
                                    clue = j[-1]
                                    clue = clue[0]
                                    if clue == 1:
                                        if i not in nl:
                                            nl.append(i)
                                    self.knowledge_base.remove(j)

                    for i in nl:
                        if i not in self.flagged_cells:
                            nl.remove(i)


                    index_i = fgc[0]
                    index_j = fgc[1]

                    for i in self.knowledge_base:
                        if len(i) == 2:
                            #print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                            if [index_i,index_j] in i:
                                #print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                                clue = i[-1]
                                clue = clue[0]
                                if clue == 1:
                                    #print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                                    self.flag_cells_csp( [index_i,index_j] )
                    print()


            # in case our list_cells or traverse_cells is empty
            else:
                self.traverse_cells.append(self.unvisited_cells.pop())





            # if self.traverse_cells:
            #     index = self.traverse_cells.pop(-1)
            #     index_board_i = index[0]
            #     index_board_j = index[1]
            #
            #     list_cells = self.constraint_cell_processing(index_board_i, index_board_j)
            #
            #     if list_cells:  # If not empty()
            #         # val = self.environment_obj.get_clue(self.environment_obj.board_array, index_board_i, index_board_j)
            #         val = self.environment_obj.get_clue(self.array_board, index_board_i, index_board_j)
            #
            #         self.highlight_board_agent(index_board_i, index_board_j)
            #         self.var_removed_confirmed([index_board_i, index_board_j])
            #         self.form_equation(list_cells, val, [index_board_i, index_board_j])
            #         safe_cells_to_traverse = self.csp_solver(list_cells, [index_board_i, index_board_j])
            #         for i in safe_cells_to_traverse:
            #             self.environment_obj.color_cell('T', i[0], i[1], 'testing')
            #
            # # in case our list_cells or traverse_cells is empty
            # else:
            #     self.traverse_cells.append(self.unvisited_cells.pop())

        if not self.unvisited_cells:
            print(self.knowledge_base)
            print()
            print("cells left to visit: , " , self.unvisited_cells)
            print("traverse: , ", self.traverse_cells)

            print("EXITING ")

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
