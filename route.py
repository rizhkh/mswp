import numpy as np
import startprgm
import main
import alg
#from main import maze
from collections import deque
from ast import literal_eval
import random
import time

# This class is to move the agent from target to solution

class move:

    m = None    # empty object
    maze_array = []
    fire_cells = [1]
    last_fire_cells = []    # index of last fire cell to be on fire
    screen = None
    q = deque() # where list of active nodes are stored
    q_visited = []
    q_list_of_visited_nodes = [] #[[1,1]]

    start_i = 1    # starting index i for current node (parent node)
    start_j = 1    # starting index j for current node (parent node)

    target_i = 0
    target_j = 0

    f_visit = []  # fire cell
    f_list_of_visited_nodes = []
    cur_n_fire = []
    fire_pos = []
    fire_init = []
    incr = [0] # random counter for fire cell

    open_list = deque()
    closed_list = []
    # node_key_fval = [] # [ ['position','func(n)'] ]
    # book_list = {} # To book keep index and their func values
    restricted_cells = []
    a_visit = []    # Keeps track of visited node for the route that will be used
    net_cost = []
    est_cost = [] #dict()  # stores [index,cost]
    current_move = [ ]  # stores current_move

    rcmp_open_list = deque()
    rcmp_closed_list = []
    rcmp_restricted_cells = []      # MIGHT NOT USE THIS
    rcmp_a_visit = []
    rcmp_net_cost = []
    rcmp_est_cost = [] #dict()  # stores [index,cost]
    rcmp_current_move = [ ]

    non_repeat = []
    prev_steps = []
    restrct_cells = []
    number = [1]
    prev = []
    prev_fn = []

    val = []
    usc_pq_list = []
    usc_dist = dict()
    usc_processed = dict()
    usc_prev = dict()
    usc_pq = dict()
    usc_visited = []



    def __init__(self , scrn, arr, obj):
        self.m = obj    #Copy the ref address in an empty obj -> point towards the orignal address
        self.screen = scrn #obj.get_screen()
        self.maze_array = np.copy(arr)  # (obj.get_arr())
        self.target_i = obj.row - 2
        self.target_j = obj.col - 2

    def calc_heuristic(self,current_i,current_j,goal_i,goal_j,distance):
        dx = abs(current_i - goal_i)
        dy = abs(current_j - goal_j)
        h = distance  * (dx + dy)
        return (dx + dy)

    # Returns the cell value of the current explored neighbor cell from map
    def visit_neighbor_astar(self, i, j):
        return self.maze_array[i][j]

    # CHANGE THIS FUNCTION TO WHERE A LIST STORES INDEX POSITION and F(N)
    def expand_neighbor_astar(self, i, j, current_node, array, clsed_list, restrcted_cells, opn_list):  # , prev_gn):
        n_cost = 9000
        if ([i,j] in self.fire_cells) or ([i,j] in self.last_fire_cells):
            restrcted_cells.append([i, j])
            return -1

        if self.visit_neighbor_astar(i, j) != 8:
            if [i, j] not in clsed_list:
                if [i, j] not in restrcted_cells:
                    cn_i = current_node[0]
                    cn_j = current_node[1]
                    g_prev = array[cn_i][cn_j]  # self.get_gVal( [cn_i,cn_j] ) # g(n) of current cell currently stored
                    g = g_prev + array[i][j]
                    array[i][j] = g
                    # dist = self.visit_neighbor_astar(i, j)
                    h = self.calc_heuristic(i, j, self.target_i, self.target_j, g)
                    n_cost = g + h
                    if [i, j] not in opn_list:
                        opn_list.append([i, j])
        if self.visit_neighbor_astar(i, j) == 8:
            restrcted_cells.append([i, j])
        return n_cost

    # returns smallest f(n) of the nodes being checked and also calls backtracking function incase player is at a dead end
    def get_net_cost(self, list, current_node, rstrcted_cells, clsed_lists):
        pos_i = pos_j = 0
        cost = 9999
        inc_backtrack = 0
        for i in list:
            if i[0] < cost and i[0] != 9000:
                cost = i[0]
                pos_i = i[1]
                pos_j = i[2]
            if i[0] == 9000:
                inc_backtrack += 1

        if cost == -1:  #   COMMENT THIS IF YOU WANT TO JUST RUN STRATEGY ONE
            position = self.backtracking(current_node, rstrcted_cells, clsed_lists)  # self.backtracking( [i[1],i[2]] )
            # position = self.backtracking(current_node) #self.backtracking( [i[1],i[2]] )
            pos_i = position[0]
            pos_j = position[1]
            cost = 9000

        if inc_backtrack==4:
            position = self.backtracking(current_node, rstrcted_cells, clsed_lists)  # self.backtracking( [i[1],i[2]] )
            #position = self.backtracking(current_node) #self.backtracking( [i[1],i[2]] )
            pos_i = position[0]
            pos_j = position[1]
            cost = 9000

        index = [ pos_i, pos_j ]
        return [ cost, index ]

    #Functionality: Helps player backtrack incase of a deadend situation
    def backtracking(self, pos, rstrcted_cells, clsed_list):
        # self.m.player_movement(pos[0], pos[1], (0, 0, 255), "player")
        self.m.player_movement(pos[0], pos[1], (224, 224, 224), "player")
        self.m.player_movement(pos[0], pos[1], (255, 255, 255), "player")
        rstrcted_cells.append(pos)
        clsed_list.pop()
        if pos in self.a_visit:
            ind = self.a_visit.index(pos)
            self.a_visit.pop(ind)
        if clsed_list:
            index = clsed_list[-1]
        else:
            index = [0,0]
        return index

    # NOTE: WHEN YOU ARE ABOUT TO BACKTRACK - ADD THAT CURRENT NODE TO CLOSED NODES
    # TO BACKTRACK KEEP A TRACK OF PREV_NODE AND CHECK AT THE TIME OF BACKTRACKING IF ITS IN CLOSED_LIST OR OPEN_LIST AND CHANGE CURRENT NODE TO THAT

    #Functionality: Initializes the players possion on the board / maze
    def player_init(self):
        self.open_list.append([1, 1])
        self.closed_list.append([1,1])
        self.prev_fn.append(9000)
        current_node = [1, 1]
        self.current_move.append( current_node )
        move = self.player_move_process([1,1])
        return move

    #Functionality: calls a star algorithm
    def player_move_process(self,current_node):
        next_step_astar = self.a_star(current_node)
        return next_step_astar

