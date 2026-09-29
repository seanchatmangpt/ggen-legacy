---- MODULE GGenLegacyV26928 ----
EXTENDS Naturals, Sequences
CONSTANTS Observed, Admitted, Planned, Manufactured, Verified, Receipted, Replayed, Released, Refused
VARIABLE state

Init == state = Observed
Next ==
  \/ /\ state = Observed /\ state' \in {Admitted, Refused}
  \/ /\ state = Admitted /\ state' = Planned
  \/ /\ state = Planned /\ state' \in {Manufactured, Refused}
  \/ /\ state = Manufactured /\ state' \in {Verified, Refused}
  \/ /\ state = Verified /\ state' = Receipted
  \/ /\ state = Receipted /\ state' \in {Replayed, Refused}
  \/ /\ state = Replayed /\ state' = Released
  \/ /\ state \in {Released, Refused} /\ UNCHANGED state

NoReleaseWithoutReplay == state = Released => state # Observed
TypeOK == state \in {Observed, Admitted, Planned, Manufactured, Verified, Receipted, Replayed, Released, Refused}
Spec == Init /\ [][Next]_state
====
