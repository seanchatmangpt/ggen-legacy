# After Code Reading Review Standard

## Purpose

This standard governs every substantial repository, PRD, ARD, pull request, benchmark, release note, and public claim that presents itself as contributing to trustworthy software production after mandatory human source inspection leaves the critical path.

It does not forbid source reading. It forbids replacing source reading with weaker assurance while claiming a stronger production model.

## Required review questions

Every material change answers:

1. **What human source-reading or source-writing task is removed from the critical path?**
2. **What machine control replaces it?**
3. **What new risk is introduced by that replacement?**
4. **Which authority defines the intended consequence?**
5. **Which architecture rule prevents silent drift?**
6. **Which planner, workflow, or deterministic rule selects the production route?**
7. **Who or what authorizes actuation?**
8. **Which mechanism independently attempts to falsify the result?**
9. **Which runtime evidence establishes what actually occurred?**
10. **Which typed state may the result receive?**
11. **Which receipt binds the production path?**
12. **How is the result replayed from a clean state?**
13. **What exact observation would falsify completion?**
14. **What remains `UNKNOWN`, `UNSUPPORTED`, or outside scope?**

A missing answer blocks any no-read or post-manual-code claim.

## Pull request template

```markdown
## After Code Reading contribution

### Human critical-path task removed

### Replacement machine control

### New risk introduced

### Admitted authority

### Planning and abstention

### Actuation boundary

### Independent verifier

### Positive witnesses

### Negative falsifiers

### Operational evidence

### Receipt and replay

### Claim ceiling and standing

### Same-object falsifier

### Explicit unknowns and exclusions
```

## README opening standard

A participating repository README should identify, in order:

1. the human code-reading bottleneck it addresses;
2. the repository's specific contribution;
3. the hard invariant it preserves;
4. the current evidence state;
5. the condition that would falsify the claim.

## PRD/ARD standard

A PRD or ARD must contain:

- contribution to After Code Reading;
- human responsibility retained;
- manual construction or inspection removed;
- machine authority introduced;
- authority and trust boundaries;
- independent verifier;
- receipt and replay;
- claim ceiling;
- same-object falsifier.

## Release-note standard

Release notes should report consequences and displaced critical-path labor rather than feature count alone.

Required fields:

- verified consequences produced;
- human implementation-reading requirement before and after;
- new automatic gates;
- new refusal conditions;
- evidence and replay result;
- exact standing;
- unresolved risks.

## Benchmark standard

The default metric is:

```text
Post-Reading Throughput
=
verified engineering consequences
/
(human inspection time + elapsed time + compute + coordination)
```

At minimum, a benchmark records:

- exact workload and source coordinate;
- manual source lines read and written;
- human attention minutes;
- admitted requirements;
- verifier inventory;
- tests and falsifiers executed;
- architecture violations found;
- mutation and fuzz results where applicable;
- runtime evidence;
- receipt completeness;
- replay result;
- unsupported claims refused;
- cost and elapsed time;
- final typed state.

Generated code volume, commits, or tokens may be reported as machine-utilization measures. They are not product throughput.

## No-read admission checklist

A bounded no-read claim requires all checks:

```text
[ ] exact product boundary named
[ ] exact source and authority identities bound
[ ] requirements admitted
[ ] architecture constraints executable
[ ] planner or deterministic production law declared
[ ] no-change/abstention/refusal represented
[ ] actuation separately authorized
[ ] producer and verifier separated
[ ] positive witnesses executed
[ ] negative falsifiers executed
[ ] runtime evidence captured
[ ] standing independently computed
[ ] receipt valid
[ ] clean replay matched
[ ] manual implementation reading not required for acceptance
```

Unchecked items prevent `ALIVE` and prevent the unqualified phrase “manufactured without reading code.”

## Automatic refusal conditions

Return `REFUSED` or a bounded blocking state when:

- code reading was removed but no replacement control exists;
- the producer's own generated tests are the sole verifier;
- requirements exist only as prompts or unadmitted prose;
- architecture is not executable or independently inspectable;
- planning and actuation share ambient authority;
- silence, absence of findings, or missing observation is treated as success;
- no-change cannot be represented;
- generated output is manually patched;
- receipt identity is incomplete;
- replay has not occurred;
- documentation exceeds the evidence ceiling.

## Reviewer decision

The reviewer emits one of:

- `ALIVE` — complete declared boundary independently verified and replayed;
- `PARTIAL_ALIVE` — bounded subset observed; crown remains open;
- `BLOCKED` — required authority, dependency, permission, or evidence unavailable;
- `BUILD_BROKEN` — declared manufacture or verification command failed;
- `UNKNOWN` — insufficient observation;
- `UNSUPPORTED` — outside the declared product boundary;
- `REFUSED` — proposed actuation or claim violates policy.

## Core doctrine

> **Do not ask whether someone read the code. Ask which authority governed production, which independent mechanisms tried to disprove the result, what actually executed, which evidence granted standing, and whether the complete run can be replayed.**
