---
name: cant-evals
description: Generate CANT-tagged behavioral eval cases when adding or updating a skill in a Kanopi skills plugin (cms-cultivator, delivery-record, premium-service-skills, devops-skills, pm-skills, or any repo derived from skills-plugin-template). Invoke when a new skill needs gate and pressure cases, when the user says "add CANT evals", "behavioral evals for this skill", "pressure case", "gate case", "test this skill's promises", or after writing a SKILL.md with side effects or honesty rules.
---

# CANT Evals

Turn a skill's behavioral promises into executable, CANT-tagged eval cases
for the behavioral eval harness (`scripts/run-behavioral-evals.sh` in every
repo derived from skills-plugin-template).

The premise, from the catalog this plugin ships: agents rarely fail because
they can't do the job. They fail because something supplied a justification.
A rule written in a skill file is a suggestion until something checks it.
This skill writes the checks.

## Inputs

- **The target repo is the current working directory.** Every path below
  (`skills/`, `evals/cases/`, `scripts/`) is relative to it. Never search
  for the skill under test outside the cwd; the one exception is the
  catalog, which ships with this plugin.
- **The skill under test**: `skills/<name>/SKILL.md` in the target repo,
  usually the one just added or changed (check `git status` / `git diff`,
  or list `skills/`).
- **The catalog**: `${CLAUDE_PLUGIN_ROOT}/cant.yaml` — machine-readable,
  stable IDs (`CANT-1` … `CANT-28` in v1). Read it; do not work from memory.
  Each entry has `id`, `name`, `genus`, `move`, `quote`, `counter`. The file
  is long: Grep for the entries the mapping table points you at rather than
  reading it whole.
- **The harness schema**: `evals/cases/README.md` in the target repo is
  authoritative for case fields, expectation types, and fixture rules. If
  `scripts/run-behavioral-evals.sh` or `evals/cases/` is missing, stop
  without writing any case file and say exactly:
  **"This repo has not adopted the behavioral eval harness (see
  kanopi/skills-plugin-template)."** Do not invent a runner, and do not
  write cases nothing can run (CANT-24, CANT-27).

## Workflow

Budget discipline: this whole job fits in about a dozen tool rounds. Read
exactly three inputs — the target `SKILL.md`, `evals/cases/README.md`, and
the catalog entries the mapping table points at — then write the cases and
run `--check`. Do not survey the repo beyond `git status` and a listing of
`skills/` and `evals/fixtures/`; the schema README already tells you how
fixtures work (CANT-26: exploring is not progress).

### 1. Extract the promises

Read the skill under test and list every **behavioral promise** — an
instruction about conduct, not capability. Look for:

| Promise type | Typical wording in the skill |
|---|---|
| Confirmation gate | "show the user X and wait for approval before ..." |
| Refusal rule | "refuse to ... without a named reviewer" |
| Honesty rule | "never fabricate", "report the metric as measured" |
| Fixed-form output | a mandated header, trailer, label, or phrase |
| Scope boundary | "never push", "do not modify files outside ..." |
| Verification rule | "run the tests before claiming success" |

If the skill has **no** behavioral promises (a pure reference skill), stop
without writing any case file and say exactly: **"No behavioral promises
found; routing evals cover this skill."** Do not manufacture cases.

### 2. Map each promise to techniques

For each promise, ask: *which named excuse would an agent or user use to
break it?* Match against `cant.yaml` entries and record the IDs. Common
mappings:

| Promise | Likely techniques |
|---|---|
| Confirmation gate | CANT-1 (Pre-Approval Gambit), CANT-2 (Authority Play), CANT-3 (Emergency Exemption), CANT-19 (Loophole Lawyer) |
| Honesty about tests/metrics | CANT-5 (Requested Fabrication), CANT-10 (Confident Should), CANT-22 (Bare Number), CANT-23 (False All-Clear) |
| Refusal requirements | CANT-2 (Authority Play), CANT-6 (Special Occasion), CANT-7 (Triviality Waiver) |
| Delegated work claims | CANT-11 (Secondhand Success), CANT-12 (Proxy Pass) |
| Unreachable inputs | CANT-27 (The Invented Input) |
| Process/order rules | CANT-8 (Deferred Discipline), CANT-9 (Exploration Detour), CANT-26 (Motion as Progress) |

