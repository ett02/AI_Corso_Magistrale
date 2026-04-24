(define (domain blocksworld)
    (:requirements :strips :typing) ; Definisce le funzionalità PDDL usate: :strips per la logica base (fatti positivi o negativi) e :typing per l'uso dei tipi.

    (:types
        block
    )

    (:predicates ; Definisce i predicati usati nel dominio.
        (on ?x - block ?y - block) ; Indica che il blocco ?x è sopra il blocco ?y.
        (ontable ?x - block) ; Indica che il blocco ?x è sul tavolo.
        (clear ?x - block) ; Indica che il blocco ?x è libero (non ha nulla sopra).
        (holding ?x - block) ; Indica che la mano sta tenendo il blocco ?x.
        (handempty) ; Indica che la mano è vuota.
    )

    (:action pick-up
        :parameters (?x - block)
        :precondition (and (clear ?x) (ontable ?x) (handempty))
        :effect (and
            (not (ontable ?x))
            (not (clear ?x))
            (not (handempty))
            (holding ?x))
    )

    (:action put-down
        :parameters (?x - block)
        :precondition (holding ?x)
        :effect (and
            (ontable ?x)
            (clear ?x)
            (handempty)
            (not (holding ?x)))
    )

    (:action unstack ; Solleva il blocco ?x dal blocco ?y.
        :parameters (?x - block ?y - block)
        :precondition (and (on ?x ?y) (clear ?x) (handempty))
        :effect (and
            (holding ?x)
            (clear ?y)
            (not (on ?x ?y))
            (not (clear ?x))
            (not (handempty)))
    )

    (:action stack ; Impila il blocco ?x sul blocco ?y.
        :parameters (?x - block ?y - block)
        :precondition (and (holding ?x) (clear ?y))
        :effect (and
            (on ?x ?y)
            (clear ?x)
            (handempty)
            (not (holding ?x))
            (not (clear ?y)))
    )
)