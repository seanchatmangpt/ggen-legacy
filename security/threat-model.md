# Threat Model

## Assets

Source repositories and history, credentials, customer configuration, semantic authority, capability ledgers, projectors, generated artifacts, evidence, receipts, release decisions, and retirement authorizations.

## Adversaries

Malicious contributor, compromised dependency, untrusted repository, overprivileged agent, insider, supply-chain attacker, evidence forger, replay attacker, confused deputy, and operator under schedule pressure.

## Principal threats

- path or symlink escape during observation or manufacture;
- command injection through repository content;
- secret exfiltration through logs or generated output;
- authority poisoning, provenance substitution, or stale revision;
- duplicate owners or ambiguous merge law;
- stale-head verification;
- generated-output tampering;
- receipt forgery, omission, reordering, or duplicate replay;
- direct actuation bypassing the broker;
- self-certification loops;
- evidence retention or residency violation;
- premature release or sunset authorization;
- destructive cleanup of behavior not yet inventoried.

## Required mitigations

Sandboxed workers, outbound deny, capability-based filesystem access, path canonicalization, immutable inputs, digest binding, pinned dependencies, secret redaction, policy admission, independent verification, state-preserving refusals, immutable evidence storage, and separate release/sunset authority.

## Security falsifiers

Negative fixtures include path escape, symlink escape, unowned write, direct actuation, stale coordinate, missing/tampered receipt, duplicate replay, authority contradiction, premature authorization, and replay divergence.

A threat model and scanner report do not establish production security standing.
