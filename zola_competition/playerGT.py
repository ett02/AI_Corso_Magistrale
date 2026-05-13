import math
import random
import time

MAX_BOARD_SIZE = 16

# Generazione statica delle tabelle di Zobrist (1 volta all'avvio)
ZOBRIST_TABLE = {
    "Red": [[random.getrandbits(64) for _ in range(MAX_BOARD_SIZE)] for _ in range(MAX_BOARD_SIZE)],
    "Blue": [[random.getrandbits(64) for _ in range(MAX_BOARD_SIZE)] for _ in range(MAX_BOARD_SIZE)]
}
ZOBRIST_TURN = random.getrandbits(64)

# Memoria persistente condivisa tra tutti i turni del bot
_SHARED_TT = {}
_SHARED_KILLERS = {}
_SHARED_HISTORY = [[[[0] * MAX_BOARD_SIZE for _ in range(MAX_BOARD_SIZE)]
                     for _ in range(MAX_BOARD_SIZE)]
                    for _ in range(MAX_BOARD_SIZE)]
_SHARED_AGE = [0]


class TimeoutException(Exception):
    pass


class ZolaAI:
    def __init__(self, game, timeout=2.9):
        self.game = game
        self.timeout = timeout
        self.start_time = 0
        self.root_player = None
        self.transposition_table = _SHARED_TT
        self.killer_moves = _SHARED_KILLERS
        self.history = _SHARED_HISTORY
        self.age = _SHARED_AGE
        self.completed_depth = 0

    # ── Zobrist Hashing ──────────────────────────────────────────────

    def compute_initial_zobrist(self, state):
        """Calcola l'hash iniziale della scacchiera in O(N²)."""
        h = 0
        for r in range(state.size):
            for c in range(state.size):
                piece = state.board[r][c]
                if piece is not None:
                    h ^= ZOBRIST_TABLE[piece][r][c]
        if state.to_move == "Blue":
            h ^= ZOBRIST_TURN
        return h

    # ── Timeout ──────────────────────────────────────────────────────

    def check_time(self):
        if time.perf_counter() - self.start_time > self.timeout:
            raise TimeoutException()

    # ── Euristica Originale (adattata per NegaMax) ───────────────────

    def evaluate_state(self, state):
        """
        Euristica semplice identica a playerSuperSupremo/wisePlayerOptimized.
        Adattata per NegaMax: valuta dal punto di vista di state.to_move.
        Pesi: materiale ×100, catture ×10, mobilità ×1.
        """
        current = state.to_move
        opponent = self.game.opponent(current)

        winner = self.game.winner(state)
        if winner == current:
            return 100_000
        if winner == opponent:
            return -100_000
        if winner is not None:
            return 0

        my_count = state.count(current)
        opp_count = state.count(opponent)

        my_moves = self.game._actions_for_player(state, current)
        opp_moves = self.game._actions_for_player(state, opponent)

        my_mobility = len(my_moves)
        opp_mobility = len(opp_moves)

        my_captures = sum(1 for m in my_moves if m[2] is True)
        opp_captures = sum(1 for m in opp_moves if m[2] is True)

        score = 0
        score += (my_count - opp_count) * 100
        score += (my_captures - opp_captures) * 10
        score += (my_mobility - opp_mobility) * 1

        return score

    # ── Move Ordering ────────────────────────────────────────────────

    def order_moves(self, moves, depth, tt_best_move=None):
        """
        Move ordering avanzato con History Heuristic:
        1. TT best move
        2. Catture
        3. Killer moves
        4. Quiet moves ordinate per history score
        """
        tt_list = []
        captures = []
        killers = []
        quiet = []

        k1, k2 = self.killer_moves.get(depth, (None, None))

        for m in moves:
            if m == "PASS":
                quiet.append(m)
            elif tt_best_move and m == tt_best_move:
                tt_list.append(m)
            elif m[2]:  # is_capture
                captures.append(m)
            elif m == k1 or m == k2:
                killers.append(m)
            else:
                quiet.append(m)

        # Ordina le mosse quiet per history score (decrescente)
        if quiet and quiet[0] != "PASS":
            quiet.sort(
                key=lambda m: self.history[m[0][0]][m[0][1]][m[1][0]][m[1][1]]
                    if m != "PASS" else -1,
                reverse=True
            )

        return tt_list + captures + killers + quiet

    # ── Aggiornamento Killer e History ───────────────────────────────

    def update_killers(self, move, depth):
        if move != "PASS" and not move[2]:
            k1, k2 = self.killer_moves.get(depth, (None, None))
            if move != k1:
                self.killer_moves[depth] = (move, k1)

    def update_history(self, move, depth):
        if move != "PASS" and not move[2]:
            (fr, fc), (tr, tc), _ = move
            self.history[fr][fc][tr][tc] += depth * depth

    # ── NegaMax con TT + LMR + Futility Pruning ─────────────────────

    def negamax(self, state, depth, alpha, beta, current_hash):
        """
        NegaMax con:
        - Transposition Table (Zobrist)
        - Late Move Reduction (LMR)
        - Futility Pruning
        - Killer Moves + History Heuristic
        """
        self.check_time()

        # ── TT Lookup ──
        tt_entry = self.transposition_table.get(current_hash)
        tt_best_move = None
        if tt_entry is not None:
            tt_depth, tt_value, tt_flag, tt_bm, _ = tt_entry
            tt_best_move = tt_bm

            if tt_depth >= depth:
                if tt_flag == 'EXACT':
                    return tt_value, tt_best_move
                elif tt_flag == 'LOWERBOUND':
                    alpha = max(alpha, tt_value)
                elif tt_flag == 'UPPERBOUND':
                    beta = min(beta, tt_value)

                if alpha >= beta:
                    return tt_value, tt_best_move

        # ── Terminazione ──
        legal_moves = self.game.actions(state)

        if depth == 0 or self.game.is_terminal(state) or not legal_moves:
            return self.evaluate_state(state), None

        # ── Futility Pruning (depth <= 2, solo mosse quiet) ──
        futility_prune = False
        if depth <= 2:
            static_eval = self.evaluate_state(state)
            margin = 150 if depth == 1 else 350
            if static_eval + margin <= alpha:
                capture_moves = [m for m in legal_moves if m != "PASS" and m[2]]
                if not capture_moves:
                    return static_eval, None
                legal_moves = capture_moves
                futility_prune = True

        # ── Move Ordering ──
        legal_moves = self.order_moves(legal_moves, depth, tt_best_move)

        alpha_orig = alpha
        best_value = -math.inf
        best_move = legal_moves[0] if legal_moves else None

        current_player = state.to_move
        enemy = self.game.opponent(current_player)
        base_child_hash = current_hash ^ ZOBRIST_TURN

        for i, move in enumerate(legal_moves):
            # ── Calcola hash figlio incrementalmente ──
            if move == "PASS":
                child_hash = base_child_hash
            else:
                (fr, fc), (tr, tc), is_capture = move
                child_hash = base_child_hash
                child_hash ^= ZOBRIST_TABLE[current_player][fr][fc]
                if is_capture:
                    child_hash ^= ZOBRIST_TABLE[enemy][tr][tc]
                child_hash ^= ZOBRIST_TABLE[current_player][tr][tc]

            child_state = self.game.result(state, move)

            # ── LMR: Late Move Reduction ──
            is_quiet = (move != "PASS" and not move[2])
            do_lmr = (i >= 3 and depth >= 3 and is_quiet and not futility_prune)

            if do_lmr:
                # Ricerca ridotta (zero-window, depth - 2)
                value = -self.negamax(
                    child_state, depth - 2, -(alpha + 1), -alpha, child_hash
                )[0]

                if value > alpha:
                    # Sorpresa: ri-cerca a profondità piena
                    value = -self.negamax(
                        child_state, depth - 1, -beta, -alpha, child_hash
                    )[0]
            else:
                # Ricerca a profondità piena
                value = -self.negamax(
                    child_state, depth - 1, -beta, -alpha, child_hash
                )[0]

            if value > best_value:
                best_value = value
                best_move = move

            alpha = max(alpha, value)
            if alpha >= beta:
                self.update_killers(move, depth)
                self.update_history(move, depth)
                break

        # ── TT Store con Replacement Policy ──
        flag = 'EXACT'
        if best_value <= alpha_orig:
            flag = 'UPPERBOUND'
        elif best_value >= beta:
            flag = 'LOWERBOUND'

        existing = self.transposition_table.get(current_hash)
        if (existing is None
                or depth >= existing[0]
                or self.age[0] - existing[4] >= 2):
            self.transposition_table[current_hash] = (
                depth, best_value, flag, best_move, self.age[0]
            )

        return best_value, best_move

    # ── Iterative Deepening con Aspiration Windows ───────────────────

    def search(self, state):
        self.root_player = state.to_move
        self.start_time = time.perf_counter()
        self.age[0] += 1

        # Decadimento della history table
        for r1 in range(state.size):
            for c1 in range(state.size):
                for r2 in range(state.size):
                    for c2 in range(state.size):
                        self.history[r1][c1][r2][c2] >>= 1

        # Pulizia TT se troppo grande
        if len(self.transposition_table) > 800_000:
            to_remove = [k for k, v in self.transposition_table.items()
                         if self.age[0] - v[4] >= 3]
            for k in to_remove:
                del self.transposition_table[k]
            if len(self.transposition_table) > 800_000:
                self.transposition_table.clear()

        legal_moves = self.game.actions(state)
        if not legal_moves:
            return None

        best_move = random.choice(legal_moves)
        current_hash = self.compute_initial_zobrist(state)

        # Aspiration Windows
        prev_score = 0
        WINDOW = 50
        self.completed_depth = 0

        depth = 1
        try:
            while True:
                if depth > 1:
                    a = prev_score - WINDOW
                    b = prev_score + WINDOW
                else:
                    a = -math.inf
                    b = math.inf

                val, current_best = self.negamax(
                    state, depth, a, b, current_hash
                )

                # Se fuori finestra, ri-cerca con finestra piena
                if val is not None and (val <= a or val >= b):
                    val, current_best = self.negamax(
                        state, depth, -math.inf, math.inf, current_hash
                    )

                self.completed_depth = depth

                if current_best is not None:
                    best_move = current_best
                    prev_score = val

                if val >= 90_000:
                    break

                depth += 1

        except TimeoutException:
            pass

        print(f"[AI GT {self.root_player}] Profondità raggiunta: {self.completed_depth}. Mossa scelta: {best_move}")
        return best_move


def playerStrategy(game, state, timeout=3):
    safe_timeout = max(0.1, timeout - 0.15)
    ai_bot = ZolaAI(game, timeout=safe_timeout)
    return ai_bot.search(state)
