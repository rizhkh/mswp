import pygame as pygame
import numpy as np
#import random
#import alg
import time
from ast import literal_eval
from sys import exit
from collections import deque

# To comment blocks of code press ctrl + /
from mswp.boardenvironment import environment
from mswp.agent import Agnt

class start:
    PYGAMEWIDTH = 300  # 600   # Do not change this: This is window sizing
    PYGAMEHEIGHT = 300  # Do not change this: This is window sizing
    row = 10  # row
    col = 10  # col
    box_width = 19
    box_height = 19
    board_array = np.zeros((0, 0), dtype=int)
    board_array_2 = np.zeros((0, 0), dtype=int)
    #board_array = np.zeros((0, 0), dtype=object)
    screen = None
    screen_two = None

    list_of_all_rects = []

    recent_clicked_rect_x = None
    recent_clicked_rect_y = None

    environment_class = None
    agent_class = None

    total_mines = 0

    def __init__(self, scree_one):
        self.screen = scree_one


    def get_arr(self):
        return self.board_array

    def get_all_rects(self):
        return self.environment_class.get_all_rects() #self.list_of_all_rects

    def highlight_board(self,i,j):
        # canvas_arr_i = i * 20  # the reason it is being multiplied is because the cell size is set to 20 - if its the orignal value then it causes GUI problems
        # canvas_arr_j = j * 20
        status = self.environment_class.get_cell_value(self.board_array,i,j)
        if status != 1:
            #color = (150, 150, 150)
            val = self.environment_class.get_clue(self.board_array,i,j)
            #self.environment_class.rect_clicked( str(val) , color, canvas_arr_i,canvas_arr_j)
            self.environment_class.color_cell(str(val), i, j,0)
        elif status == 1:   # IF THE CELL IS A MINE
            color = (255, 0, 0)
            self.total_mines += 1
            #self.environment_class.rect_clicked('', color, canvas_arr_i, canvas_arr_j)
            self.environment_class.color_cell('', i, j,1)

    # This function works just once - you click once that is it - the rest is auto movement
    def click_cell(self,obj,i,j):
        obj = self.environment_class  # do not remove this - obj variable is being passed the reference of global obj this way the refernce is copied in start_algorithm
        # and we dont have pass any obj in main.py

        # we are dividing by 20 due do GUI dimension for pycharm - its a scaling issue in GUI
        index_board_i= int(i/20)
        index_board_j= int(j/20)
        # after this wherever we send i and j we dont need to worry about rescaling issues

        #print("index: " , index_board_i , ",", index_board_j)
        val = obj.get_clue(self.board_array , index_board_i, index_board_j)
        self.highlight_board(index_board_i,index_board_j)

        # returned_list =  self.agent_class.process_current_cell(index_board_i,index_board_j)
        # #print(returned_list)
        # # Note: MAKE SURE TO CHECK IF THE NEIGHBOR LIST HAS ANY CELL THAT HAS BEEN REVEALED OR MARKED AS A MINE/FLAGGED
        # self.agent_class.form_equation(returned_list, val, [index_board_i,index_board_j])

        #self.agent_class.csp_solver(returned_list)


        returned_list =  self.agent_class.process_current_cell_csp(index_board_i,index_board_j)
        #print(returned_list)
        # Note: MAKE SURE TO CHECK IF THE NEIGHBOR LIST HAS ANY CELL THAT HAS BEEN REVEALED OR MARKED AS A MINE/FLAGGED
        self.agent_class.form_equation(returned_list, val, [index_board_i,index_board_j])

        # add a new func that removes duplicates from kb - takes its first element and traverses rest of the kb and if it finds a duplicate it deletes it

        self.agent_class.csp_solver(returned_list, [index_board_i,index_board_j])

        #self.agent_class.traverse_board(returned_list) # to automate movement

        #self.highlight( returned_list )

    def forSimpleWindow(self):
        for i in range(0 , len( self.board_array_2) ):
            for j in range(0, len( self.board_array_2 )):
                status = self.environment_class.get_cell_value(self.board_array_2,i,j)

    def highlight_board_empty(self,i,j):
        # canvas_arr_i = i * 20  # the reason it is being multiplied is because the cell size is set to 20 - if its the orignal value then it causes GUI problems
        # canvas_arr_j = j * 20
        status = self.environment_class.get_cell_value(self.board_array,i,j)
        if status != 1:
            #color = (150, 150, 150)
            val = self.environment_class.get_clue(self.board_array,i,j)
            #self.environment_class.rect_clicked( str(val) , color, canvas_arr_i,canvas_arr_j)
            self.environment_class.color_cell(str(val), i, j,0)
        elif status == 1:   # IF THE CELL IS A MINE
            color = (255, 0, 0)
            self.total_mines += 1
            #self.environment_class.rect_clicked('', color, canvas_arr_i, canvas_arr_j)
            self.environment_class.color_cell('', i, j,1)

    def start_algorithm(self, obj):

        self.board_array = np.zeros((self.row, self.col), dtype=int)

        self.board_array_for_agent_info = np.copy(self.board_array)

        pygame.display.set_caption("MineSweeper", "MS")
        pygame.display.flip()

        self.environment_class = environment(self.screen, self.board_array, obj, self.box_height, self.box_width)

        #self.generate_board()   # This function draws the maze
        self.board_array = self.environment_class.add_mines_randomly(self.board_array)
        self.environment_class.generate_board(self.board_array)
        self.board_array_2 = np.copy(self.board_array)
        print(self.board_array) # shows map where the mines are

        self.agent_class = Agnt( self.board_array , self.row, self.col, self.box_height, self.box_width)
        self.agent_class.set_environment_obj(self.environment_class)    # because of this method agent class can use environment methods now

        pygame.display.flip()
