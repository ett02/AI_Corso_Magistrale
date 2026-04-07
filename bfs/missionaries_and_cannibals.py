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

    def _is_valid(self, left_m, left_c):
        """ Check if a state is mathematically and logically valid. """
        right_m = self.N - left_m
        right_c = self.N - left_c
        
        # State boundaries validation
        if left_m < 0 or left_c < 0 or right_m < 0 or right_c < 0:
            return False
        
        # Cannibals outnumber missionaries on either bank when missionaries are present
        if (left_m > 0 and left_m < left_c) or (right_m > 0 and right_m < right_c):
            return False
            
        return True

    def actions(self, state):
        left_m, left_c, boat_side = state
        
        actions_list = []
        if boat_side == 1:
            max_m = min(left_m, self.B)
            max_c = min(left_c, self.B)
            for boat_m in range(0, max_m + 1):
                for boat_c in range(0, max_c + 1):
                    # Valid load constraint
                    if 1 <= boat_m + boat_c <= self.B:
                        # Original constraint: never more cannibals than missionaries on the boat
                        if boat_m > 0 and boat_m < boat_c:
                            continue
                            
                        # Predict next state and append if safe
                        if self._is_valid(left_m - boat_m, left_c - boat_c):
                            actions_list.append((boat_m, boat_c))
        else:
            right_m = self.N - left_m
            right_c = self.N - left_c
            max_m = min(right_m, self.B)
            max_c = min(right_c, self.B)
            for boat_m in range(0, max_m + 1):
                for boat_c in range(0, max_c + 1):
                    # Valid load constraint
                    if 1 <= boat_m + boat_c <= self.B:
                        # Original constraint: never more cannibals than missionaries on the boat
                        if boat_m > 0 and boat_m < boat_c:
                            continue
                            
                        # Predict next state and append if safe
                        if self._is_valid(left_m + boat_m, left_c + boat_c):
                            actions_list.append((boat_m, boat_c))
                            
        return actions_list
    
    def result(self, state, action):
        left_m, left_c, boat_side = state
        boat_m, boat_c = action
        if boat_side == 1:
            return (left_m - boat_m, left_c - boat_c, 0)
        else:
            return (left_m + boat_m, left_c + boat_c, 1)

    def is_goal(self, state):
        return state == self.goal

    def action_cost(self, s, a, s1):
        return 1

    def h(self, node):
        left_m, left_c, boat_side = node.state
        # A simple admissible heuristic: roughly estimate the minimum one-way trips needed.
        # It's an optimistic approximation.
        return (left_m + left_c) / self.B

def run_game(nn=3, bb=2):
    mc_problem = MissionariesAndCannibals(N=nn, B=bb)
    print(f"\nMissionaries and Cannibals problem (N={mc_problem.N}, B={mc_problem.B})")
    print("-" * 65)
    
    try:
        solution = astar_search(mc_problem)
    except NameError:
        # Fallback if astar_search is entirely missing from problem imports (just in case)
        print("ERROR: astar_search not found in imports.")
        return
        
    if solution is failure:
        print("No solution found!")
        return
        
    states = path_states(solution)
    actions = path_actions(solution)
    total_steps = len(actions)
    
    print(f"Solution found in {total_steps} steps:\n")
    
    for j in range(len(states)):
        m, c, b = states[j]
        
        # Rendering the banks via python string manipulation
        left_bank = "M " * m + "  " * (mc_problem.N - m) + "C " * c + "  " * (mc_problem.N - c)
        right_bank = "M " * (mc_problem.N - m) + "  " * m + "C " * (mc_problem.N - c) + "  " * c
        river = " ⛵🌊   " if b == 1 else "   🌊⛵ "
        
        # Displaying the state using fixed width formatting to maintain terminal alignment
        print(f"[{j:02d}]  {left_bank} {river} {right_bank}", end="")
        
        if j < len(states) - 1:
            mb, cb = actions[j]
            direction = "right" if b == 1 else "left"
            print(f"   --> {mb}M, {cb}C crossing {direction}", end="")
        print()
        
    print(f"\nTotal path depth (solution cost): {total_steps} steps.")
    print("-" * 65 + "\n")
    
def test():
    run_game(3, 2)
    run_game(4, 2)
    run_game(4, 3)
    run_game(5, 2)
    run_game(5, 3)

def main():
    print("""
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
    """)
    
    while True:
        try:
            val_n = input("Insert the number of missionaries and cannibals (N > 0): ").strip()
            nn = int(val_n)
            if nn <= 0:
                print("Error: N must be strictly positive (greater than 0). Try again.\n")
                continue
                
            val_b = input("Insert the boat capacity (B > 0): ").strip()
            bb = int(val_b)
            if bb <= 0:
                print("Error: B must be strictly positive (greater than 0). Try again.\n")
                continue
                
            break
        except ValueError:
            print("Invalid input! Please enter a valid integer number.\n")
            
    run_game(nn, bb)

if __name__ == "__main__":
    main()