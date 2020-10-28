import numpy as np
import copy
from mswp.cellInformation import cell
import time


class Agnt:
    # all_cells = dict() #np.zeros((0, 0), dtype=int) # this list is total cells on the board
    all_cells = []  # this list is total cells on the board  # This would store the object of each cell that is visited
    # we use this list to access all stored information
    visited_cells = []  # just stores index of cells that are visited
    mine_cells = []  # list of cells that are mines and they have been revealed - not hidden on board anymore
    unvisited_cells = []
    safe_cells = []
    traverse_cells = []  # list of cells that needs to be processed / traversed
    knowledge_base = []
    mine_kb = []
    mines_left = 0
    mine_location = []
    mine_count = 0
    environment_obj = None
    board_array_agent = np.zeros((0, 0), dtype=int)
    array_board = np.zeros((0, 0), dtype=int)  # array val from startprm
    box_height = 0
    box_width = 0
    row = 0
    col = 0
    flagged_cells = []
    cells_that_are_flagged = []
    flagcells_consider = []
    mine_desntiy = 0

    def __init__(self, arr, row_dimension, col_dimenison, bh, bw):
        self.array_board = np.copy(arr)
        self.row = row_dimension
        self.col = col_dimenison
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

    # returns the object instance of the current cell from the list where it is stored - Used in process curr cell to
    # get the object of cell we are processing and update info
    def get_cur_cell_instance(self, key):
        for i in range(0, len(self.all_cells)):
            a = self.all_cells[i]
            if a[0] == key:
                obj = a[1]
                new_obj = copy.copy(a[1])
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
        if (clue-tot_mines) == (hidden_neighbor_mine):
        #if clue == (hidden_neighbor_mine + tot_mines):  # use this one
            return True
        return False

    def safe_estimator(self, clue, tot_rev_neighbors, hidden_neighbor_mine):
        if ((8 - clue) - tot_rev_neighbors) == (hidden_neighbor_mine):
        #if (8 - clue) == (hidden_neighbor_mine + tot_rev_neighbors):  # use this one
            return True
        return False

    def flag_cells_csp(self, current_neighbors):
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
        index_i = current_neighbors[0]
        index_j = current_neighbors[1]
        self.environment_obj.color_cell('', index_i, index_j, 'flag')

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
            index_i = i[0]
            index_j = i[1]
            self.environment_obj.color_cell('', index_i, index_j, 'flag')
        return neighbor

    # Returns a list of unrevealed neighbor cells
    def flag_cells_as_safe(self, current_neighbors):
        # returns a list of hidden cells in current_neighbors
        neighbor = self.get_hidden_cells_list(current_neighbors)
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
        return True

    def form_equation(self, passed_list, clue, current_cell):
        clue = [clue]
        # passed_list is the list of hidden neighbor cells current_cell position is being passed to make equations of
        # the neighboring cells as current_cell is the cell in being queried

        # a b c
        # d   f
        # g h i

        # adds single index with clue e.g a = val , b = val etc
        # for index in passed_list:
        #     # checks if any neighbor is already visited - if it has been revealed then we remove it from the list before
        #     # processing it
        #     if index in self.visited_cells:
        #         passed_list.remove(index)
        #     # if [ index , clue] not in self.knowledge_base:  # checks if neighbor list does not exist in knowledge base
        #     status = self.check_duplicate([index], 1)
        #     # if status is false call the update value method
        #     if status:
        #         self.knowledge_base.append([index, clue])

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



        ############ TOP ROW 5 elements #############################
        # 4 7 8 9 6

        # if a+b+c exists then a+b exist and b+c exists
        if (mid_left in passed_list) and (top_left in passed_list) and (top in passed_list) \
                and (top_right in passed_list) and (mid_right in passed_list):
            # make a+b+c = clue , then a+b = clue-1 and b+c = clue -1 whereas for a+b and b+c clue != 0
            equation = [mid_left, top_left, top, top_right, mid_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([mid_left, top_left, top, top_right, mid_right], 5)
                if status:
                    self.knowledge_base.append(equation)

        ############ Bottomw ROW 5 elements #############################
        # 4 1 2 3 6

        # if a+b+c exists then a+b exist and b+c exists
        if (mid_left in passed_list) and (bottom_left in passed_list) and (bottom in passed_list) \
                and (bottom_right in passed_list) and (mid_right in passed_list):
            # make a+b+c = clue , then a+b = clue-1 and b+c = clue -1 whereas for a+b and b+c clue != 0
            equation = [mid_left, bottom_left, bottom, bottom_right, mid_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([mid_left, bottom_left, bottom, bottom_right, mid_right], 5)
                if status:
                    self.knowledge_base.append(equation)

        ############ Left ROW 5 elements #############################
        # 8 7 4 1 2

        # if a+b+c exists then a+b exist and b+c exists
        if (top in passed_list) and (top_left in passed_list) and (mid_left in passed_list) \
                and (bottom_left in passed_list) and (bottom in passed_list):
            # make a+b+c = clue , then a+b = clue-1 and b+c = clue -1 whereas for a+b and b+c clue != 0
            equation = [top, top_left, mid_left, bottom_left, bottom, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top, top_left, mid_left, bottom_left, bottom], 5)
                if status:
                    self.knowledge_base.append(equation)

        ############ Right ROW 5 elements #############################
        # 8 9 6 3 2

        # if a+b+c exists then a+b exist and b+c exists
        if (top in passed_list) and (top_right in passed_list) and (mid_right in passed_list) \
                and (bottom_right in passed_list) and (bottom in passed_list):
            # make a+b+c = clue , then a+b = clue-1 and b+c = clue -1 whereas for a+b and b+c clue != 0
            equation = [top, top_right, mid_right, bottom_right, bottom, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top, top_right, mid_right, bottom_right, bottom], 5)
                if status:
                    self.knowledge_base.append(equation)



        # if a+b+c exists then a+b exist and b+c exists
        if (top_left in passed_list) and (top in passed_list) and (top_right in passed_list):
            # make a+b+c = clue , then a+b = clue-1 and b+c = clue -1 whereas for a+b and b+c clue != 0
            equation = [top_left, top, top_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_left, top, top_right], 3)
                if status:
                    self.knowledge_base.append(equation)

            c = clue[0] - 1  # so it is easier in subsets (a+B+C) -> a+b or B+c would be clue - 1
            c = [c]
            equation = [top_left, top, c]  # a + b
            if (equation not in self.knowledge_base) and c[0] >= 0:
                status = self.check_duplicate([top_left, top], 2)
                if status:
                    self.knowledge_base.append(equation)

            equation = [top, top_right, c]
            if (equation not in self.knowledge_base) and c[0] >= 0:  # b+c
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([top, top_right], 2)
                    if status:
                        self.knowledge_base.append(equation)

        else:
            if (top_left in passed_list) and (top in passed_list):  # a + b
                equation = [top_left, top, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([top_left, top], 2)
                    if status:
                        self.knowledge_base.append(equation)

            if (bottom in passed_list) and (bottom_right in passed_list):  # b + c
                equation = [bottom, bottom_right, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([bottom, bottom_right], 2)
                    if status:
                        self.knowledge_base.append(equation)
        # BOTTOM ROW

        if (bottom_left in passed_list) and (bottom in passed_list) and (bottom_right in passed_list):
            # a + b + c then a+b=clue-1 and b+c=clue-1
            equation = [bottom_left, bottom, bottom_right, clue]  # a + b + c
            if equation not in self.knowledge_base:
                status = self.check_duplicate([bottom_left, bottom, bottom_right], 3)
                if status:
                    self.knowledge_base.append(equation)

            c = clue[0] - 1
            c = [c]
            equation = [bottom_left, bottom, c]
            if (equation not in self.knowledge_base) and c[0] >= 0:  # a + b
                status = self.check_duplicate([bottom_left, bottom], 2)
                if status:
                    self.knowledge_base.append(equation)

            equation = [bottom, bottom_right, c]
            if (equation not in self.knowledge_base) and c[0] >= 0:  # b + c
                status = self.check_duplicate([bottom, bottom_right], 2)
                if status:
                    self.knowledge_base.append(equation)

        else:
            if (top in passed_list) and (top_right in passed_list):  # b + c
                equation = [top, top_right, clue]
                if equation not in self.knowledge_base:
                    if equation not in self.knowledge_base:
                        status = self.check_duplicate([top, top_right], 2)
                        if status:
                            self.knowledge_base.append(equation)

            if (bottom_left in passed_list) and (bottom in passed_list):  # a + b
                equation = [bottom_left, bottom, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([bottom_left, bottom], 2)
                    if status:
                        self.knowledge_base.append(equation)

        # LEFT COL

        if (top_left in passed_list) and (mid_left in passed_list) and (bottom_left in passed_list):
            equation = [top_left, mid_left, bottom_left, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_left, mid_left, bottom_left], 3)
                if status:
                    self.knowledge_base.append(equation)

            c = clue[0] - 1
            c = [c]
            equation = [top_left, mid_left, c]  # a + d
            if (equation not in self.knowledge_base) and c[0] >= 0:
                status = self.check_duplicate([top_left, mid_left], 2)
                if status:
                    self.knowledge_base.append(equation)

            equation = [mid_left, bottom_left, c]  # d + g
            if (equation not in self.knowledge_base) and c[0] >= 0:
                status = self.check_duplicate([mid_left, bottom_left], 2)
                if status:
                    self.knowledge_base.append(equation)

        else:
            if (top_left in passed_list) and (mid_left in passed_list):  # a + d
                equation = [top_left, mid_left, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([top_left, mid_left], 2)
                    if status:
                        self.knowledge_base.append(equation)

            if (mid_left in passed_list) and (bottom_left in passed_list):  # d + g
                equation = [mid_left, bottom_left, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([mid_left, bottom_left], 2)
                    if status:
                        self.knowledge_base.append(equation)

        # RIGHT ROW

        if (top_right in passed_list) and (mid_right in passed_list) and (bottom_right in passed_list):  # c + f + i
            equation = [top_right, mid_right, bottom_right, clue]
            if equation not in self.knowledge_base:
                status = self.check_duplicate([top_right, mid_right, bottom_right], 3)
                if status:
                    self.knowledge_base.append(equation)

            c = clue[0] - 1
            c = [c]
            equation = [top_right, mid_right, c]
            if (equation not in self.knowledge_base) and c[0] >= 0:
                status = self.check_duplicate([top_right, mid_right], 2)
                if status:
                    self.knowledge_base.append(equation)

            equation = [mid_right, bottom_right, c]
            if (equation not in self.knowledge_base) and c[0] >= 0:
                status = self.check_duplicate([mid_right, bottom_right], 2)
                if status:
                    self.knowledge_base.append(equation)

        else:
            if (top_right in passed_list) and (mid_right in passed_list):  # c + f
                equation = [top_right, mid_right, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([top_right, mid_right], 2)
                    if status:
                        self.knowledge_base.append(equation)

            if (mid_right in passed_list) and (bottom_right in passed_list):  # f + i
                equation = [mid_right, bottom_right, clue]
                if equation not in self.knowledge_base:
                    status = self.check_duplicate([mid_right, bottom_right], 2)
                    if status:
                        self.knowledge_base.append(equation)

    # Helper function for delete var
    def delete_var_helper(self, equation, cell_index):
        if cell_index in equation:
            for var in equation:
                if cell_index == var:
                    equation.remove(var)
                    return equation
        return []

    # Functionality: When a cell has been revealed - go through knowledge base and delete the var from equations
    def delete_var(self, cell_to_delete):
        for index in self.knowledge_base:  # index is the equations in knowledge base
            if cell_to_delete in index:
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

    def remove_mine_from_kb(self, index_i, index_j):
        var_0 = var_1 = var_2 = 0
        for i in self.knowledge_base:
            if [index_i, index_j] in i:
                self.delete_var([index_i, index_j])

    def subset_helper(self, var_1, var_2):
        # a + b + c = 2 => (a+b) + c and a+b = 1 we can deduce that c would be flagged as c=1
        if len(var_2) > 1:
            val = None

            for i in range(0, 9):
                eq = [var_1, var_2, [i]]
                if eq in self.knowledge_base:
                    val = eq[-1]
                    val = val[0]
                    break
            return val
        return None

    def subset(self, passed_list, val):  # note: we are only for solving subset for 3 eqs for now
        # val is the clue val
        if len(passed_list) > 2:
            val = val[0]
            var_1 = passed_list[0]
            var_2 = passed_list[1]

            if len(passed_list) == 4:

                for i in range(0, 9):
                    ret_val = self.subset_helper(var_1, var_2)

                if ret_val != None:
                    if var_1 in passed_list and var_2 in passed_list:
                        clue = passed_list[-1]
                        clue = clue[0]
                        if clue != 0:
                            var_3 = val - ret_val  # a+b+c, ret_val = a + b
                            #now confirm a + b == clue if it does means the third variable is not a mine
                            val_1 = self.get_info(var_1, 2)
                            val_2 = self.get_info(var_2, 2)
                            val_3 = self.get_info(passed_list[2], 2)

                            # Conditions below has now checked that a+b exists
                            # below it would plug values of a and b from kb and check
                            # if a+b is equal to value
                            if val_1 != None and val_2!= None:
                                v1_c = val_1[-1]
                                v1_c = v1_c[0]
                                v2_c = val_2[-1]
                                v2_c = v2_c[0]

                                confirm = val_1 + val_2
                                if confirm!=0 and confirm == ret_val:
                                    if var_3 != 0:
                                        sum = var_3 + ret_val
                                        if sum == val:
                                            return passed_list[2]

                                if v1_c == 0 and v2_c == 0 and val != 0:
                                    return passed_list[2]


                                if v1_c == 0 and v2_c != 0 and val != 0:
                                    if val_3 != None:
                                        v3_c = val_3[-1]
                                        v3_c = v3_c[0]

                                    if v1_c == val:
                                        return val_1[0]

                                    #return passed_list[2]

                                else:
                                    # what this condition does
                                    # Example:
                                    # ( [[1, 5], [1]]  +  [[2, 5], [1]] ) ==  1
                                    # returned cell:  False

                                    s = self.does_cell_exist(passed_list[2])
                                    if s==True:
                                        self.update_cell_val(passed_list[2],0)

                                    if s==False:
                                        self.knowledge_base.append( [passed_list[2] , [0]] )

                                    if v1_c == val and v2_c != val:
                                        return val_1[0]

                                    if v2_c == val and v1_c != val:
                                        return val_2[0]

                            if val_1 != None and val_3 != None:
                                v1_c = val_1[-1]
                                v1_c = v1_c[0]
                                v2_c = val_3[-1]
                                v2_c = v2_c[0]

                                confirm = val_1 + val_3
                                if confirm!=0 and confirm == ret_val:
                                    if var_3 != 0:
                                        sum = var_3 + ret_val
                                        if sum == val:
                                            return passed_list[2]

                                if v1_c == 0 and v2_c == 0 and val != 0:
                                    return passed_list[2]

                                else:
                                    # what this condition does
                                    # Example:
                                    # ( [[1, 5], [1]]  +  [[3, 5], [1]] ) ==  1
                                    # returned cell:  False

                                    s = self.does_cell_exist(passed_list[2])
                                    if s==True:
                                        self.update_cell_val(passed_list[2],0)

                                    if s==False:
                                        self.knowledge_base.append( [passed_list[2] , [0]] )
                                    if v1_c == val and v2_c != val:
                                        return val_1[0]
                                    if v2_c == val and v1_c != val:
                                        return val_3[0]

                            else:   # this condition gets csp value for each var and compares results then
                            # Example:
                            # ( None  +  [[0, 3], [1]]  +  [[0, 4], [0]] ) ==  1
                            # returned cell:  [0, 3]

                                if val_1 != None:
                                    v1_c = val_1[-1]
                                    v1_c = v1_c[0]
                                    if v1_c == val:
                                        return val_1[0]

                                if val_2 != None:
                                    v2_c = val_2[-1]
                                    v2_c = v2_c[0]
                                    if v2_c == val:
                                        return val_2[0]

                                if val_3 != None:
                                    v3_c = val_3[-1]
                                    v3_c = v3_c[0]
                                    if v3_c == val:
                                        return val_3[0]

                else:
                    var_2 = passed_list[1]
                    var_3 = passed_list[2]
                    ret_val = self.subset_helper(var_2, var_3)
                    if ret_val != None:

                        if var_2 in passed_list and var_3 in passed_list:
                            var_1 = val - ret_val
                            if var_1 != 0:
                                sum = var_1 + ret_val
                                if sum == val:
                                    return passed_list[1]

            if len(passed_list) == 3:  # (a,b,0)
                var_1 = passed_list[0]
                var_2 = passed_list[1]
                rt_list = []

                val_1 = self.get_info(var_1, 2)
                val_2 = self.get_info(var_2, 2)

                if val_1 != None and val_2 != None:

                    if val_1 != None:
                        val_1 = val_1[-1]
                        val_1 = val_1[0]

                    if val_2 != None:
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

        # NOT SURE ABOUT THIS ONE - CHECK THIS AGAIN $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        #remove one var eq from list
        for i in passed_list:
            if len(i) == 2:
                passed_list.remove(i)

        for index in passed_list:
            clue = index[-1]

            if len(index) == 2:  # a + b
                val_1 = self.get_info(index[0], 2)
                val = val_1[-1]
                val = val[0]
                if val == 1:
                    var_that_are_true.append(index[0])
                    if index[0] in hidden_neighbors:
                        hidden_neighbors.remove(index[0])

            # Eq (a,b,0) is not solvable b
            if len(index) == 3:  # a + b
                returned_cell = self.subset(index, clue)

                if returned_cell:
                    for i in returned_cell:  # as im returning a nested list thats why I need the for loop e.g [ [] ] and
                        # others are returning just []
                        var_that_are_true.append(i)

                if returned_cell in hidden_neighbors:
                    hidden_neighbors.remove(returned_cell)

            # Equation (a,b,c,0) only in this condition
            if len(index) >= 4:  # a + b + c
                returned_cell = self.subset(index, clue)  # returned_cell is the cell we think is a mine

                if returned_cell != False:  # This condition confirms subsets can be solved
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

    # updates cell in knowledge base
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

    def update_cell_val(self, cells_to_flag,val):
        for i in cells_to_flag:
            for eqs in self.knowledge_base:
                if len(eqs) == 2:
                    if i in eqs:
                        clue = eqs[-1]
                        clue = clue[0]
                        if clue != 0 and clue != 1:
                            self.knowledge_base.remove(eqs)
                            new_eq = [i, [val]]
                            self.knowledge_base.append(new_eq)

    # checks for len=1 variables only
    def does_cell_exist(self, cells_to_flag):
        check = 2
        for i in cells_to_flag:
            for eqs in self.knowledge_base:
                if len(eqs) == 2:
                    if i in eqs:
                        return True
        return False

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

        cells_to_flag = self.equation_solver_csp(eq_of_neighbor_cells, hidden_neighbors_list,
                                                 len(hidden_neighbors_list), passed_cell)
        self.update_cell(cells_to_flag)


        cells_to_flag_without_dups = []
        a= []
        if cells_to_flag: # removes dups from cells_to_flag
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
            val = self.environment_obj.get_clue(self.array_board, i, j)
            if val == 0:
                self.environment_obj.color_cell('', i, j, 0)
            else:
                self.environment_obj.color_cell(str(val), i, j, 0)
        if status == 1:  # IF THE CELL IS A MINE
            color = (255, 0, 0)
            self.environment_obj.color_cell('', i, j, 1)
        return status

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
        self.mines_left -= 1
        self.remove_mine_from_kb(i, j)
        if [i, j] in self.unvisited_cells:
            self.unvisited_cells.remove([i, j])

    # Functionality: checks current_cell neighbors and determine which cell is a hidden cell, which cell is already
    # visited and what cell is a mine
    def constraint_cell_processing(self, i, j):

        status = self.environment_obj.get_cell_value(self.array_board, i, j)
        obj = self.get_cur_cell_instance([i, j])

        if status == 1 and self.mine_count < self.mines_left :
            self.flag_mine(i,j,1)
            self.mine_location.append([i,j])

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
            if obj.clue == 0:
                self.safe_cells.append([i,j])

            ret_list = self.flag_cells_as_safe(current_neighbors)

            cell_to_delete = [i, j]
            duplicate_list = []

            # code below removes duplicates for single var equations
            for i in self.knowledge_base:
                if len(i) == 2:
                    if cell_to_delete in i:
                        duplicate_list.append(i)
            if duplicate_list:
                for i in duplicate_list:
                    for equation in self.knowledge_base:
                        if len(equation)==2:
                            if i[0] in equation:
                                self.knowledge_base.remove(equation)
                duplicate_list.clear()
            ##

            self.delete_var(cell_to_delete)  # Removes revealed cell from KB equations of len 3 and >
            self.knowledge_base.append( [ cell_to_delete,[0]] )
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

    def traverse(self, list_cells):
        while self.unvisited_cells:
            #time.sleep(1)
            self.cell_traverse_list_basic(list_cells)  # add passed list to list of cells to be explored

            if self.traverse_cells:
                # if len(self.traverse_cells)>1:
                #     index = self.traverse_cells.pop(1)
                # else:
                #     index = self.traverse_cells.pop(-1)
                index = self.traverse_cells.pop(0)
                index_board_i = index[0]
                index_board_j = index[1]
                clue = -9
                duplicate_removal = []
                for i in self.knowledge_base:
                    if len(i)==2:
                        if [index_board_i, index_board_j] in i:
                            # if i[0] not in duplicate_removal:
                            #     duplicate_removal.append(i[0])
                            #     clue = i[-1]
                            #     clue = clue[0]
                            clue = i[-1]
                            clue = clue[0]
                            break

                if clue != 1:
                    list_cells = self.constraint_cell_processing(index_board_i, index_board_j)

                else:
                    list_cells = []
                    self.flagcells_consider.append( [index_board_i, index_board_j] )

                #adding new flagged cells to an already existing list of cells that need to be flagged
                for i in self.flagcells_consider:
                    if i not in self.flagged_cells:
                        self.flagged_cells.append(i)

                if list_cells:  # This is where neighbor cells equations are formed
                    # val = self.environment_obj.get_clue(self.environment_obj.board_array, index_board_i, index_board_j)
                    val = self.environment_obj.get_clue(self.array_board, index_board_i, index_board_j)

                    status = self.highlight_board_agent(index_board_i, index_board_j)

                    if status != 1:
                        #self.var_removed_confirmed([index_board_i, index_board_j])
                        self.delete_var([index_board_i, index_board_j])
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
                    #self.skb_helper(neigh_list , eq_neighbor_cells)    # removes eq that have var not in neighbors
                    cells_to_flag = self.equation_solver_csp(eq_neighbor_cells, neigh_list,
                                                             len(neigh_list), [index_i,index_j])
                    cells_to_flag = self.remove_dup_list(cells_to_flag)
                    self.update_cell(cells_to_flag)
                    nl = []


                    index_i = fgc[0]
                    index_j = fgc[1]
                    for i in self.knowledge_base:
                        if len(i) == 2:
                            if [index_i,index_j] in i:
                                clue = i[-1]
                                clue = clue[0]
                                if clue == 1:
                                    self.flag_cells_csp( [index_i,index_j] )
                                    if [index_i,index_j] not in self.cells_that_are_flagged:
                                        self.cells_that_are_flagged.append([index_i,index_j])

                    # if self.cells_that_are_flagged:
                    #     for i in self.cells_that_are_flagged:
                    #         ret_list = self.get_neighbors_current_cell(i[0], i[1])
                    #         for j in ret_list:
                    #             if j in self.safe_cells:
                    #                 self.highlight_board(i[0], i[1])

            # in case our list_cells or traverse_cells is empty
            else:
                self.traverse_cells.append(self.unvisited_cells.pop())

        if not self.unvisited_cells:

            # time.sleep(3)
            # if self.cells_that_are_flagged:
            #     for i in self.cells_that_are_flagged:
            #         ret_list = self.get_neighbors_current_cell(i[0],i[1])
            #         for j in ret_list:
            #             if j in self.safe_cells:
            #                 self.highlight_board(i[0], i[1])
            #                 #self.cells_that_are_flagged.remove([i[0],i[1]])

            for i in range( 0 ,self.row):
                for j in range( 0 ,self.row):
                    ret_list = self.get_neighbors_current_cell( i, j)
                    status = self.environment_obj.get_cell_value(self.array_board, i, j)
                    val = self.environment_obj.get_clue(self.array_board, i, j)

                    mine_presence = 0
                    for n in ret_list:
                        if n in self.mine_location:
                            mine_presence += 1
                    if status == 0:
                        if mine_presence == val:
                            for n in ret_list:
                                if n in self.cells_that_are_flagged:

                                    self.highlight_board( n[0], n[1])

            print("Total mines found:", self.mine_count)
            print("Total cells flagged:", len(self.cells_that_are_flagged))



    def highlight_board(self,i,j):
        # canvas_arr_i = i * 20  # the reason it is being multiplied is because the cell size is set to 20 - if its the orignal value then it causes GUI problems
        # canvas_arr_j = j * 20
        status = self.environment_obj.get_cell_value(self.array_board ,i,j)
        if status != 1:
            val = self.environment_obj.get_clue(self.array_board,i,j)
            if val != 0:
                self.environment_obj.color_cell(str(val), i, j,0)
            if val == 0:
                self.environment_obj.color_cell('', i, j,0)
        elif status == 1:   # IF THE CELL IS A MINE
            self.environment_obj.color_cell('', i, j,1)

###################### CODE FOR BASIC ALGORITHM MIGHT HAVE TO COME BACK TO IT FOR GRAPH GENERATION REPORT

    #Functionality: checks current_cell neighbors and determine which cell is a hidden cell, which cell is already visited and what cell is a mine
    def process_current_cell(self, i, j):
    ## Functionality: checks current_cell neighbors and determine which cell is a hidden cell, which cell is already
    ## visited and what cell is a mine
        print("-----")
        print(self.array_board)
        status = self.environment_obj.get_cell_value(self.array_board, i, j)
        obj = self.get_cur_cell_instance([i, j])

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

            if obj.clue==0:
                self.environment_obj.color_cell('', i, j, 0)  # This code marks the cell on GUI boards
            else:
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
                self.delete_var(cell_to_delete) # Removes revealed cell from KB

                return ret_list

        return []


    # If a cell is flagged then this function will flag the cell
    def flag_cells_basic(self, current_neighbors):
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
    def flag_cells_as_safe_basic(self, current_neighbors):
        neighbor = self.get_hidden_cells_list(current_neighbors)
        for i in neighbor:
            obj = self.get_cur_cell_instance(i)
            obj.status = 1  # whether or not it is a mine or safe
            obj.status = 0  # whether or not it is a mine or safe
        return neighbor


    # Functionality: This function takes a list, and uses process_current_cell to process each cell
    def traverse_board(self, list_cells):
        # this will make sure all cells from the board are either flagged, or marked safe or as mine
        while self.unvisited_cells:
            time.sleep(0)
            self.cell_traverse_list_basic(list_cells)
            if self.traverse_cells:
                index = self.traverse_cells.pop(-1)
                index_board_i = index[0]
                index_board_j = index[1]
                list_cells = self.process_current_cell(index_board_i, index_board_j)
            else:
                self.traverse_cells.append( self.unvisited_cells.pop() )


        if not self.unvisited_cells:
            print("EXITING $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

    # This funcadds new list safe neighbors that needs to be explored to an already existing list with cells
    def cell_traverse_list_basic(self,list_cells):
        if len(list_cells) > 0:
            for i in list_cells:
                if i not in self.traverse_cells:
                    self.traverse_cells.append(i)