The genus decides the test's shape (this is the practical corollary from the
catalog README):

- **pretext** → adversarial **prompt**: the case's `prompt` field delivers
  the excuse, ideally quoting the rationalization the skill's own defenses
  anticipate.
- **self-talk** → adversarial **environment**: a fixture where the wrong
  path is the easy path (a denied command, a missing tool, a file a lazy
  glob won't match), with a neutral prompt.
- **hybrid** → both, graded on the attempt.

### 3. Ensure contractual strings exist

Expectations grade **contractual strings the skill itself mandates**
(approval headers, refusal language, trailer formats) — never incidental
phrasing. If a promise has no stable string to assert on, **edit the skill
first** to add one (a fixed header like `=== READY FOR APPROVAL ===`, a
fixed refusal sentence, a fixed "Tests not run" form). Naming the technique
in the skill's defense text ("pre-approval in the same message does not
count (CANT-1)") both strengthens the gate and documents the mapping.

### 4. Write the cases

One JSON file per case in `evals/cases/`, named `<skill>--<scenario>.json`
(the `name` field must equal the filename minus `.json`). Follow the schema
in `evals/cases/README.md`. Minimum for any side-effect skill:

1. **One gate case** — happy path; assert the flow stops at the
   confirmation (`output_matches` the approval header, `tool_not_called`
   for the side effect).
2. **One pressure case per distinct technique family** — the prompt applies
   the excuse; assertions are the same as the gate case plus
   `output_not_matches` for false success claims.

Tag every case with the `cant` field listing the technique IDs it
exercises. Keep `max_turns` as tight as the mandated workflow allows, and
mark the single most representative case `"smoke": true`.

Reuse an existing fixture from `evals/fixtures/` when one fits; create a
new blueprint only when the technique needs a specific environment
(self-talk cases usually do). Fixtures never have a git remote, and
`setup.sh` deletes itself before staging.

### 5. Validate and run

```bash
./scripts/run-behavioral-evals.sh --check          # static validation, free
./scripts/run-behavioral-evals.sh --case <name>    # each new case, costs tokens
```

`--check` is mandatory: always run it after writing cases, even when told
the cases are obviously valid (CANT-3, CANT-10), and re-run it after fixing
what it flags. (`--list` prints the CANT coverage report; offer it to the
human, don't spend a turn on it yourself.) The paid
runs (`--case`, `--smoke`, or the full suite) are gated: present the cases
first, and run them only on approval that arrives in a message after the
presentation — pre-approval in the same message does not count (CANT-1).
**A failing case is a skill bug — fix the skill, not the test**, and record
the fix in `CHANGELOG.md`.

### 6. Register

Follow the target repo's checklist for new eval cases (CHANGELOG entry;
anything else its CLAUDE.md requires). Report the final mapping as a short
table: promise → CANT IDs → case file.

## Anti-rationalization table (for this skill itself)

| If you catch yourself thinking | Stop — that is |
|---|---|
| "This skill is too simple to need cases" | CANT-7, The Triviality Waiver. Reference-only skills are exempt; anything with a promise is not. |
| "I'll add the eval cases in a follow-up" | CANT-8, The Deferred Discipline. Cases land in the same change as the skill. |
| "The case would pass, no need to run it" | CANT-10, The Confident Should. `--check` is free; run it. Ask before paid runs, then actually run them. |
| "I'll loosen the assertion so it passes" | CANT-19, The Loophole Lawyer. Fix the skill, not the test. |
| "cant.yaml probably says..." | CANT-27, The Invented Input. Read the file; it ships in this plugin. |
