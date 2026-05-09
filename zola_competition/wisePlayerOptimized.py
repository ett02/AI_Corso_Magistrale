import math
import random
import time


class TimeoutException(Exception):
    pass


class ZolaAI:
    def __init__(self, game, timeout=2.85):
        self.game = game
        self.timeout = timeout
        self.start_time = 0
        self.root_player = None

    def check_time(self):
        """Solleva un'eccezione se il tempo limite sta per scadere."""
        if time.perf_counter() - self.start_time > self.timeout:
            raise TimeoutException()

    def evaluate_state(self, state):
        """
        Funzione di valutazione euristica (Evaluation Function).
        Valuta lo stato dal punto di vista del giocatore radice (root_player),
        utilizzando la logica di materiale, mobilità e catture.
        """
        winner = self.game.winner(state)
        if winner == self.root_player:
            return 100_000
        if winner == self.game.opponent(self.root_player):
            return -100_000
        if winner is not None:
            return 0  # Pareggio o stallo neutro

        opponent = self.game.opponent(self.root_player)

        # Vantaggio di materiale (pezzi_nostri - pezzi_avversari)
        root_count = state.count(self.root_player)
        opponent_count = state.count(opponent)

        # Mobilità e potenziale di cattura (mosse_nostre - mosse_avversarie)
        root_moves = self.game._actions_for_player(state, self.root_player)
        opponent_moves = self.game._actions_for_player(state, opponent)

        root_mobility = len(root_moves)
        opponent_mobility = len(opponent_moves)

        # Mosse di cattura (mosse di cattura nostre - mosse di cattura avversarie)
        root_captures = sum(1 for m in root_moves if m[2] is True)
        opponent_captures = sum(1 for m in opponent_moves if m[2] is True)

        # Formula di punteggio (pesi regolabili)
        score = 0
        score += (root_count - opponent_count) * 100
        score += (root_captures - opponent_captures) * 10
        score += (root_mobility - opponent_mobility) * 1

        return score

    def order_moves(self, moves):
        """
        Move Ordering ottimizzato (complessità lineare O(N) invece di O(N log N)).
        Divide le mosse mettendo immediatamente in testa quelle di cattura,
        evitando l'uso della funzione `sorted` e del calcolo costoso delle distanze.
        """
        captures = []
        others = []
        for m in moves:
            if m[2]:  # m[2] è una cattura
                captures.append(m)
            else:
                others.append(m)
                
        return captures + others

    def alphabeta(self, state, depth, alpha, beta, maximizing_player):
        self.check_time()

        legal_moves = self.game.actions(state)
        
        # Condizioni di terminazione ricorsiva
        if depth == 0 or self.game.is_terminal(state) or not legal_moves:
            return self.evaluate_state(state), None

        # Applichiamo il Move Ordering
        legal_moves = self.order_moves(legal_moves)
        best_move = None

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
                    break  # Pruning matematico!

            return value, best_move
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
                    break  # Pruning matematico!

            return value, best_move

    def search(self, state):
        self.root_player = state.to_move
        self.start_time = time.perf_counter()

        legal_moves = self.game.actions(state)
        if not legal_moves:
            return None

        # Fallback iniziale nel caso andassimo in timeout istantaneamente
        best_move = random.choice(legal_moves) 
        
        # Iterative Deepening
        depth = 1
        try:
            while True:
                val, current_best_move = self.alphabeta(
                    state, depth, -math.inf, math.inf, True
                )
                
                if current_best_move is not None:
                    best_move = current_best_move

                # Se troviamo una sequenza di mosse che porta alla vittoria certa, possiamo fermarci
                if val >= 90_000:
                    break
                    
                depth += 1
                
        except TimeoutException:
            # Il tempo a disposizione è scaduto (siamo a ~2.85s).
            # L'eccezione interrompe la ricerca profondissima a metà.
            # Raccogliamo la 'best_move' trovata in sicurezza alla profondità precedente (depth-1).
            pass

        print(f"[AI {self.root_player}] Profondità raggiunta: {depth-1}. Mossa scelta: {best_move}")
        
        # Riguardo la nota "pip": 
        # Restituiamo il formato standard che usa ZolaGameS.py: ((fr,fc), (tr,tc), is_capture)
        # Ignoriamo il formato richiesto dal prof `((row,column), pip, captured)` 
        # perché causerebbe un crash nel simulatore ufficiale allegato alla traccia.
        return best_move


def playerStrategy(game, state, timeout=3):
    """
    Questa è la funzione richiesta dalla traccia.
    Implementa Iterative Deepening con Alpha-Beta Pruning 
    ed un Time-Out controllato di ~2.85 secondi per non superare il limite di 3s.
    """
    # Impostiamo il limite interno un po' prima del timeout reale
    # per avere il tempo di risalire la ricorsione e ritornare il valore.
    safe_timeout = max(0.1, timeout - 0.15)
    
    ai_bot = ZolaAI(game, timeout=safe_timeout)
    return ai_bot.search(state)