###  A STAR ALGORITHM FOR MY OWN IMPLEMENTED SOLUTION
    def a_star(self, current_node):
        if self.open_list:
            status = False

            if (current_node in self.fire_cells) or (current_node in self.last_fire_cells):
                return 88

            if current_node == [0,0]:
                return True

            if current_node == [self.target_i,self.target_j]: #IF CURRENT NODE IS GOAL CELL
                return 88

            if current_node == True:
                return True

            index_i = current_node[0]
            index_j = current_node[1]

            # Checks neighbors and returns the f(n) of the each explored neighbor
            self.net_cost.append( [ self.expand_neighbor_astar( index_i + 1, index_j, current_node, self.maze_array, self.closed_list , self.restricted_cells, self.open_list), index_i + 1, index_j ] ) # down
            self.net_cost.append( [ self.expand_neighbor_astar( index_i, index_j - 1, current_node, self.maze_array, self.closed_list , self.restricted_cells, self.open_list) , index_i, index_j - 1 ] ) # right
            self.net_cost.append( [ self.expand_neighbor_astar( index_i - 1, index_j, current_node, self.maze_array, self.closed_list , self.restricted_cells, self.open_list) , index_i - 1, index_j ] ) # up
            self.net_cost.append( [ self.expand_neighbor_astar( index_i, index_j + 1, current_node, self.maze_array, self.closed_list , self.restricted_cells, self.open_list) , index_i, index_j + 1 ] ) # left

            # Compares and chooses the appropriate f(n) for the next cell - in this case, it chooses the smallest value while book keeping all visited cells, barriers etc
            result = self.get_net_cost(self.net_cost, current_node, self.restricted_cells, self.closed_list)  # results is [cost,index]

            # Result value of 9000 indicates that no direction is open to explore (either blocked or already explored) - this will then remove current node and add it list of visited nodes
            # ( if it is a dead end then it will select a node from a list of visited nodes that has neighbors in list of open nodes list and explore that - it systematically tracks back to that node
            # e.g instead of jumping back from node 9 to 6 instanty - it checks node 8,7 before it does making sure these nodes have no available neighbors in open cells)
            # Note: No node is removed from closed list at all. Once that node is visited it is visted that cannot be reversed according to the algorithm
            if result[0] == 9000:
                if not self.closed_list:
                    return False
                current_node = self.closed_list[-1]
                if current_node not in self.open_list:
                    self.open_list.append(current_node)
                status = True

            self.net_cost.clear()   # clear the last list so new nodes and their fn is saved for newer iteration

            # adds the current node in the fringe when they are explored
            if status == False:
                np = result[1]
                if self.open_list:
                    self.open_list.remove([current_node[0], current_node[1]])   # removes node from open list when it is being added to closed list
                current_node = np   # To highligh nodes on the canvas board

                self.m.player_movement(np[0], np[1], (0, 0, 255), "player")
                self.m.player_movement(np[0], np[1], (255, 255, 102), "player")

                self.a_visit.append( [np[0], np[1]] )   # THIS LIST HAS THE ROUTE YOUR PLAYER HAS TAKEN
                self.closed_list.append(np)
                self.est_cost.append([np, result[0]])  # [index,cost]
                if self.current_move:
                    self.current_move.clear()
                self.current_move.append( np )
        return current_node # returns the current node index position


    # Algorithms below are the same A star algorithms just with very small changes to get the results according to mentioned strategy description
    # These algorithms follow the same functionality as above

    ###  A STAR ALGORITHM FOR STRATEGY ONE - different function because this function returns complete list or bool
    def a_star_SOne(self, current_node):
        while self.open_list:
            status = False

            if (current_node in self.fire_cells) or (current_node in self.last_fire_cells):
                return 88

            if current_node == [0,0]:
                return True

            if current_node == [self.target_i,self.target_j]: #IF CURRENT NODE IS GOAL CELL
                return self.a_visit

            # if current_node == True:
            #     return True

            index_i = current_node[0]
            index_j = current_node[1]

            self.net_cost.append( [ self.expand_neighbor_astar( index_i + 1, index_j, current_node, self.maze_array , self.closed_list , self.restricted_cells, self.open_list), index_i + 1, index_j ] ) # down
            self.net_cost.append( [ self.expand_neighbor_astar( index_i, index_j - 1, current_node, self.maze_array, self.closed_list , self.restricted_cells, self.open_list) , index_i, index_j - 1 ] ) # right
            self.net_cost.append( [ self.expand_neighbor_astar( index_i - 1, index_j, current_node, self.maze_array, self.closed_list , self.restricted_cells, self.open_list) , index_i - 1, index_j ] ) # up
            self.net_cost.append( [ self.expand_neighbor_astar( index_i, index_j + 1, current_node, self.maze_array, self.closed_list , self.restricted_cells, self.open_list) , index_i, index_j + 1 ] ) # left
            result = self.get_net_cost(self.net_cost, current_node, self.restricted_cells, self.closed_list)  # results is [cost,index]

            if result[0] == 9000:
                if not self.closed_list:
                    return False
                current_node = self.closed_list[-1]
                if current_node not in self.open_list:
                    self.open_list.append(current_node)

                status = True
            self.net_cost.clear()   # we clear the last list so new nodes and their fn is saved
            if status == False:
                np = result[1]
                if self.open_list:
                    self.open_list.remove([current_node[0], current_node[1]])
                current_node = np

                self.a_visit.append( [np[0], np[1]] )   # THIS LIST HAS THE ROUTE YOUR PLAYER HAS TAKEN
                self.closed_list.append(np)
                self.est_cost.append([np, result[0]])  # [index,cost]
                if self.current_move:
                    self.current_move.clear()
                self.current_move.append( np )
                # print(self.maze_array)
        return False    # For strategy one - it returns false if there is no path to the target. This function returns the complete route when it
        # reaches the target - then the object calling it runs the path in the maze and as per strategy one if it is in the way of fire cell it will die


    ###  A STAR ALGORITHM FOR STRATEGY TWP - Same as above with a little small tweaks according to run Strategy 2 from description
    def rcmp_clear_restricted(self):
        self.rcmp_restricted_cells.clear()

    def recompute_a_star_Two(self, current_node, mode):
        if mode == 'returnList':
            self.rcmp_open_list.clear()
            self.rcmp_closed_list.clear()
            self.rcmp_a_visit.clear()
            self.rcmp_net_cost.clear()
            self.rcmp_est_cost.clear()

        self.rcmp_open_list.append(current_node)
        self.rcmp_closed_list.append(current_node)
        self.rcmp_current_move.append( current_node )
        array = self.maze_array.copy()

        check = False

        while self.rcmp_open_list:
            status = False
            if (current_node in self.fire_cells) or (current_node in self.last_fire_cells):
                return 88

            if current_node == [0,0]:
                return 66

            if current_node == [self.target_i,self.target_j] and mode == 'returnList': #IF CURRENT NODE IS GOAL CELL
                al = self.rcmp_a_visit[:]

                self.rcmp_open_list.clear()
                self.rcmp_closed_list.clear()
                self.rcmp_a_visit.clear()
                self.rcmp_net_cost.clear()
                self.rcmp_est_cost.clear()
                return al

            if current_node == [self.target_i,self.target_j] and mode == 'returnBool': #IF CURRENT NODE IS GOAL CELL
                self.rcmp_open_list.clear()
                self.rcmp_closed_list.clear()
                self.rcmp_a_visit.clear()
                self.rcmp_net_cost.clear()
                self.rcmp_est_cost.clear()
                return True

            index_i = current_node[0]
            index_j = current_node[1]
            self.rcmp_net_cost.append(
                [self.expand_neighbor_astar(index_i + 1, index_j, current_node, array, self.rcmp_closed_list , self.rcmp_restricted_cells, self.rcmp_open_list), index_i + 1, index_j])  # down
            self.rcmp_net_cost.append(
                [self.expand_neighbor_astar(index_i, index_j - 1, current_node, array, self.rcmp_closed_list , self.rcmp_restricted_cells, self.rcmp_open_list), index_i, index_j - 1])  # right
            self.rcmp_net_cost.append(
                [self.expand_neighbor_astar(index_i - 1, index_j, current_node, array, self.rcmp_closed_list , self.rcmp_restricted_cells, self.rcmp_open_list), index_i - 1, index_j])  # up
            self.rcmp_net_cost.append(
                [self.expand_neighbor_astar(index_i, index_j + 1, current_node, array, self.rcmp_closed_list , self.rcmp_restricted_cells, self.rcmp_open_list), index_i, index_j + 1])  # left

            result = self.get_net_cost(self.rcmp_net_cost, current_node, self.rcmp_restricted_cells, self.rcmp_closed_list)  # results is [cost,index]

            if result[0] == 9000:
                if not self.rcmp_closed_list:
                    return False
                current_node = self.rcmp_closed_list[-1]
                if current_node not in self.rcmp_open_list:
                    self.rcmp_open_list.append(current_node)
                status = True
            self.rcmp_net_cost.clear()  # we clear the last list so new nodes and their fn is saved
            if status == False:
                np = result[1]
                self.rcmp_open_list.remove([current_node[0], current_node[1]])
                current_node = np
                self.rcmp_a_visit.append([np[0], np[1]])  # THIS LIST HAS THE ROUTE YOUR PLAYER HAS TAKEN
                self.rcmp_closed_list.append(np)
                self.rcmp_est_cost.append([np, result[0]])
                if self.rcmp_current_move:
                    self.rcmp_current_move.clear()
                self.rcmp_current_move.append(np)
        sList = self.rcmp_a_visit.copy()

        self.rcmp_open_list.clear()
        self.rcmp_closed_list.clear()
        self.rcmp_a_visit.clear()
        self.rcmp_net_cost.clear()
        self.rcmp_est_cost.clear()
        return False


    # CODE BELOW INITIALIZES FIRE POSITION AND MOVEMENT
    # IT USES BFS TO MOVE
    ### FIRE GENERATION

    # Functionalty: returns the prob rate (follows the formula 1-(1-q)^k) to firemovement function and if the prob is more than 0.5 then cell will be on fire
    def fire_prob(self, i,j,arr, flammability):
        n = 0   # number of neighbors
        if  arr[i-1][j] == 1 or arr[i-1][j] == 0:   # check neighbor on top
            n += 1
        if  arr[i+1][j] == 1 or arr[i+1][j] == 0:   # check neighbor on bottom
            n += 1
        if  arr[i][j-1] == 1 or arr[i][j-1] == 0:   # check neighbor on left
            n += 1
        if  arr[i][j+1] == 1 or arr[i][j+1] == 0:   # check neighbor on right
            n += 1
        q = flammability#random.uniform(0, 1)
        q_pow = pow((1 - q), n)
        p = 1 - q_pow
        return p

    def fire_start_pos(self , arr):
        i = j = self.m.col-1
        while arr[i][j] == 8:
            i = random.randint(3, self.m.col - 4)  # This would generate the random position of the fire
            j = random.randint(2, self.m.col - 4)
        return [i,j]

    def clear_path_fire(self,i,j):
        if i!=0 and i!=19:
            if j!=0 and j!=19:
                self.maze_array[i + 1][j] = 1
                self.maze_array[i - 1][j] = 1
                self.maze_array[i][j + 1 ] = 1
                self.maze_array[i][j - 1] = 1
        return [i,j]

    def get_fire_init_pos(self):
        return self.fire_init[0]

    def init_fire(self):
        pos = self.fire_start_pos(self.m.get_arr())
        self.fire_init.append(pos)
        self.clear_path_fire(pos[0],pos[1])
        self.fire_pos.append( pos )
        status = False  # This boolean variable will be utilized to stop traversing when target is reached
        self.visit_Neighbor_bfs(pos[0], pos[1], status)   #<- function that adds parent node to list of visited cells to be tracked

    def clear_fire_list(self):
        self.cur_n_fire.clear()
        self.fire_cells.clear()
        self.f_visit.clear()
        self.f_list_of_visited_nodes.clear()
        self.fire_pos.clear()

    def fire_movement_process(self, status, number, flammability):
        status = self.player_move_BFS(status, number, flammability)   # Fire spreads using BFS algorithm
        return status

    # ADD DETAILS
    # Follows BFS algorithm where the neighbors are expanded, current node is added to list of visited nodes and the next node selected is from the left mose side in queue
    def player_move_BFS(self, status, number, flammability):
        if self.q:
            if number == 0 :
                cur_n = self.q.popleft()    # Takes the element present at start in queue(where it stores neighbor) as active node and removes to tackle duplicate nodes
                self.cur_n_fire.append(cur_n)
                start_point = cur_n[0]  # get index i for current node
                end_point = cur_n[1]  # get index j for current node
                #self.highlight_fire_node(start_point, end_point, (255, 0, 0))
                self.fire_cells.append( self.fire_prob(start_point - 1, end_point, self.m.get_arr(), flammability ) )  # add the prob. value of cell being on fire in a list for next time step
                status = self.visit_Neighbor_bfs(start_point - 1, end_point, status)  # move up

            if number == 1:
                cur_n = self.cur_n_fire[-1]
                start_point = cur_n[0]  # get index i for current node
                end_point = cur_n[1]  # get index j for current node
                #self.highlight_fire_node(start_point, end_point, (255, 0, 0))
                self.fire_cells.append( self.fire_prob(start_point - 1, end_point, self.m.get_arr(), flammability ) )
                status = self.visit_Neighbor_bfs(start_point + 1, end_point, status)  # move down

            if number == 2:
                cur_n = self.cur_n_fire[-1]
                start_point = cur_n[0]  # get index i for current node
                end_point = cur_n[1]  # get index j for current node
                #self.highlight_fire_node(start_point, end_point, (255, 0, 0))
                self.fire_cells.append( self.fire_prob(start_point - 1, end_point, self.m.get_arr(), flammability ) )
                status = self.visit_Neighbor_bfs(start_point, end_point - 1, status)  # move left

            if number == 3:
                cur_n = self.cur_n_fire[-1]
                start_point = cur_n[0]  # get index i for current node
                end_point = cur_n[1]  # get index j for current node
                #self.highlight_fire_node(start_point, end_point, (255, 0, 0))
                self.fire_cells.append( self.fire_prob(start_point - 1, end_point, self.m.get_arr(), flammability ) )
                status = self.visit_Neighbor_bfs(start_point, end_point + 1, status)  # move right
                self.cur_n_fire.pop()

        # If current explored open cell has flammability rate of 0 then cell is added to queue again so it can be estimated again later
        else:
            if self.last_fire_cells:    # last position of cell on fire - func. above will check its neighbor(determine that if they are open) and start from there just incase queue gets empty
                if self.last_fire_cells:    # chooses the newest added open cell from the list as current node to be set on fire - In this case this should have at most 1 cell
                    cur_n = self.last_fire_cells[-1]
                else:
                    cur_n = self.fire_start_pos(self.m.get_arr())
                self.q.append(cur_n)
            else:   #just incase queue gets emptied. Last open cell gets added to queue of nodes to be checked - This should not be reached
                cur_n = self.cur_n_fire[-1]
                self.q.append( cur_n )
                self.cur_n_fire.pop()
        return status

    def check_surround(self, i ,j):
        if self.maze_array[ i + 1 ][j] != 8:
            if self.maze_array[i + 1][j] == 4 or self.maze_array[i + 1][j] == 1111:
                return True

        if self.maze_array[ i - 1 ][j] != 8:
            if self.maze_array[i - 1][j] == 4 or self.maze_array[i - 1][j] == 1111:
                return True

        if self.maze_array[ i ][j+1] != 8:
            if self.maze_array[i][j+1] == 4 or self.maze_array[i][j+1] == 1111:
                return True

        if self.maze_array[ i ][j-1] != 8:
            if self.maze_array[i][j-1] == 4 or self.maze_array[i][j-1] == 1111:
                return True

        return False

    def highlight_fire_node(self, i ,j, color):
        self.m.player_movement(i, j , color, 'fire')

    def visit_Neighbor_bfs(self,i, j , status):
        prob = self.fire_cells[-1]  # retrieves the prob to generate a fire cell

        if status == True:  # if Target state is reached in other neighbors - This would return True as well instead of traversing (this should not be reached)
            return True

        if [i , j] == self.current_move[-1]: #self.current_move:   # Returns true to stop fire traverse if it reaches player
            color = (0, 0, 0)#(178, 103, 100)
            self.highlight_fire_node(i, j, (255, 0, 0))
            return True

        if prob >=0.5:  # if probability is more than 0.5 generate fire cell
            if self.maze_array[i][j] != 8:
                if [i,j] not in self.f_list_of_visited_nodes:   # Checks if current cell has not been visited already
                    sum = self.incr[0]
                    sum += 1
                    self.incr.pop()
                    self.incr.append(sum)
                    check_s = self.incr[0]

                    check = self.check_surround(i,j)    # this check_s and this funct makes sure each fire cell has a neighbor on fire after fire is started
                    if check==True and check_s>1:
                        pos = [i,j]
                        self.q.append(pos)  # adds node in the list of nodes that still has to be set as current nodes - in this func its the neighbor being explored
                        self.current_node(self.f_visit, self.f_list_of_visited_nodes,i, j)
                        color = (255, 0, 0)
                        self.m.player_movement(i, j, color,'fire')
                        self.last_fire_cells.append( [i,j] )
                    if check<2:
                        pos = [i,j]
                        self.q.append(pos)  # adds node in the list of nodes that still has to be set as current nodes - in this func its the neighbor being explored
                        self.current_node(self.f_visit, self.f_list_of_visited_nodes,i, j)
                        color = (255, 0, 0)
                        self.m.player_movement(i, j, color,'fire')
                        self.last_fire_cells.append( [i,j] )
        else:
            if self.maze_array[i][j] == 0 or self.maze_array[i][j] == 1:
                if [i,j] not in self.q:
                    self.q.append([i,j])    # the empty cell where there is no fire is again added to list of nodes that has to be visited in the future
        self.fire_cells.pop(-1)
        return status

    def highlight_cur_node(self, i ,j, color):
        self.m.player_movement(i, j , color, "open")

    # This function helps add nodes to list/queue as long as the correct list are passed - This same function is used in fire movement, player moment with correct lists being passed as arguments
    def current_node(self,q_v,q_l_v,i,j):
        q_v.append([i,j])   # queues visited # not really used - might use it in future - self.q_visited.append([i,j])
        q_l_v.append([i,j]) # queue of all list of visited nodes - self.q_list_of_visited_nodes.append([i,j])


    # UNUSED ALGORITHMS THAT WERE IMPLEMENTED BUT NOT USED

    def player_move_dfs(self):
        # Algorithm: Add the starting position as parent node
        # Go to neighbor (using function call visit_neighbor_dfs)
        # that function calls func that checks if cell is visited or not

        # DFS: when this function starts traversing, it keeps travelling in one direction until no neighbor can be visited
        # or it is already visited, in that case it backtracks to the previous node (removing current node from top of stack
        # and setting the active node to it - does the same if no neighbor is able to be visited)

        color = (0, 0, 204)   # blue color for starting point
        self.m.m_pattern(self.start_i , self.start_j, (0, 0, 204), "start")
        target = [self.target_i, self.target_j]
        color = (204, 0, 102)
        self.m.m_pattern(self.target_i, self.target_j, color, "open")

        self.q.append( [self.start_i, self.start_j] )   # adds parent node to list of nodes
        self.current_node(self.q_visited, self.q_list_of_visited_nodes,self.start_i, self.start_j)   # adds parent node to list of visited nodes and as active node

        pos = self.q[-1]  # peek the top most element on stack ( in this sit. get index of parent node to start traversing)
        i = pos[0]
        j = pos[1]
        p = deque()
        p = self.visit_neighbor_dfs( i , j, target,False)
        print("end : " , self.q)

    def visit_neighbor_dfs(self, i , j, target, status):
        if status is not True:  # If target state is fou,d traverse_dfs would return true to stop traversing any further
            status = self.traverse_dfs(i - 1, j, target, status)  # up

        if status is not True:
            status = self.traverse_dfs(i + 1, j, target, status) # down

        if status is not True:
            status = self.traverse_dfs(i , j + 1, target, status)  # right

        if status is not True:
            status = self.traverse_dfs(i, j - 1, target, status) # left

        if  status == True: #To step further traversing when target state is reached
            return True

        if self.q:
            self.q.pop()    # the element will only pop after checking the moves to its neighbor are completed or not
            color = (255,255,255) #   (55,0,255) # blue color when backtracked
            self.m.player_movement(i, j, color, "back track")
        return False

    # Functionality:  To check cell is visited or not
    def traverse_dfs(self, i, j , target, status):
        if status == True:  # if Target state is reached in other neighbors - This would return True as well instead of traversing (this should not be reached)
            return True

        if [i , j] == target:   # Returns True and changes color of target when it is reached
            color = (178, 103, 100)
            self.m.player_movement(i, j, color, "open")
            return True

        if self.maze_array[i][j] == 0 or self.maze_array[i][j] == 1:
            if [i,j] not in self.q_list_of_visited_nodes:
                pos = [i,j]
                self.q.append(pos)
                self.current_node(self.q_visited, self.q_list_of_visited_nodes, i, j)
                color = (178, 0, 178)
                self.m.player_movement(i, j, color, "open")
                self.m.player_movement(i, j, (255, 255, 9), "open")
                status = self.visit_neighbor_dfs(i, j, target, status)
        return status

    def uniform_cost_search(self, current_node):
        ## current node is in this form [ [1,1] ]
        for i in range(1,19):
            for j in range(1,19):
                if self.maze_array[i][j]==8:
                    self.usc_dist[repr([i, j])] = 5555  # 'infinity'     # processed stores in format : [ [1,1] ]
                    self.usc_processed[repr([i, j])] = False  # processed stores in format : [ [i,j] ]
                    self.usc_prev[repr([i, j])] = None
                else:
                    self.usc_dist[repr([i, j])] = 1000  # 'infinity'     # processed stores in format : [ [1,1] ]
                    self.usc_processed[repr([i, j])] = False  # processed stores in format : [ [i,j] ]
                    self.usc_prev[repr([i, j])] = None

        self.usc_dist[ repr(current_node) ] = 0
        self.usc_pq[ repr(current_node) ] = self.usc_dist[ repr(current_node) ]
        self.usc_pq_list.append( [current_node, self.usc_dist[ repr(current_node) ]] )     # this is for while loop
        self.usc_prev[ repr(current_node) ] = current_node

        self.usc_dist[ repr([1,2]) ] = 2
        self.usc_pq[ repr([1,2]) ] = self.usc_dist[ repr([1,2]) ]
        self.usc_pq_list.append( [ [1,2], self.usc_dist[ repr([1,2]) ]] )     # this is for while loop
        self.usc_prev[ repr([1,2]) ] = None
        self.usc_processed[repr([1, 2])] = False

        self.usc_dist[ repr([2,1]) ] = 2
        self.usc_pq[ repr([2,1]) ] = self.usc_dist[ repr([2,1]) ]
        self.usc_pq_list.append( [ [2,1], self.usc_dist[ repr([2,1]) ]] )     # this is for while loop
        self.usc_prev[ repr([2,1]) ] = None
        self.usc_processed[repr([2, 1])] = False

        pprev = []
        while self.usc_pq:
            index = min(self.usc_pq, key=self.usc_pq.get)
            index2 = literal_eval(index)
            if index2 == [self.target_i,self.target_j]:
                break
            self.m.player_movement(index2[0], index2[1], (0, 0, 255), "player")
            self.m.player_movement(index2[0], index2[1], (255, 255, 102), "player")
            #current_node = index
            val = self.usc_pq.pop( index )
            node = [index,val]
            self.usc_visited.append( literal_eval(node[0]) )
            if node[0] in self.usc_processed:
                if self.usc_processed.get( node[0] ) == False:
                    cn = literal_eval(node[0])  # converts string back to list
                    cn_i = cn[0]    # currentnode_index_i in while loop
                    cn_j = cn[1]
                    child = [
                        [cn_i - 1,cn_j] ,
                        [cn_i + 1,cn_j] ,
                        [cn_i , cn_j-1] ,
                        [cn_i , cn_j+1] ,
                    ]
                    for i in child:
                        if self.maze_array[i[0]][i[1]] != 8:
                            if i not in self.usc_visited:
                                d = self.usc_dist[repr([cn_i,cn_j])] + self.maze_array[i[0]][i[1]]
                                uvw = self.usc_dist[repr(i)]
                                if d < uvw:
                                    self.usc_dist[repr(i)] = d
                                    self.usc_pq[repr(i)] = d
                                    self.usc_prev[repr(i)] = [cn_i, cn_j]
                                    pprev.append([[i], [[cn_i, cn_j]]])
                                    #current_node = i
                self.usc_processed[ repr([cn_i, cn_j]) ] = True
        return self.usc_prev
