(define (domain career-capability-admission)
  (:requirements :strips)
  (:predicates
    (admitted-python)
    (admitted-cloud)
    (admitted-distributed-systems)
    (admitted-agentic-architecture)
    (admitted-forward-deployment))

  (:action admit-cloud
    :parameters ()
    :precondition (admitted-python)
    :effect (admitted-cloud))

  (:action admit-distributed-systems
    :parameters ()
    :precondition (admitted-python)
    :effect (admitted-distributed-systems))

  (:action admit-agentic-architecture
    :parameters ()
    :precondition (and (admitted-cloud) (admitted-distributed-systems))
    :effect (admitted-agentic-architecture))

  (:action admit-forward-deployment
    :parameters ()
    :precondition (admitted-agentic-architecture)
    :effect (admitted-forward-deployment))
)
