(define (domain linehaul_with_costs)
    ; In questo esempio non tutte le azioni hanno lo stesso costo. 
    ; In particolare le azioni relative all'operatore drive avranno un costo diverso a seconda del chilometraggio e del costo per km del mezzo.
    ; Il requirement :action-costs permette di definire funzioni matematiche che vengono incrementate o decrementate ad ogni azione.
    ; In particolare definiamo la funzione :total-cost che rappresenta il costo totale del piano
    ; e nell'azione :drive inseriamo l'effetto increase che incrementa il costo totale del piano.
    (:requirements :strips :typing :action-costs)

    (:types
      refrigerated_truck - truck
      location truck quantity
    )

    (:predicates
        (at ?t - truck ?l - location)
        (free_capacity ?t - truck ?q - quantity)
        (demand_chilled_goods ?l - location ?q - quantity)
        (demand_ambient_goods ?l - location ?q - quantity)
        (plus1 ?q1 ?q2 - quantity)
    )

    (:functions
        (distance ?l1 ?l2 - location)
        (per_km_cost ?t - truck)
        (total-cost)
    )

    ; The effect of the delivery action is to decrease demand at ?l and free capacity of ?t by one.
    (:action deliver_ambient
        :parameters (?t - truck ?l - location ?d ?d_less_one ?c ?c_less_one - quantity)
        :precondition (and (at ?t ?l)
            (demand_ambient_goods ?l ?d)
            (free_capacity ?t ?c)
            (plus1 ?d_less_one ?d) ;; only true if ?d > n0
            (plus1 ?c_less_one ?c)) ;; only true if ?c > n0
        :effect (and (not (demand_ambient_goods ?l ?d))
            (demand_ambient_goods ?l ?d_less_one)
            (not (free_capacity ?t ?c))
            (free_capacity ?t ?c_less_one))
    )

    (:action deliver_chilled
        ;; Note type restriction on ?t: it must be a refrigerated truck.
        :parameters (?t - refrigerated_truck ?l - location ?d ?d_less_one ?c ?c_less_one - quantity)
        :precondition (and (at ?t ?l)
            (demand_chilled_goods ?l ?d)
            (free_capacity ?t ?c)
            (plus1 ?d_less_one ?d) ;; only true if ?d > n0
            (plus1 ?c_less_one ?c)) ;; only true if ?c > n0
        :effect (and (not (demand_chilled_goods ?l ?d))
            (demand_chilled_goods ?l ?d_less_one)
            (not (free_capacity ?t ?c))
            (free_capacity ?t ?c_less_one))
    )

    (:action drive
        :parameters (?t - truck ?from ?to - location)
        :precondition (at ?t ?from)
        :effect (and (not (at ?t ?from))
            (at ?t ?to)
            (increase
                (total-cost)
                (* (distance ?from ?to) (per_km_cost ?t))))
    )

)