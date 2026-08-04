(define (domain autonomic-foundry)
  (:requirements :strips :typing :negative-preconditions)

  (:types concept)

  (:predicates
    (observed ?c - concept)
    (admitted ?c - concept)
    (resolved ?c - concept)
    (projected ?c - concept)
    (receipted ?c - concept)
    (blocked ?c - concept)
    (wip-free)
    (wip-active))

  (:action admit-concept
    :parameters (?c - concept)
    :precondition (and
      (observed ?c)
      (not (admitted ?c))
      (wip-free))
    :effect (and
      (admitted ?c)
      (wip-active)
      (not (wip-free))))

  (:action resolve-concept
    :parameters (?c - concept)
    :precondition (and
      (admitted ?c)
      (wip-active)
      (not (blocked ?c)))
    :effect (resolved ?c))

  (:action project-concept
    :parameters (?c - concept)
    :precondition (and
      (resolved ?c)
      (wip-active))
    :effect (projected ?c))

  (:action receipt-concept
    :parameters (?c - concept)
    :precondition (and
      (projected ?c)
      (wip-active))
    :effect (and
      (receipted ?c)
      (wip-free)
      (not (wip-active))))
)
