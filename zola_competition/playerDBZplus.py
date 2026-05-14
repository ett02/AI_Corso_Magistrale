import math
import random
import time

MAX_BOARD_SIZE = 16
ZOBRIST_TABLE = {
    "Red":  [[random.getrandbits(64) for _ in range(MAX_BOARD_SIZE)] for _ in range(MAX_BOARD_SIZE)],
    "Blue": [[random.getrandbits(64) for _ in range(MAX_BOARD_SIZE)] for _ in range(MAX_BOARD_SIZE)],
}
ZOBRIST_TURN = random.getrandbits(64)

# Memoria persistente condivisa tra tutti i turni del bot
_SHARED_TT      = {}
_SHARED_KILLERS = {}
# History: solo celle [fr][fc][tr][tc] usate (dict sparse invece di matrice 4D)
_SHARED_HISTORY = {}
_SHARED_AGE     = [0]


class TimeoutException(Exception):
    pass


class ZolaAI:
    def __init__(self, game, timeout=2.9):
        self.game        = game
        self.timeout     = timeout
        self.start_time  = 0
        self.root_player = None
        self.transposition_table = _SHARED_TT
        self.killer_moves        = _SHARED_KILLERS
        self.history             = _SHARED_HISTORY
        self.age                 = _SHARED_AGE

    # ---------------------------------------------------------------- utils --
    def check_time(self):
        if time.perf_counter() - self.start_time > self.timeout:
            raise TimeoutException()

    def _total_pieces(self, state):
        return state.count("Red") + state.count("Blue")

    def _is_endgame(self, state):
        return self._total_pieces(state) <= 14

    # ----------------------------------------------------------- zobrist hash --
    def compute_initial_zobrist(self, state):
        h = 0
        for r in range(state.size):
            for c in range(state.size):
                piece = state.board[r][c]
                if piece is not None:
                    h ^= ZOBRIST_TABLE[piece][r][c]
        if state.to_move == "Blue":
            h ^= ZOBRIST_TURN
        return h

    # -------------------------------------------------------------- euristica --
    def evaluate_state(self, state):
        opponent = self.game.opponent(self.root_player)

        winner = self.game.winner(state)
        if winner == self.root_player:   return  100_000
        if winner == opponent:           return -100_000
        if winner is not None:           return  0

        root_count     = state.count(self.root_player)
        opponent_count = state.count(opponent)

        root_moves     = self.game._actions_for_player(state, self.root_player)
        opponent_moves = self.game._actions_for_player(state, opponent)

        root_mobility     = len(root_moves)
        opponent_mobility = len(opponent_moves)

        root_captures     = sum(1 for m in root_moves     if m[2] is True)
        opponent_captures = sum(1 for m in opponent_moves if m[2] is True)

        # Pesi dinamici: in endgame mobilità e catture pesano di più
        if self._is_endgame(state):
            w_mat, w_cap, w_mob = 100, 20, 8
            # Bonus Zugzwang leggero: avversario quasi bloccato
            if opponent_mobility <= 2:
                zug = (3 - opponent_mobility) * 40
            else:
                zug = 0
        else:
            w_mat, w_cap, w_mob = 100, 10, 1
            zug = 0

        score  = (root_count     - opponent_count)     * w_mat
        score += (root_captures  - opponent_captures)  * w_cap
        score += (root_mobility  - opponent_mobility)  * w_mob
        score += zug
        return score

    # ---------------------------------------------------------- move ordering --
    def order_moves(self, moves, depth, tt_best_move=None):
        """
        TT best → catture → killers → history best → altre.
        History sparse (dict) invece di matrice 4D.
        """
        best     = []
        captures = []
        killers  = []
        others   = []

        k1, k2 = self.killer_moves.get(depth, (None, None))

        for m in moves:
            if tt_best_move and m == tt_best_move:
                best.append(m)
            elif m[2]:
                captures.append(m)
            elif m == k1 or m == k2:
                killers.append(m)
            else:
                others.append(m)

        # History leggera O(N): porta la quiet con score massimo in testa
        if len(others) > 1:
            best_idx   = 0
            best_score = -1
            for idx, m in enumerate(others):
                if m != "PASS":
                    h = self.history.get((m[0], m[1]), 0)
                    if h > best_score:
                        best_score = h
                        best_idx   = idx
            if best_score > 0 and best_idx != 0:
                others[0], others[best_idx] = others[best_idx], others[0]

        return best + captures + killers + others

    # ------------------------------------------------------- alpha-beta core --
    def alphabeta(self, state, depth, alpha, beta, maximizing_player, current_hash):
        self.check_time()

        tt_entry     = self.transposition_table.get(current_hash)
        tt_best_move = None
        if tt_entry is not None:
            tt_depth, tt_value, tt_flag, tt_best_move_saved, _tt_age = tt_entry
            tt_best_move = tt_best_move_saved
            if tt_depth >= depth:
                if tt_flag == "EXACT":
                    return tt_value, tt_best_move
                elif tt_flag == "LOWERBOUND":
                    alpha = max(alpha, tt_value)
                elif tt_flag == "UPPERBOUND":
                    beta  = min(beta, tt_value)
                if alpha >= beta:
                    return tt_value, tt_best_move

        legal_moves = self.game.actions(state)

        if depth == 0 or self.game.is_terminal(state) or not legal_moves:
            return self.evaluate_state(state), None

        legal_moves = self.order_moves(legal_moves, depth, tt_best_move)
        best_move   = None
        alpha_orig  = alpha
        beta_orig   = beta

        current_player  = state.to_move
        enemy           = self.game.opponent(current_player)
        base_child_hash = current_hash ^ ZOBRIST_TURN

        if maximizing_player:
            value = -math.inf
            for move in legal_moves:
                if move == "PASS":
                    child_hash = base_child_hash
                else:
                    (fr, fc), (tr, tc), is_capture = move
                    child_hash = base_child_hash ^ ZOBRIST_TABLE[current_player][fr][fc]
                    if is_capture:
                        child_hash ^= ZOBRIST_TABLE[enemy][tr][tc]
                    child_hash ^= ZOBRIST_TABLE[current_player][tr][tc]

                child_state  = self.game.result(state, move)
                child_value, _ = self.alphabeta(
                    child_state, depth - 1, alpha, beta, False, child_hash
                )
                if child_value > value:
                    value     = child_value
                    best_move = move
                alpha = max(alpha, value)
                if alpha >= beta:
                    if move != "PASS" and not move[2]:
                        k1, k2 = self.killer_moves.get(depth, (None, None))
                        if move != k1:
                            self.killer_moves[depth] = (move, k1)
                        key = (move[0], move[1])
                        self.history[key] = self.history.get(key, 0) + depth * depth
                    break
        else:
            value = math.inf
            for move in legal_moves:
                if move == "PASS":
                    child_hash = base_child_hash
                else:
                    (fr, fc), (tr, tc), is_capture = move
                    child_hash = base_child_hash ^ ZOBRIST_TABLE[current_player][fr][fc]
                    if is_capture:
                        child_hash ^= ZOBRIST_TABLE[enemy][tr][tc]
                    child_hash ^= ZOBRIST_TABLE[current_player][tr][tc]

                child_state  = self.game.result(state, move)
                child_value, _ = self.alphabeta(
                    child_state, depth - 1, alpha, beta, True, child_hash
                )
                if child_value < value:
                    value     = child_value
                    best_move = move
                beta = min(beta, value)
                if alpha >= beta:
                    if move != "PASS" and not move[2]:
                        k1, k2 = self.killer_moves.get(depth, (None, None))
                        if move != k1:
                            self.killer_moves[depth] = (move, k1)
                        key = (move[0], move[1])
                        self.history[key] = self.history.get(key, 0) + depth * depth
                    break

        # TT store con aging
        flag = "EXACT"
        if value <= alpha_orig: flag = "UPPERBOUND"
        elif value >= beta_orig: flag = "LOWERBOUND"

        existing = self.transposition_table.get(current_hash)
        if (existing is None
                or depth >= existing[0]
                or self.age[0] - existing[4] >= 2):
            self.transposition_table[current_hash] = (
                depth, value, flag, best_move, self.age[0]
            )

        return value, best_move

    # -------------------------------------------------------- iterative search --
    def search(self, state):
        self.root_player = state.to_move
        self.start_time  = time.perf_counter()
        self.age[0]     += 1

        # Decay history sparse: dimezza solo le celle effettivamente usate
        to_del = []
        for k in self.history:
            self.history[k] >>= 1
            if self.history[k] == 0:
                to_del.append(k)
        for k in to_del:
            del self.history[k]

        # TT: pulizia lazy con aging
        if len(self.transposition_table) > 1_000_000:
            to_remove = [k for k, v in self.transposition_table.items()
                         if self.age[0] - v[4] >= 3]
            for k in to_remove:
                del self.transposition_table[k]

        legal_moves = self.game.actions(state)
        if not legal_moves:
            return None

        best_move    = random.choice(legal_moves)
        current_hash = self.compute_initial_zobrist(state)

        depth = 1
        try:
            while True:
                val, current_best_move = self.alphabeta(
                    state, depth, -math.inf, math.inf, True, current_hash
                )
                if current_best_move is not None:
                    best_move = current_best_move
                if val >= 90_000:
                    break
                depth += 1
        except TimeoutException:
            pass

        print(f"[AI DBZ+ {self.root_player}] Endgame: {self._is_endgame(state)} | "
              f"Profondità: {depth - 1} | Mossa: {best_move}")
        return best_move


def playerStrategy(game, state, timeout=3):
    safe_timeout = max(0.1, timeout - 0.15)
    ai_bot       = ZolaAI(game, timeout=safe_timeout)
    return ai_bot.search(state)
