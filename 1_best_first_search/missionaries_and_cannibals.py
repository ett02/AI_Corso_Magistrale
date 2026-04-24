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

    def _is_valid(self, missionaries_on_the_left, cannibals_on_the_left):
        """ Check if a state is mathematically and logically valid. """
        missionaries_on_the_right = self.N - missionaries_on_the_left
        cannibals_on_the_right = self.N - cannibals_on_the_left
        
        # Negatives
        if missionaries_on_the_left < 0 or cannibals_on_the_left < 0 or missionaries_on_the_right < 0 or cannibals_on_the_right < 0:
            return False
        
        # Cannibals outnumber missionaries on either bank when missionaries are present
        if (missionaries_on_the_left > 0 and missionaries_on_the_left < cannibals_on_the_left) or (missionaries_on_the_right > 0 and missionaries_on_the_right < cannibals_on_the_right):
            return False
            
        return True

    def actions(self, state):
        missionaries_on_the_left, cannibals_on_the_left, boat_side = state
        actions_list = []

        # missionaries and cannibals on the starting bank (where the boat is located)
        missionaries_on_the_bank = missionaries_on_the_left if boat_side == 1 else self.N - missionaries_on_the_left
        cannibals_on_the_bank = cannibals_on_the_left if boat_side == 1 else self.N - cannibals_on_the_left
        
        # max number of missionaries and cannibals that can be on the boat (to avoid cycles for invalid states)
        max_m = min(missionaries_on_the_bank, self.B)
        max_c = min(cannibals_on_the_bank, self.B)

        for missionaries_on_the_boat in range(0, max_m + 1):
            for cannibals_on_the_boat in range(0, max_c + 1):
                # Valid load constraint
                if 1 <= missionaries_on_the_boat + cannibals_on_the_boat <= self.B:
                    # Original constraint: never more cannibals than missionaries on the boat
                    if missionaries_on_the_boat > 0 and missionaries_on_the_boat < cannibals_on_the_boat:
                        continue
                    # Predict next state and append if safe
                    direction = -1 if boat_side == 1 else 1
                    if self._is_valid(missionaries_on_the_left + direction * missionaries_on_the_boat, cannibals_on_the_left + direction * cannibals_on_the_boat):
                        actions_list.append((missionaries_on_the_boat, cannibals_on_the_boat))                   
        return actions_list
    
    def result(self, state, action):
        missionaries_on_the_left, cannibals_on_the_left, boat_side = state
        missionaries_on_the_boat, cannibals_on_the_boat = action

        direction = -1 if boat_side == 1 else 1
        new_missionaries_on_the_left = missionaries_on_the_left + direction * missionaries_on_the_boat
        new_cannibals_on_the_left = cannibals_on_the_left + direction * cannibals_on_the_boat
        new_boat_side = 1 - boat_side
        return (new_missionaries_on_the_left, new_cannibals_on_the_left, new_boat_side)

    def h(self, node):
        missionaries_on_the_left, cannibals_on_the_left, boat_side = node.state
        # A simple admissible heuristic: roughly estimate the minimum one-way trips needed.
        # It's an optimistic approximation.
        return (missionaries_on_the_left + cannibals_on_the_left) / self.B

def run_game(nn=3, bb=2, algorithm=astar_search):
    mc_problem = MissionariesAndCannibals(N=nn, B=bb)
    print(f"\nMissionaries and Cannibals problem (N={mc_problem.N}, B={mc_problem.B})")
    print("-" * 65)
    
    try:
        solution = algorithm(mc_problem)
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
        
        # Rendering the banks
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
            
    print("\n" + "=" * 65)
    print("ASTAR SEARCH")
    print("=" * 65)
    run_game(nn, bb, astar_search)
    
    print("\n" + "=" * 65)
    print("GREEDY BFS")
    print("=" * 65)
    run_game(nn, bb, greedy_bfs)
    
    print("\n" + "=" * 65)
    print("UNIFORM COST SEARCH")
    print("=" * 65)
    run_game(nn, bb, uniform_cost_search)

    print("\n" + "=" * 65)
    print("BREADTH FIRST SEARCH")
    print("=" * 65)
    run_game(nn, bb, breadth_first_bfs)
    
    print("\n" + "=" * 65)
    print("DEPTH FIRST SEARCH")
    print("=" * 65)
    run_game(nn, bb, depth_first_bfs)

if __name__ == "__main__":
    main()