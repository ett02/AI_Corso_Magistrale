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
    def __init__(self, initial=(N, N, 1), goal=(0, 0, 0), N=3, B=2):
        self.__dict__.update(initial=initial, goal=goal, N=N, B=B)

    def actions(self, state):
        m, c, b = state # m = number of missionaries on the left bank, c = number of cannibals on the left bank, b = boat position (1 if on the left bank, 0 if on the right bank)
        if b == 1: # boat is on the left bank
            return [(mb, cb) # mb = number of missionaries in the boat, cb = number of cannibals in the boat
                    for mb in range(0, m + 1) 
                    for cb in range(0, c + 1) 
                    if 1 <= mb + cb <= self.B # the boat can carry at most B people and it cannot be empty
                    and (mb >= cb or mb == 0) # there must never be more cannibals than missionaries on the boat
                    and (m - mb >= c - cb or m - mb == 0) # there must never be more cannibals than missionaries on the left bank
                    and (self.N - m + mb >= self.N - c + cb or self.N - m + mb == 0)] # there must never be more cannibals than missionaries on the right bank
        else: # boat is on the right bank
            return [(mb, cb) # mb = number of missionaries in the boat, cb = number of cannibals in the boat
                    for mb in range(0, self.N - m + 1) 
                    for cb in range(0, self.N - c + 1) 
                    if 1 <= mb + cb <= self.B # the boat can carry at most B people and it cannot be empty
                    and (mb >= cb or mb == 0) # there must never be more cannibals than missionaries on the boat
                    and (m + mb >= c + cb or m + mb == 0) # there must never be more cannibals than missionaries on the left bank
                    and (self.N - m - mb >= self.N - c - cb or self.N - m - mb == 0)] # there must never be more cannibals than missionaries on the right bank
    
    def result(self, state, action): # state = (m, c, b), action = (mb, cb)
        m, c, b = state
        mb, cb = action
        if b == 1: # boat is on the left bank
            return (m - mb, c - cb, 0) # boat moves to the right bank
        else: # boat is on the right bank
            return (m + mb, c + cb, 1) # boat moves to the left bank
            
    def is_goal(self, state):        return state == self.goal
    def action_cost(self, s, a, s1): return 1
    def h(self, node):               return 0