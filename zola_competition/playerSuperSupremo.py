import math
import random
import time


class TimeoutException(Exception):
    pass


class ZolaAI:
    def __init__(self, game, timeout=2.9):
        self.game = game
        self.timeout = timeout
        self.start_time = 0
        self.root_player = None
        # Transposition Table per memorizzare le posizioni valutate
        self.transposition_table = {}

    def check_time(self):
        """Solleva un'eccezione se il tempo limite sta per scadere."""
        if time.perf_counter() - self.start_time > self.timeout:
            raise TimeoutException()

    def get_state_hash(self, state):
        """Genera un hash unico e veloce per la scacchiera attuale."""
        board_tuple = tuple(tuple(row) for row in state.board)
        return hash((board_tuple, state.to_move))

    def evaluate_state(self, state):
        """
        Euristica Originale "Corretta". Molto veloce da calcolare.
        """
        winner = self.game.winner(state)
        if winner == self.root_player:
            return 100_000
        if winner == self.game.opponent(self.root_player):
            return -100_000
        if winner is not None:
            return 0

        opponent = self.game.opponent(self.root_player)

        root_count = state.count(self.root_player)
        opponent_count = state.count(opponent)

        root_moves = self.game._actions_for_player(state, self.root_player)
        opponent_moves = self.game._actions_for_player(state, opponent)

        root_mobility = len(root_moves)
        opponent_mobility = len(opponent_moves)

        root_captures = sum(1 for m in root_moves if m[2] is True)
        opponent_captures = sum(1 for m in opponent_moves if m[2] is True)

        score = 0
        score += (root_count - opponent_count) * 100
        score += (root_captures - opponent_captures) * 10
        score += (root_mobility - opponent_mobility) * 1

        return score

    def order_moves(self, moves, tt_best_move=None):
        """
        Move Ordering semplificato O(N).
        Priorità 1: Mossa Hash (Transposition Table)
        Priorità 2: Catture
        Priorità 3: Altre mosse
        """
        best = []
        captures = []
        others = []
        
        for m in moves:
            if tt_best_move and m == tt_best_move: # CHECK
                best.append(m)
            elif m[2]:  # is_capture
                captures.append(m)
            else:
                others.append(m)

        return best + captures + others

    def alphabeta(self, state, depth, alpha, beta, maximizing_player):
        self.check_time()

        state_hash = self.get_state_hash(state)
        tt_entry = self.transposition_table.get(state_hash)
        
        tt_best_move = None
        if tt_entry is not None:
            tt_depth, tt_value, tt_flag, tt_best_move_saved = tt_entry
            tt_best_move = tt_best_move_saved
            
            # Possiamo usare il valore dalla TT se l'abbiamo calcolato a una profondità sufficiente
            if tt_depth >= depth:
                if tt_flag == 'EXACT':
                    return tt_value, tt_best_move
                elif tt_flag == 'LOWERBOUND':
                    alpha = max(alpha, tt_value)
                elif tt_flag == 'UPPERBOUND':
                    beta = min(beta, tt_value)
                    
                if alpha >= beta:
                    return tt_value, tt_best_move

        legal_moves = self.game.actions(state)
        
        if depth == 0 or self.game.is_terminal(state) or not legal_moves:
            return self.evaluate_state(state), None

        # Passiamo la TT best move per metterla come primissima mossa da controllare
        legal_moves = self.order_moves(legal_moves, tt_best_move)
        best_move = None
        
        alpha_orig = alpha
        beta_orig = beta

        if maximizing_player:
            value = -math.inf
            for move in legal_moves:
                child_state = self.game.result(state, move)
                child_value, _ = self.alphabeta(
                    child_state, depth - 1, alpha, beta, False
                )

                if child_value > value:
                    value = child_value
                    best_move = move

                alpha = max(alpha, value)
                if alpha >= beta:
                    break

        else:
            value = math.inf
            for move in legal_moves:
                child_state = self.game.result(state, move)
                child_value, _ = self.alphabeta(
                    child_state, depth - 1, alpha, beta, True
                )

                if child_value < value:
                    value = child_value
                    best_move = move

                beta = min(beta, value)
                if alpha >= beta:
                    break

        # Salviamo in Transposition Table
        flag = 'EXACT'
        if value <= alpha_orig:
            flag = 'UPPERBOUND'
        elif value >= beta_orig:
            flag = 'LOWERBOUND'
            
        self.transposition_table[state_hash] = (depth, value, flag, best_move)

        return value, best_move

    def search(self, state):
        self.root_player = state.to_move
        self.start_time = time.perf_counter()
        
        # Svuotiamo la cache per liberare memoria
        self.transposition_table.clear()

        legal_moves = self.game.actions(state)
        if not legal_moves:
            return None

        best_move = random.choice(legal_moves) 
        
        depth = 1
        try:
            while True:
                val, current_best_move = self.alphabeta(
                    state, depth, -math.inf, math.inf, True
                )
                
                if current_best_move is not None:
                    best_move = current_best_move

                if val >= 90_000:
                    break
                    
                depth += 1
                
        except TimeoutException:
            pass

        print(f"[AI SuperSupremo {self.root_player}] Profondità raggiunta: {depth-1}. Mossa scelta: {best_move}")
        
        return best_move


def playerStrategy(game, state, timeout=3):
    safe_timeout = max(0.1, timeout - 0.15)
    ai_bot = ZolaAI(game, timeout=safe_timeout)
    return ai_bot.search(state)
