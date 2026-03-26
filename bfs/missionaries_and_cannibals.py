from problem import *
from bfs_algorithms import *

class MissionariesAndCannibals(Problem):
    """
    The Missionaries and Cannibals problem is a classic river crossing puzzle.
    There are N missionaries and N cannibals on the left bank of a river.
    There is a boat that can carry at most B people.
    The boat can only be rowed by a missionary or a cannibal.
    There must never be more cannibals than missionaries on either bank.
    
    N = number of missionaries and cannibals
    B = boat capacity
    The state is a tuple (m, c, b) where:
        m = number of missionaries on the left bank
        c = number of cannibals on the left bank
        b = boat position (1 if on the left bank, 0 if on the right bank)
    Initial state: (N, N, 1)
    Goal state: (0, 0, 0)
    """
    def __init__(self, N=3, B=2):
        self.__dict__.update(initial=(N, N, 1), goal=(0, 0, 0), N=N, B=B)

    def actions(self, state):
        left_m, left_c, boat_side = state # left_m = number of missionaries on the left bank, left_c = number of cannibals on the left bank
        right_m = self.N - left_m # right_m = number of missionaries on the right bank
        right_c = self.N - left_c # right_c = number of cannibals on the right bank
        if boat_side == 1: # boat is on the left bank
            return [(boat_m, boat_c) # boat_m = number of missionaries in the boat, boat_c = number of cannibals in the boat
                    for boat_m in range(0, left_m + 1) 
                    for boat_c in range(0, left_c + 1) 
                    if 1 <= boat_m + boat_c <= self.B # the boat can carry at most B people and it cannot be empty
                    and (boat_m >= boat_c or boat_m == 0) # there must never be more cannibals than missionaries on the boat
                    and (left_m - boat_m >= left_c - boat_c or left_m - boat_m == 0) # there must never be more cannibals than missionaries on the left bank
                    and (right_m + boat_m >= right_c + boat_c or right_m + boat_m == 0)] # there must never be more cannibals than missionaries on the right bank
        else: # boat is on the right bank
            return [(boat_m, boat_c) # boat_m = number of missionaries in the boat, boat_c = number of cannibals in the boat
                    for boat_m in range(0, right_m + 1) 
                    for boat_c in range(0, right_c + 1) 
                    if 1 <= boat_m + boat_c <= self.B # the boat can carry at most B people and it cannot be empty
                    and (boat_m >= boat_c or boat_m == 0) # there must never be more cannibals than missionaries on the boat
                    and (left_m + boat_m >= left_c + boat_c or left_m + boat_m == 0) # there must never be more cannibals than missionaries on the left bank
                    and (right_m - boat_m >= right_c - boat_c or right_m - boat_m == 0)] # there must never be more cannibals than missionaries on the right bank
    
    def result(self, state, action): # state = (left_m, left_c, boat_side), action = (boat_m, boat_c)
        left_m, left_c, boat_side = state
        boat_m, boat_c = action
        if boat_side == 1: # boat is on the left bank
            return (left_m - boat_m, left_c - boat_c, 0) # boat moves to the right bank
        else: # boat is on the right bank
            return (left_m + boat_m, left_c + boat_c, 1) # boat moves to the left bank

    def is_goal(self, state):        return state == self.goal
    def action_cost(self, s, a, s1): return 1
    def h(self, node):               return 0

def run_game(nn=3, bb=2):
    mc_problem = MissionariesAndCannibals(N=nn, B=bb)
    print(f"Missionaries and Cannibals problem (N={mc_problem.N}, B={mc_problem.B})")
    solution = astar_search(mc_problem)
    if solution is failure:
        print("No solution found")
        return
    print("Solution:")
    for (m, c, b) in path_states(solution):
        for i in range(m):
            print("M ", end="")
        for i in range(mc_problem.N - m):
            print("  ", end="")
        for i in range(c):
            print("C ", end="")
        for i in range(mc_problem.N - c):
            print("  ", end="")
        print("\t⛵🌊  \t" if b == 1 else "\t  🌊⛵\t", end="")
        for i in range(mc_problem.N - m):
            print("M ", end="")
        for i in range(m):
                print("  ", end="")
        for i in range(mc_problem.N - c):
            print("C ", end="")
        for i in range(c):
            print("  ", end="")
        print()

run_game(3, 2)
print("\n\n")
run_game(4, 2)
print("\n\n")
run_game(5, 3)