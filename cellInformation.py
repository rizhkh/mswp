import numpy as np

# Idea for using this obj: each cell will be an object that will be stored in reference to each cell index on 2d array by index position

class cell:
    current_position = None # index in 2d array or matrix
    status = None   # whether or not it is a mine or safe
    clue = None # if safe, the number of mines surrounding it indicated by the clue
    safe_n = None   # already revealed cells that are not flagged
    appearing_mines_in_neighbors = None # number of flagged cells around it or mines
    cells_still_unexplored_in_neighbors = None  # number of unexplored neighbors around it

    def __init__(self, index, status, mines_surrounding_it_clue, safe_neighbors, mines_indentified_around, hidden_cells_around):
        self.current_position = index
        # whether or not it is a mine or safe
        self.status = status  # unVisited, Flagged or safe - un_visited = 'un-visited' ,Flagged = 1 , safe = 0
        # if safe, the number of mines surrounding it indicated by the clue
        self.clue = mines_surrounding_it_clue  # If this is not safe store value as 'not safe'
        # the number of safe squares identified around it
        self.safe_n = safe_neighbors  # already revealed cells that are not flagged
        # the number of mines identified around it.
        self.appearing_mines_in_neighbors = mines_indentified_around  # number of flagged cells around it or mines
        # the number of hidden squares around it
        self.cells_still_unexplored_in_neighbors = hidden_cells_around  # number of unexplored neighbors around it

    def get_current_position(self):
        return self.current_position

    def set_current_position(self,index):
        self.current_position = index

    def set_cell_status(self,status):
        # whether or not it is a mine or safe
        self.status = status  # Flagged or not - Flagged = 1 , not_flagged= 0

    def set_mines_surrounding_cell(self,mines_surrounding_it_clue):
        # if safe, the number of mines surrounding it indicated by the clue
        self.clue = mines_surrounding_it_clue  # If this is not safe store value as 'not safe'

    def set_safe_neighbors(self,safe_neighbors):
        # the number of safe squares identified around it
        self.safe_n = safe_neighbors  # already revealed cells that are not flagged

    def set_flagged_mines_around_current_cell(self,mines_indentified_around):
        # the number of mines identified around it.
        self.appearing_mines_in_neighbors = mines_indentified_around  # number of flagged cells around it or mines

    def set_hidden_cells_around_current_cell(self,hidden_cells_around):
        # the number of hidden squares around it
        self.cells_still_unexplored_in_neighbors = hidden_cells_around  # number of unexplored neighbors around it

    def print_cell_info(self):
        print("-----")
        print("Index :" , self.current_position)
        print("Visited, Flagged or Safe :" , self.status)
        print("Clue :" , self.clue)
        print("Revealed cells in neighbors :" , self.safe_n)
        print("mines or flagged cells in neighbors: " , self.appearing_mines_in_neighbors)
        print("unexplored neighbors around :" , self.cells_still_unexplored_in_neighbors)
        print("-----")