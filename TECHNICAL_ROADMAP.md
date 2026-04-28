# Technical Roadmap

This roadmap turns the current improvement ideas into a staged refactor plan.
The goal is to reduce maintenance risk first, then improve reliability and
extensibility without forcing a large rewrite in one pass.

## P0: Stabilize The Current Architecture

Status: completed

Goals:
- Stop `src/` and `clawhub-zaomeng-skill/runtime/src/` from drifting.
- Add guardrails before larger refactors.
- Keep current behavior and CLI flow stable.

Tasks:
1. Add a runtime mirror consistency check.
2. Keep mirror validation in the test suite.
3. Document the consolidation path before moving files.
4. Replace broad internal `print` usage with structured logging where output is
   not part of the CLI UX.
5. Introduce project-level exception types for config, LLM, profile loading,
   and visualization failures.
6. Replace broad mirror globs with an explicit runtime mirror file manifest.
7. Move runtime wrapper files out of the mirror set so only shared business
   modules remain under sync control.

## P1: Consolidate Shared Code

Status: in progress

Goals:
- Remove double maintenance across `src/` and runtime.
- Centralize core services and domain logic.

Tasks:
1. Extract shared Python code into a single package directory.
2. Keep runtime as a thin wrapper around the shared package.
3. Define repository-style interfaces for profiles, sessions, relations, and
   visualization exporters.
4. Normalize construction through a single runtime factory.
5. Align packaging docs and manifests with the shared-implementation / thin-wrapper split.
6. Keep local developer checks and CI pointed at the same `scripts/dev_checks.py` entrypoint.
7. Standardize core module construction around `RuntimeParts` helper constructors before considering a DI framework.
8. Make `RuntimeParts` the lazy composition root for reflection, distillation, speaker, extractor, and chat engine creation.
9. Reuse foundational runtime dependencies through `RuntimeParts.fork()` so CLI and tools do not rebuild the base graph from scratch.
10. Support incremental dependency overrides on top of forked runtime parts so tests and alternate entrypoints can swap only the pieces they need.
11. Synchronize runtime-owned wrapper files through the same mirror tooling so the compatibility layer stays mechanical instead of hand-maintained.
12. Drive wrapper guardrails from the runtime-owned manifest entries so source/runtime wrapper pairs stay aligned without duplicate test lists.
13. Derive runtime layer documentation checks from the mirror manifest so packaging docs and wrapper docs drift less easily.
14. Keep `include` and `runtime_owned` under the same default mirror/report path so wrapper drift is caught by the standard runtime sync flow.
15. Extract markdown-backed session and relation stores behind repository-style interfaces so chat and relation extraction stop persisting those assets directly.
16. Route relation graph visualization export through an injected exporter so extraction and rendering can evolve independently.

## P2: Reliability And Developer Experience

Status: in progress

Goals:
- Make failures easier to diagnose.
- Reduce accidental regressions.

Tasks:
1. Improve type coverage and enable `mypy`.
2. Add targeted retries for LLM requests with exponential backoff.
3. Add lightweight read-through caching for config, rules, and profile bundles.
4. Expand unit coverage and wire automated test execution into CI.

## P3: Scale-Oriented Enhancements

Status: planned

Goals:
- Prepare for larger novels and longer-running runtime usage.

Tasks:
1. Add chunk-level parallelism for safe high-cost processing stages.
2. Introduce streaming or incremental parsing for very large inputs.
3. Add optional hot-reload for config and rule files after caching is stable.
4. Expose metrics only if the project moves toward a long-running service mode.

## Non-Goals For Now

- No Git submodule split.
- No heavy dependency injection framework.
- No full plugin platform in the current phase.
- No Prometheus integration until service-style deployment becomes a real need.
