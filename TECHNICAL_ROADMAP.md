# Technical Roadmap

This roadmap replaces the earlier "embedded runtime mirror inside the skill"
direction with a cleaner separation:

- the skill becomes a prompt-first package with lightweight helper scripts
- the CLI becomes an independent application entrypoint
- shared Python code lives in reusable core modules instead of inside the skill

The target is to stop treating the skill as a bundled executable runtime while
still preserving the useful shared logic for text preparation, storage,
prompting, parsing, and result shaping.

## Architectural Direction

Target boundaries:

- `skill`
  - `SKILL.md`
  - prompts and reference docs
  - lightweight helper scripts such as text loading, chunking, transcoding,
    excerpt preparation, and output shaping
- `cli`
  - argparse / subcommands
  - interactive session UX
  - local developer workflow and standalone automation
- `shared core`
  - config and contracts that are not CLI-specific
  - text loading / parsing / chunking
  - prompt assembly helpers
  - persona / relation storage helpers
  - result parsing and post-processing
  - host LLM adaptation

Non-target:

- the skill should not permanently carry a mirrored CLI runtime as its primary
  execution model

## P0: Reset The Boundary

Status: completed

Goals:
- Replace the old roadmap assumptions before more code accumulates on them.
- Document the new skill / CLI / shared-core split clearly.
- Mark the embedded runtime path as transitional rather than strategic.

Tasks:
1. Rewrite the roadmap around prompt-first skill packaging.
2. Update packaging language so "skill = packaged runtime" is no longer the
   long-term story.
3. Add the first lightweight skill helper script that does useful preprocessing
   without depending on the CLI shell.
4. Start carving out shared helper modules for skill-side utilities.

## P1: Extract Skill Helpers From CLI Assumptions

Status: completed

Goals:
- Let the skill call prompts plus helper scripts directly.
- Move preprocessing responsibilities out of the embedded runtime mindset.

Tasks:
1. Create a dedicated shared helper area for novel text loading, decoding,
   sentence splitting, chunking, and excerpt preparation.
2. Ship those helpers inside the skill as standalone scripts the host can call
   directly.
3. Add helper scripts for:
   - loading and transcoding raw novel text
   - building prompt-sized excerpts
   - normalizing output file names and directories
   - exporting compact structured payloads for prompts
4. Keep helper scripts stateless and file-oriented so hosts can compose them
   without importing the CLI.
5. Add focused tests for helper behavior on Chinese text, encoding edge cases,
   and excerpt boundaries.

## P2: Shrink The Skill Package

Status: completed

Goals:
- Remove the skill's dependency on a bundled CLI runtime.
- Keep only prompt assets, references, examples, and helper scripts.

Tasks:
1. Stop documenting `runtime/zaomeng_cli.py` as the preferred skill execution
   path.
2. Remove runtime-mirror assumptions from packaging docs and tests.
3. Replace runtime-oriented manifest entries with prompt/helper-oriented ones.
4. Move any still-useful runtime utilities into shared core or skill helpers.
5. Remove runtime mirror tooling after the skill package no longer ships a
   bundled runtime.

## P3: Make CLI A Standalone Product Layer

Status: completed

Goals:
- Let the CLI evolve independently from the skill package.
- Keep its UX, subcommands, and local automation without forcing those concerns
  into the skill bundle.

Tasks:
1. Move argparse entrypoints and session-oriented orchestration behind a
   dedicated CLI layer.
2. Keep interactive chat/session UX as CLI-only behavior.
3. Make the CLI consume shared prompts/helpers/core modules rather than owning
   duplicated logic.
4. Split CLI packaging, docs, and tests from skill packaging checks.

## P4: Consolidate Shared Core

Status: completed

Goals:
- Reuse domain logic without coupling it to either the skill shell or the CLI
  shell.
- Keep the genuinely reusable pieces in one place.

Tasks:
1. Separate CLI-only modules from reusable core modules.
2. Keep host LLM integration in shared core so both CLI and host-driven skill
   flows can reuse it.
3. Centralize prompt assembly, output parsing, storage helpers, and relation
   rendering helpers.
4. Continue improving contracts for sessions, relations, visualization, and
   persistence only where they remain useful outside the CLI.

## P5: Quality And Reliability

Status: completed

Goals:
- Preserve current behavior quality while the architecture shifts.
- Keep regressions visible as responsibilities move.

Tasks:
1. Expand regression coverage for:
   - text decoding
   - excerpt preparation
   - profile completeness
   - cross-character differentiation
   - relation extraction quality
   - persona fidelity in chat
2. Keep LLM availability as a hard prerequisite for real generation flows.
3. Continue reducing authored fallback prose and keep rules structural.
4. Validate that skill docs, release docs, and packaging docs all describe the
   same architecture.

## Non-Goals For Now

- No heavy DI framework.
- No Git submodule split.
- No plugin system redesign in this phase.
- No service-style metrics stack while the project is still CLI/skill oriented.
