(define (domain knights-tour)
    ; Nel PDDL standard (STRIPS), le precondizioni possono verificare solo se un predicato è vero
    ; Per poter verificare se un predicato è falso, è necessario utilizzare il requirement :negative-preconditions
    ; Cioè in questo modo si può usare l'operatore (not (...)) all'interno del blocco :precondition
    ; in particolare lo usiamo per verificare che la cella di desinazione di una mossa sia non visitata (not (visited ?to))
    (:requirements :negative-preconditions)

    (:predicates
        (at ?square)
        (visited ?square)
        (valid_move ?square_from ?square_to)
    )

    (:action move
        :parameters (?from ?to)
        :precondition (and (at ?from)
            (valid_move ?from ?to)
            (not (visited ?to)))
        :effect (and (not (at ?from))
            (at ?to)
            (visited ?to))
    )
)