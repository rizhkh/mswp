import numpy as np
from collections import deque
import random


class mazeGen:
    m = None    # empty object
    maze_array = []
    screen = None
    q = deque() # where list of active nodes are stored
    q_visited = []
    q_list_of_visited_nodes = []    #[[1,1]]
    start_i = 10    # starting index i for current node (parent node)
    start_j = 10    # starting index j for current node (parent node)

    def __init__(self , x, arr, obj):
        self.m = obj    #Copy the ref address in an empty obj -> point towards the orignal address
        self.screen = x
        self.maze_array = np.copy(arr)  # (obj.get_arr())

    # Functionality: Calculates the number of cell blocks to be included in the map using random generated probabily and dimension of the map
    def calc_prob(self):
        # prob = number of filled cells/NxN -> number of filled cells = prob * (NxN) - have an int set to number of filled cells , random whenever you num = 1 ,
        # set cell as filled and decrement number of filled cells n--
        p =  0.3 #random.uniform(0, 1)
        filled_cells = ( self.m.row * self.m.col) * p
        return  int(filled_cells)

    def maze_generate_DFS(self):
        # Algorithm: Add the starting position as parent node
        # Go to neighbor (using function call visit_neighbor_dfs)
        # that function calls func that checks if cell is visited or not
        filled_cells = []
        filled_cells.append(self.calc_prob())
        self.maze_array[self.start_i, self.start_j] = 1
        self.q.append( [self.start_i, self.start_j] )
        self.current_node(self.start_i, self.start_j)
        pos = self.q[-1]  # peek the top most element on stack
        i = pos[0]
        j = pos[1]
        self.visit_neighbor_dfs( i , j , filled_cells)    # down
        return self.maze_array

    def visit_neighbor_dfs(self, i , j, filled_cells):
        self.traverse_dfs(i - 1, j , filled_cells) # up
        self.traverse_dfs(i + 1, j , filled_cells)  # down
        self.traverse_dfs(i , j + 1 , filled_cells)   # right
        self.traverse_dfs(i, j - 1 , filled_cells)  # left
        if self.q:
            self.q.pop()    # the element will only pop after checking the moves to its neighbor are completed or not

    # Functionality:  To check cell is visited or not
    def traverse_dfs(self, i, j, filled_cells):
        num = random.randint(0, 2)
        if self.maze_array[i][j] == 0:
            if [i,j] not in self.q_list_of_visited_nodes:
                if num == 1 and filled_cells[-1] > 0:
                    f_c = filled_cells[-1]
                    f_c = f_c - 1
                    filled_cells.pop()
                    filled_cells.append(f_c)
                    self.q.append([ i, j])
                    self.maze_array[i][j] = 8
                    self.visit_neighbor_dfs(i, j, filled_cells)
                else:
                    pos = [i, j]
                    self.q.append(pos)
                    self.current_node(i, j)
                    self.maze_array[i][j] = 1
                    self.visit_neighbor_dfs(i, j, filled_cells)


    # Functionality: Follows BFS algorithm to generaze path. Whenever a random blocked cell is during the search process, BFS algorithm jumps to next neighbor in queue
    def maze_generate_BFS(self, array):
        filled_cells = []
        filled_cells.append(self.calc_prob())
        arr = array
        arr = self.visit_Neighbor_bfs(self.start_i, self.start_j, filled_cells , arr)
        self.current_node(self.start_i, self.start_j)   # Sets parent node as current node and adds it to list of visited nodes and in queue of nodes
        if not self.q:
            self.q.append([self.start_i, self.start_j])
        while self.q:
            #self.q_visited.pop()
            cur_n = self.q.popleft()    # Takes the element present at start in queue(where it stores neighbor) as active node
            start_point = cur_n[0] #get index i for current node
            end_point = cur_n[1]    #get index j for current node
            self.current_node(start_point, end_point)    #adds active node in list of visited nodes
            arr = self.visit_Neighbor_bfs(start_point - 1, end_point, filled_cells, arr)  # move up
            arr = self.visit_Neighbor_bfs(start_point + 1, end_point, filled_cells ,arr)  # move down
            arr = self.visit_Neighbor_bfs(start_point, end_point - 1, filled_cells, arr)  # move left
            arr = self.visit_Neighbor_bfs(start_point, end_point + 1, filled_cells, arr)  # move right
        #print(arr)
        return arr

    def visit_Neighbor_bfs(self, i, j, filled_cells, arr):
        num = random.randint(0, 1)
        #print(filled_cells)
        if [i,j] not in self.q_list_of_visited_nodes:   # Checks whether neighbor of current element has been visited or not
            if arr[i][j] == 0:
                if num == 1 and filled_cells[-1] > 0:   # Random decision using random.int - if condition is true then it would generate a blocked cell
                    f_c = filled_cells[-1]  # f_c and Filled_cells are the number of cells that has to be generated as blocks on map
                    f_c = f_c - 1
                    filled_cells.pop()
                    filled_cells.append(f_c)
                    self.q.append([i, j])
                    arr[i][j] = 8
                else:  # Generates open cells
                    pos = [i, j]
                    self.q.append(pos)
                    arr[i][j] = 1
        return arr

    # This function highlights the current active node
    def highlight_cur_node(self, i ,j):
        color = (255, 255, 255)# purple -(125, 0, 255)
        self.m.m_pattern(i, j , color, "open")

    # Functionality: this method iterates over 2d array and over each array checks prob and fills it - no algorithm maze generation
    def generate_maze_no_alg(self):
        inc = 0
        filled_cells = []
        filled_cells.append(self.calc_prob())
        for index_i in range( 1, self.m.col-1):
            for index_j in range(1,self.m.col-1):
                self.visit_Neighbor_generate_maze_no_alg(index_i, index_j, filled_cells, inc)
                inc += 1
        return self.maze_array

    def visit_Neighbor_generate_maze_no_alg(self, i, j, filled_cells, inc):
        num = random.randint(0, 1)
        if self.maze_array[i][j] == 0:
            if num == 1 and filled_cells[-1] > 0:   # Random decision using random.int - if condition is true then it would generate a blocked cell
                f_c = filled_cells[-1]   # f_c and Filled_cells are the number of cells that has to be generated as blocks on map
                f_c = f_c - 1
                filled_cells.pop()
                filled_cells.append(f_c)
                self.maze_array[i][j] = 8
            else:   # Generates open cells
                pos = [i , j]
                self.q.append(pos)
                self.maze_array[i][j] = 1

    # Adds the current active node in the visited list for the Fringe
    def current_node(self,i,j):
        self.q_visited.append([i,j])
        self.q_list_of_visited_nodes.append([i,j])

    def make_path_door(self,arr):
        for i in range( 1, self.m.col-1):
            for j in range(1,self.m.col-1):
                if arr[i][j] == 8:
                    inc = 0
                    inc = inc + self.create_path(i-1,j,arr)
                    inc = inc + self.create_path(i+1, j, arr)
                    inc = inc + self.create_path(i, j-1, arr)
                    inc = inc + self.create_path(i, j+1, arr)
                    if inc==2:
                        arr[i][j] = 1


        return arr

    # Functionality: facilitates make_path_door - Creates a door between closed paths
    def create_path(self,i,j,arr):
        if arr[i][j] != 8:
            return 1
        return 0

    #Functionality: To clear the start and goal state from barriers
    def clear_start(self, arr, start, end):
        i = self.m.row - 2
        j = self.m.col - 2
        arr[1][1] = 1
        arr[1][2] = 1
        arr[2][1] = 1
        arr[2][2] = 1
        arr[2][3] = 1
        arr[3][1] = 1
        arr[3][2] = 1
        arr[3][3] = 1
        arr[4][1] = 1
        arr[4][2] = 1
        arr[4][3] = 1

        arr[i][j] = 0
        arr[i-1][j] = 1
        arr[i-2][j] = 1
        arr[i-3][j] = 1
        arr[i][j-1] = 1
        arr[i][j - 2] = 1
        arr[i][j - 3] = 1
        arr[i-1][j - 1] = 1
        return arr
