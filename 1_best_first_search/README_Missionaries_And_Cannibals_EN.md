# Missionaries and Cannibals - University Project

Author: Giuseppe Pasquale Caligiure (Mat. 280867)

Available on GitHub: https://github.com/caligiure/AI_Corso_Magistrale/tree/main/bfs

## Overview
This project is an implementation of the classic Missionaries and Cannibals river crossing puzzle using Artificial Intelligence search algorithms. This program, **realized using the framework proposed by the professor**, models the problem space, formulates valid states and transitions, and finds optimal or sub-optimal paths to the solution using different search strategies.

The objective of the puzzle is to move `N` missionaries and `N` cannibals from the left bank of a river to the right bank using a boat that can hold at most `B` people. The core logical constraint is that at any time, on either bank, the number of cannibals cannot outnumber the number of missionaries (if there are any missionaries present), otherwise the missionaries will be eaten.

## How the Program Works
1. **Problem Formulation**: The game state is represented as a tuple `(m, c, b)`, where:
   - `m`: Number of missionaries on the left bank.
   - `c`: Number of cannibals on the left bank.
   - `b`: The position of the boat (`1` for the left bank, `0` for the right bank).
   
2. **Interactive Execution**: Upon startup, the program prompts the user to input custom values:
   - `N`: The total number of missionaries and cannibals.
   - `B`: The maximum passenger capacity of the boat.
   
3. **Algorithms Evaluated**: To demonstrate the AI problem-solving approach, the program automatically runs the puzzle through multiple search algorithms and prints the steps and solution for each:
   - **A* Search** (using an optimistic heuristic calculating the roughly estimated one-way trips)
   - **Greedy Best-First Search**
   - **Uniform Cost Search**
   - **Breadth-First Search (BFS)**
   - **Depth-First Search (DFS)**
   
4. **Visualisation**: The terminal renders an ASCII-based step-by-step visual display of the banks and the boat crossing the river (`🌊⛵`) alongside the action (e.g., `2M, 0C crossing right`) for each algorithm's found solution.

## How to Run the Program

1. Open your terminal.
2. Navigate to the project directory containing the `missionaries_and_cannibals.py` script.
3. Run the script using Python by entering the following command:

```bash
python missionaries_and_cannibals.py
```

4. Follow the on-screen prompts to interact with the command-line interface. Provide the requested strictly positive integer values (for example, `N=3`, `B=2`) and press `Enter`. The solutions for each Search Algorithm will then be visually printed out.

## Prerequisites
- Python 3.x installed on your machine.
- All included project files (`missionaries_and_cannibals.py`, `problem.py`, `bfs_algorithms.py`) must be located in the same folder.
