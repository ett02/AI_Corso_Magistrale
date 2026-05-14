import math
import random
import time

MAX_BOARD_SIZE = 16

ZOBRIST_TABLE = {
    "Red":  [[random.getrandbits(64) for _ in range(MAX_BOARD_SIZE)] for _ in range(MAX_BOARD_SIZE)],
    "Blue": [[random.getrandbits(64) for _ in range(MAX_BOARD_SIZE)] for _ in range(MAX_BOARD_SIZE)],
}
ZOBRIST_TURN = random.getrandbits(64)

# Memoria persistente condivisa tra tutti i turni della partita
_SHARED_TT      = {}
_SHARED_KILLERS = {}
_SHARED_HISTORY = [[[[0] * MAX_BOARD_SIZE for _ in range(MAX_BOARD_SIZE)]
                     for _ in range(MAX_BOARD_SIZE)]
                    for _ in range(MAX_BOARD_SIZE)]
_SHARED_AGE     = [0]


class TimeoutException(Exception):
    pass


class ZolaAI:
    # ------------------------------------------------------------------ init --
    def __init__(self, game, timeout=2.9):
        self.game        = game
        self.timeout     = timeout
        self.start_time  = 0
        self.root_player = None

        # Strutture condivise tra i turni (da DBZ)
        self.transposition_table = _SHARED_TT
        self.killer_moves        = _SHARED_KILLERS
        self.history             = _SHARED_HISTORY
        self.age                 = _SHARED_AGE

    # ------------------------------------------------------------- utilities --
    def check_time(self):
        if time.perf_counter() - self.start_time > self.timeout:
            raise TimeoutException()

    def _total_pieces(self, state):
        return state.count("Red") + state.count("Blue")

    def _get_phase(self, state):
        """Restituisce la fase di gioco in base al numero totale di pezzi."""
        total = self._total_pieces(state)
        if total > 20:
            return "opening"
        elif total <= 20:
            return "endgame"

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

    # ------------------------------------------------------------ heuristics --
    def _isolation_score(self, state, player):
        """
        Misura quanto i pezzi del giocatore sono isolati dai propri alleati.
        Valore più alto = pezzi più isolati (peggio per 'player').
        Usato in endgame per penalizzare pezzi nemici soli.
        """
        pieces = []
        for r in range(state.size):
            for c in range(state.size):
                if state.board[r][c] == player:
                    pieces.append((r, c))
        if len(pieces) <= 1:
            return 0
        total_dist = 0
        for i, (r1, c1) in enumerate(pieces):
            min_d = math.inf
            for j, (r2, c2) in enumerate(pieces):
                if i != j:
                    d = abs(r1 - r2) + abs(c1 - c2)
                    if d < min_d:
                        min_d = d
            total_dist += min_d
        return total_dist

    def evaluate_state(self, state):
        opponent = self.game.opponent(self.root_player)

        winner = self.game.winner(state)
        if winner == self.root_player:
            return 100_000
        if winner == opponent:
            return -100_000
        if winner is not None:
            return 0

        root_count     = state.count(self.root_player)
        opponent_count = state.count(opponent)

        root_moves     = self.game._actions_for_player(state, self.root_player)
        opponent_moves = self.game._actions_for_player(state, opponent)

        root_mobility     = len(root_moves)
        opponent_mobility = len(opponent_moves)

        root_captures     = sum(1 for m in root_moves     if m[2] is True)
        opponent_captures = sum(1 for m in opponent_moves if m[2] is True)

        phase = self._get_phase(state)

        # --- Pesi dinamici per fase ---
        if phase == "opening":
            w_material, w_capture, w_mobility = 100, 10, 1
            zugzwang_bonus = 0
            isolation_weight = 0
        elif phase == "midgame":
            w_material, w_capture, w_mobility = 100, 15, 3
            zugzwang_bonus = 20
            isolation_weight = 0
        else:  # endgame
            w_material, w_capture, w_mobility = 100, 20, 8
            zugzwang_bonus = 50
            isolation_weight = 3

        score  = (root_count - opponent_count) * w_material
        score += (root_captures - opponent_captures) * w_capture
        score += (root_mobility - opponent_mobility) * w_mobility

        # --- Bonus Zugzwang: penalizza l'avversario con pochissime mosse ---
        if opponent_mobility <= 2:
            score += (3 - opponent_mobility) * zugzwang_bonus

        # --- Isolation score in endgame: pezzi nemici isolati = vantaggio ---
        if isolation_weight > 0:
            opp_iso  = self._isolation_score(state, opponent)
            own_iso  = self._isolation_score(state, self.root_player)
            score += (opp_iso - own_iso) * isolation_weight

        return score

    # ----------------------------------------------------------- move ordering --
    def order_moves(self, moves, depth, tt_best_move=None):
        """
        Ordine: TT best move → catture → killer moves → history heuristic → altre.
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

        # History heuristic leggera: porta la quiet move con score più alto in testa O(N)
        if len(others) > 1:
            best_idx   = 0
            best_score = -1
            for idx, m in enumerate(others):
                if m != "PASS":
                    h = self.history[m[0][0]][m[0][1]][m[1][0]][m[1][1]]
                    if h > best_score:
                        best_score = h
                        best_idx   = idx
            if best_score > 0 and best_idx != 0:
                others[0], others[best_idx] = others[best_idx], others[0]

        return best + captures + killers + others

    # --------------------------------------------------------- alpha-beta core --
    def alphabeta(self, state, depth, alpha, beta, maximizing_player, current_hash,
                  use_forward_pruning=True):
        self.check_time()

        # --- Transposition Table lookup ---
        tt_entry    = self.transposition_table.get(current_hash)
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
                    beta = min(beta, tt_value)
                if alpha >= beta:
                    return tt_value, tt_best_move

        legal_moves = self.game.actions(state)

        if depth == 0 or self.game.is_terminal(state) or not legal_moves:
            return self.evaluate_state(state), None

        # --- Forward Pruning selettivo (solo in apertura/mediogioco) ---
        if use_forward_pruning:
            captures_only = [m for m in legal_moves if m[2]]
            if captures_only:
                legal_moves = captures_only
                # Paracadute: se tutte le catture portano a sconfitta certa,
                # recuperiamo anche le fughe
                fallback_needed = False
                temp_best_val   = -math.inf if maximizing_player else math.inf
                for m in captures_only:
                    child = self.game.result(state, m)
                    v, _  = self.alphabeta(child, 0, -math.inf, math.inf,
                                           not maximizing_player, current_hash,
                                           use_forward_pruning=False)
                    if maximizing_player:
                        temp_best_val = max(temp_best_val, v)
                    else:
                        temp_best_val = min(temp_best_val, v)
                if (maximizing_player and temp_best_val <= -9000) or                    (not maximizing_player and temp_best_val >= 9000):
                    fallback_needed = True
                if fallback_needed:
                    legal_moves = self.game.actions(state)

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
                    child_hash = base_child_hash
                    child_hash ^= ZOBRIST_TABLE[current_player][fr][fc]
                    if is_capture:
                        child_hash ^= ZOBRIST_TABLE[enemy][tr][tc]
                    child_hash ^= ZOBRIST_TABLE[current_player][tr][tc]

                child_state  = self.game.result(state, move)
                child_value, _ = self.alphabeta(
                    child_state, depth - 1, alpha, beta, False,
                    child_hash, use_forward_pruning
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
                        (fr, fc), (tr, tc), _ = move
                        self.history[fr][fc][tr][tc] += depth * depth
                    break
        else:
            value = math.inf
            for move in legal_moves:
                if move == "PASS":
                    child_hash = base_child_hash
                else:
                    (fr, fc), (tr, tc), is_capture = move
                    child_hash = base_child_hash
                    child_hash ^= ZOBRIST_TABLE[current_player][fr][fc]
                    if is_capture:
                        child_hash ^= ZOBRIST_TABLE[enemy][tr][tc]
                    child_hash ^= ZOBRIST_TABLE[current_player][tr][tc]

                child_state  = self.game.result(state, move)
                child_value, _ = self.alphabeta(
                    child_state, depth - 1, alpha, beta, True,
                    child_hash, use_forward_pruning
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
                        (fr, fc), (tr, tc), _ = move
                        self.history[fr][fc][tr][tc] += depth * depth
                    break

        # --- TT store con aging (da DBZ) ---
        flag = "EXACT"
        if value <= alpha_orig:
            flag = "UPPERBOUND"
        elif value >= beta_orig:
            flag = "LOWERBOUND"

        existing = self.transposition_table.get(current_hash)
        if (existing is None
                or depth >= existing[0]
                or self.age[0] - existing[4] >= 2):
            self.transposition_table[current_hash] = (
                depth, value, flag, best_move, self.age[0]
            )

        return value, best_move

    # --------------------------------------------------------- iterative search --
    def search(self, state):
        self.root_player = state.to_move
        self.start_time  = time.perf_counter()
        self.age[0]     += 1

        phase = self._get_phase(state)

        # Decadimento history (da DBZ)
        for r1 in range(state.size):
            for c1 in range(state.size):
                for r2 in range(state.size):
                    for c2 in range(state.size):
                        self.history[r1][c1][r2][c2] >>= 1

        # Pulizia TT lazy con aging
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

        # In endgame si disabilita il forward pruning e si punta a depth massima
        use_fp        = (phase != "endgame")
        # In endgame: ricerca esaustiva (depth molto alta, si ferma per timeout)
        max_depth_cap = 999

        depth = 1
        try:
            while depth <= max_depth_cap:
                val, current_best_move = self.alphabeta(
                    state, depth, -math.inf, math.inf,
                    True, current_hash, use_forward_pruning=use_fp
                )
                if current_best_move is not None:
                    best_move = current_best_move
                if val >= 90_000:
                    break
                depth += 1
        except TimeoutException:
            pass

        print(f"[AI UltraZ {self.root_player}] Fase: {phase} | "
              f"ForwardPruning: {use_fp} | "
              f"Profondità raggiunta: {depth - 1} | "
              f"Mossa scelta: {best_move}")

        return best_move


def playerStrategy(game, state, timeout=3):
    safe_timeout = max(0.1, timeout - 0.15)
    ai_bot       = ZolaAI(game, timeout=safe_timeout)
    return ai_bot.search(state)
