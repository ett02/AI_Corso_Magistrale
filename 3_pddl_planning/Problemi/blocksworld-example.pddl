(define (problem blocksworld-example)
    (:domain blocksworld)

    (:objects
        red yellow blue orange - block
    )

    (:init
        (ontable yellow)
        (ontable orange)
        (ontable red)
        (on blue orange)
        (clear blue)
        (clear red)
        (clear yellow)
        (handempty)
    )

    (:goal
        (and
            (on orange blue)
            (ontable blue)
            (ontable yellow)
            (ontable red)
            (clear orange)
            (clear yellow)
            (clear red))
    )
)