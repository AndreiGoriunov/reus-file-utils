# Reus File Utils — rewrite plan

## 1. Goal and repository baseline

Build a cross-platform collection of file utilities with equally supported CLI and PySide6 GUI interfaces. Each utility
produces a reviewable plan; a shared execution layer performs approved filesystem changes and reports individual
outcomes.

This is a ground-up rewrite. `legacy/` is reference material for intended workflows and useful examples, not an
implementation to migrate line by line or import into the new package.

Current repository context:

- The distribution is `reus-file-utils`; the package is `src/reus_file_utils`. Keep these names instead of introducing a
  media-specific top-level package.
- `pyproject.toml` requires Python `>=3.14,<3.15`, uses `uv_build`, and declares Dynaconf, PySide6, and PyYAML. The
  existing `reus-file-utils` entry point currently prints a greeting.
- `.python-version` selects Python 3.14. Use `uv` for environments, dependency management, and the lockfile.
- `README.md` is currently empty; no rewrite tests or application layers exist yet.
- Legacy code includes an extension-based folder organizer, mapping-based filename transliteration, an unfinished
  empty-directory utility, and PySimpleGUI/Tkinter UI experiments.
- `resources/` contains a nested organizer YAML profile and three transliteration maps. Review and validate these as
  candidate data fixtures; their presence does not make their behavior authoritative.
- Follow `AGENTS.md`: modern Python 3.14 typing, uv, Dynaconf, PySide6, Ruff, and pytest. Preserve unrelated
  working-tree changes during implementation.

## 2. Scope and delivery order

The proposed first release contains three offline utilities in both interfaces:

| Utility                  | Initial behavior                                                                       |
|--------------------------|----------------------------------------------------------------------------------------|
| Folder organizer         | Move files into profile-defined categories using normalized extension matching.        |
| Filename transliteration | Rename file stems using a selected, validated mapping; preserve extensions by default. |
| Empty-directory cleanup  | Remove selected empty directories bottom-up, retaining the selected root.              |

Media renaming is the next feature milestone. Preserve the useful parser, metadata, resolution, and naming ideas from
the earlier plan inside a dedicated utility, without making every utility depend on media concepts or network services.

Initial exclusions: recursive directory renaming, file-content deletion, overwrite/merge modes, cross-volume moves,
automatic undo, arbitrary plugin loading, filesystem watching, cloud synchronization, and offline translation models.
Recursion for file discovery is explicit and off by default. These boundaries can be revisited after the common
execution model is proven.

## 3. Architecture and dependency rules

Use a small shared domain and application layer, with feature-specific planning and thin interface adapters. Start with
concrete utilities registered explicitly in a composition root; avoid designing a third-party plugin framework.

```text
src/reus_file_utils/
├── __init__.py
├── __main__.py
├── bootstrap.py                 # composition and dependency wiring
├── domain/
│   ├── operations.py            # immutable filesystem intents and plans
│   ├── results.py               # issues, outcomes, progress events
│   └── errors.py
├── application/
│   ├── services.py              # discover, preview, approve, execute
│   ├── ports.py                 # filesystem/progress/cancellation contracts
│   └── registry.py              # built-in utility descriptors
├── filesystem/
│   ├── discovery.py
│   ├── paths.py                 # validation and collision policy
│   ├── executor.py
│   └── journal.py
├── utilities/
│   ├── organize/               # options, profile schema, planner
│   ├── transliterate/          # options, map schema, transformer, planner
│   ├── empty_dirs/             # options and planner
│   └── media/                  # later milestone
│       ├── models.py
│       ├── parsing.py
│       ├── resolution.py
│       ├── naming.py
│       ├── planner.py
│       └── metadata/           # provider Protocol and TMDB adapter
├── config/
│   ├── loader.py
│   └── models.py
├── resources/                  # validated bundled profiles and maps
├── cli/
│   ├── app.py
│   └── rendering.py
└── gui/
    ├── app.py
    ├── main_window.py
    ├── models/
    ├── pages/
    └── workers/

tests/
├── unit/
├── integration/
├── cli/
├── gui/
└── fixtures/
```

This is a target structure, not a requirement to create empty modules in advance. Split files when actual
responsibilities justify it.

Dependencies flow from CLI/GUI to application services, then to utility planners and shared domain contracts. Filesystem
and external-service adapters implement the required contracts and are injected at startup. Utility planners consume
discovered snapshots rather than performing mutations.

- No PySide6 imports in domain, application, utility, filesystem, or configuration code.
- No console input, printing, dialogs, or GUI event loops in shared services.
- No imports from `legacy/` in production code or new tests.
- Utilities share filesystem mechanics; organizer and cleanup code know nothing about metadata providers or title
  confidence.
- CLI startup must work without importing Qt or requiring a display server.
- Use `Protocol` at replaceable boundaries, frozen/slotted dataclasses for values, `StrEnum` for stable states,
  `pathlib.Path`, `type` aliases, and Python 3.14 generic syntax where useful. Avoid untyped dictionaries crossing
  application boundaries.

## 4. Shared planning and execution model

```text
Utility options + discovered entries
                 ↓
       Feature-specific proposals
                 ↓
      Validated immutable OperationPlan
                 ↓
   Explicit selection and plan approval
                 ↓
     Revalidation → filesystem execution
                 ↓
       Per-operation ExecutionReport
```

Core models:

| Model                                                               | Responsibility                                                                                         |
|---------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| `FileSnapshot`                                                      | Source path, entry kind, and available identity/stat information used to detect changes since preview. |
| `RenameFile`, `MoveFile`, `CreateDirectory`, `RemoveEmptyDirectory` | Distinct immutable operation variants with IDs, required paths, preconditions, and dependencies.       |
| `PlanIssue`                                                         | Stable issue code, severity, affected operation, and human-readable explanation.                       |
| `OperationPlan`                                                     | Plan ID/schema version, utility/options snapshot, roots, ordered operations, dependencies, and issues. |
| `PlanApproval`                                                      | Exact plan revision and explicitly selected operation IDs; approval is separate from the plan.         |
| `OperationResult`                                                   | Succeeded, failed, skipped, or cancelled outcome with paths and structured error details.              |
| `ExecutionReport`                                                   | All operation outcomes and aggregate counts, including operations never started.                       |

Keep utility details in feature-specific preview data associated with operation IDs. A cleanup row should not need
`ParsedMedia` or `TitleResolution` fields. Editing options, targets, or media selections regenerates validation and
invalidates previous approval.

Planning performs no mutation of the selected filesystem tree. Scanning and metadata lookup can involve I/O, but
directory creation, renaming, moving, and removal occur only during execution. Diagnostic logs or metadata caches live
outside the selected tree.

### Execution guarantees and limits

- Default to no overwrites. Detect occupied targets and duplicate planned targets before approval, then revalidate
  immediately before mutation.
- Do not describe an existence check followed by plain `rename` as race-safe: platform behavior differs. Implement and
  test a platform adapter with no-replace semantics for supported file moves; fail closed when that guarantee is
  unavailable. Do not silently fall back to an overwriting operation.
- Snapshot checks detect ordinary stale plans, not every possible concurrent filesystem change. Document this limit and
  use stronger identity/handle checks where supported.
- Keep initial renames within a directory and organizer moves within the selected root and filesystem. Detect
  cross-device failures without falling back to copy/delete.
- Explicitly plan destination-directory creation. If a prerequisite fails or is deselected, dependent operations cannot
  run.
- Block rename cycles, swaps, and case-only renames initially with an actionable issue. A later staged-rename design
  needs its own recovery semantics.
- Execute deterministically and serially first. Continue independent operations after an individual failure; stop
  dependent operations and stop the batch for systemic failures such as an unusable journal.
- Cancellation stops between filesystem actions. It does not interrupt an action midway or reverse completed operations.
- Write a journal entry before an action and its outcome afterward. Include plan/operation IDs and source/target paths.
  A crash between those records produces an uncertain outcome requiring inspection, not an automatic retry.
- Retain partial success and report it clearly. Journaling supports diagnosis and later recovery work; it does not imply
  transactional batches or guaranteed undo.

## 5. Filesystem and cross-platform policy

Target Windows, macOS, and Linux from the first vertical slice, with native integration tests for behavior that cannot
be simulated reliably.

- Discovery is deterministic, handles inaccessible entries as issues, and deduplicates overlapping input selections.
- Do not follow symlinks, Windows junctions, or other directory reparse points initially. Reject unsupported source
  entry types and avoid crossing mount boundaries during recursive discovery.
- Preserve the selected root during cleanup. Treat hidden/system entries as real contents when deciding whether a
  directory is empty.
- Track output directories so recursive organization does not repeatedly process files already categorized or move them
  into nested copies of the same category.
- Validate profile destinations as relative paths contained within the selected root. Reject absolute destinations,
  traversal, and destinations escaping through links.
- Separate platform validity from an optional portable filename policy. Validate Windows reserved names, forbidden
  characters, trailing dots/spaces, empty names, and applicable component/path limits. Show sanitization in preview;
  never truncate silently.
- Do not infer filesystem case sensitivity solely from the operating system. Use a conservative collision policy when
  capabilities are unknown, including case and Unicode normalization equivalence. Preserve original spelling unless
  transformation is requested.
- Path length checks are advisory where filesystem limits cannot be determined; actual OS errors remain structured
  execution failures.
- Surface network shares and unusual filesystems as capability-dependent. Unsupported guarantees must block execution
  rather than silently weaken the policy.

## 6. Offline utility behavior

### Folder organizer

Convert the existing nested YAML example into a documented, versioned profile schema. Normalize extension notation
consistently (`jpg` and `.jpg`), support nested categories, and define longest-suffix matching for compound extensions.
Reject ambiguous rules instead of relying on YAML order.

Scan each input directory once. Unmatched files stay in place. Files already at their intended destination become
no-ops. Preserve extension spelling by default; lowercasing is an explicit option rather than inherited legacy behavior.

Default collisions to blocked proposals. An optional suffix policy may generate deterministic alternate names during
planning, reserving every proposed target across the batch. Revalidation must fail a now-occupied target rather than
silently choosing a new name after approval.

### Filename transliteration

Load maps with safe YAML parsing and validate keys, values, duplicate keys, empty keys, and output filename validity.
Treat existing maps as named user-selectable profiles; do not assume they are linguistically interchangeable or correct
merely because a filename names a standard.

Use a deterministic single pass with longest-key matching so multi-character sequences win and replacement text is not
transformed again. Define case handling explicitly. Preserve unmatched characters, meaningful punctuation, and
extensions by default. Any output collision follows the shared planner rules.

### Empty-directory cleanup

Plan bottom-up removals. A parent is eligible only when it is already empty or all its contents are child directories
included in successful planned removal dependencies. Deselection of a child invalidates the dependent parent operation.

Immediately before removal, check that the entry is still the expected directory and use an empty-directory removal
operation. Newly added contents cause a reported skip/failure; never use recursive deletion. Do not create an undo
promise for removed directory metadata.

## 7. CLI and GUI as equal interfaces

### CLI

Keep `reus-file-utils` as the console command and add a separate GUI launcher. Begin with standard-library `argparse`;
introduce a CLI dependency only for demonstrated needs.

Proposed workflow:

```text
reus-file-utils organize preview ./Downloads --profile general --save plan.json
reus-file-utils transliterate preview ./Files --map russian-to-english --save plan.json
reus-file-utils empty-dirs preview ./Files --recursive --save plan.json
reus-file-utils apply plan.json
reus-file-utils apply plan.json --yes --json
```

Preview is the default safe path. Interactive apply displays the validated plan and asks for confirmation.
Noninteractive apply requires `--yes`; it approves eligible operations only and cannot bypass blocking validation or
unresolved media review. Allow explicit operation selection consistently with the GUI.

Saved plans use a versioned JSON schema, resolved paths, source snapshots, and no secrets. Loading a plan validates its
schema, roots, destinations, dependencies, and current filesystem state; the saved file is not executable code or
permanent authorization.

Provide stable JSON output for automation, diagnostics on stderr, and documented exit codes: success, invalid
input/configuration, blocked/stale plan, partial/execution failure, and cancellation. No interactive prompts in
noninteractive mode. Ctrl+C uses the shared cancellation mechanism and preserves results already completed.

### GUI

Build a PySide6 window with utility navigation and a shared workflow: choose inputs → configure utility → preview →
select/approve → apply → inspect results.

- Use a shared table model for source, action, proposed destination, issues, selection, and result; add feature-specific
  details panels where needed.
- Include file/folder selection, recursion controls, profile/map selection, filtering, and explicit explanations for
  blocked rows.
- Run scanning, metadata requests, and execution in `QThreadPool`/`QRunnable` workers. Exchange immutable results and
  progress through signals; update widgets only on the UI thread.
- Use cancellation tokens and request IDs so stale previews cannot overwrite newer options. Serialize execution and
  prevent duplicate apply actions.
- Keep the interface responsive while cancelling or closing. Define shutdown behavior around completion of the current
  filesystem action and journal write.
- Support the same plan import/export and validation rules as the CLI. GUI selection must not bypass the application
  service.

## 8. Media renaming milestone

Implement media renaming after the offline suite exercises the shared contracts. Its internal pipeline remains:

```text
Path → ParsedMedia → TitleResolution → proposed filename → shared OperationPlan
```

- Parse in stages: extension handling, strong episode markers, plausible year extraction, title boundaries, contextual
  release-token removal, separator cleanup. Avoid deleting token strings globally or stripping ordinary hyphenated title
  suffixes.
- Preserve season and episode tuples, including multi-episode inputs. Recognize that years may be part of titles;
  unknown or ambiguous parsing remains visible.
- Define `MetadataProvider`, `Translator`, and `Transliterator` protocols within this feature. Normalize provider
  responses into immutable candidates with provider identity, media type, localized/original titles, and year.
- Implement TMDB via `httpx` only when this milestone begins. Verify endpoint parameters, localization behavior,
  credentials, rate limits, and distribution/attribution requirements against official documentation at that time.
- Score candidates using title, year, and media type; popularity is at most a tie-breaker. Expose
  high/medium/low/ambiguous categories and reasons, with a required margin over competing candidates. Calibrate
  thresholds against fixtures instead of treating decimal scores as probabilities.
- High confidence populates a proposal; it never authorizes mutation. Ambiguous matches require explicit candidate
  selection or a manual title.
- Keep network failure distinct from a valid no-match result. Use timeouts, bounded retry for transient failures,
  cancellation, and a bounded cache keyed by query/type/year/language.
- Make target language configurable, with `ru-RU` as the initial media default. Prefer an identified localized title;
  otherwise use an explicitly enabled fallback policy. Start with clean-original fallback and optional transliteration.
  A `NullTranslator` can preserve an extension point; model-based translation is deferred.
- Explain fallback provenance. Transliteration and literal translation are not evidence of an established localized
  movie title.
- Build movie names such as `Title (1994).mkv` and TV names such as `Title - S02E03-E04.mkv`. Define missing-year
  behavior explicitly and preserve noncontiguous episode sets without falsely expressing them as ranges.
- Feed all generated filenames through the shared path policy and planner. Manual edits rerun collision and filename
  validation.

Representative parser fixtures include `The.Shawshank.Redemption.1994.1080p.BluRay.x264.mkv`, `Movie Title (1994).mkv`,
`Game.of.Thrones.S02E04.1080p.mkv`, and multi-episode names. Include ambiguous titles such as `Crash`, title-internal
years, and punctuation such as `Spider-Man`.

## 9. Configuration, resources, and dependencies

Use Dynaconf at the configuration boundary and convert loaded values to validated typed settings before calling
services. Establish explicit precedence: bundled defaults → per-user settings → explicitly selected settings file →
prefixed environment variables → invocation options. Test this order rather than relying on implicit loader behavior.

Store settings, cache, and journals in platform-appropriate user directories, independent of the current working
directory. Bundle read-only defaults and reviewed YAML resources within the package using `importlib.resources`.
`platformdirs` is a proposed small dependency for path discovery; confirm it during the bootstrap milestone.

YAML is for organizer profiles and transliteration maps; application settings use TOML. Define schema versions and
reject malformed configuration with actionable errors. No Python object construction or executable expressions in
profiles.

Retain the current Python 3.14 constraint and `uv_build`. Plan dependency changes explicitly:

| Area             | Policy                                                                                                                        |
|------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Shared runtime   | Dynaconf, PyYAML, and platform directory support.                                                                             |
| GUI              | PySide6; move to a `gui` extra once headless CLI installation is verified. Desktop builds include it.                         |
| Media networking | Add `httpx` with the media feature, not to enable the offline utilities.                                                      |
| Development      | Ruff and pytest first; add coverage, HTTP mocking, and Qt testing tools where corresponding tests need them.                  |
| Packaging        | Evaluate PyInstaller as a build dependency against the chosen Python/PySide6 versions before committing to release artifacts. |

Configure Ruff for Python 3.14 and exclude legacy/reference code from rewrite checks. Scope pytest to `tests/`. A static
type checker is a later tooling decision, not a reason to weaken type annotations now.

Do not bundle TMDB secrets. Prefer user-provided credentials via environment or per-user secret configuration, redact
them from errors/logs, and exclude them from exported plans. Credential distribution policy must be settled before
shipping media functionality.

## 10. Verification and release strategy

Use pytest temporary directories for real filesystem integration tests and injected adapters for controlled failures.
Keep unit tests focused on parsing, transformation, validation, and other meaningful behavior. Mock remote services;
normal tests must not depend on live credentials or the network.

Required coverage includes:

- Preview leaves selected trees unchanged; unapproved or invalid operations never execute.
- Duplicate targets, occupied destinations, unsupported case-only changes, and Unicode/case collisions are blocked.
- Sources or targets changed after preview are detected; no-replace behavior survives a competing target creation.
- Dependency failures, partial success, cancellation, unavailable journals, and interrupted journal records produce
  understandable reports.
- Organizer precedence, nested categories, compound extensions, malformed/traversing profiles, repeat runs, and output
  exclusion.
- Transliteration overlapping keys, non-cascading replacements, unchanged names, preserved extensions, and many-to-one
  collisions.
- Empty-directory dependency ordering, root retention, new contents after preview, hidden contents, inaccessible
  entries, and link exclusion.
- CLI/GUI service parity, JSON schema/exit codes, noninteractive behavior, GUI responsiveness, and stale-worker-result
  rejection.
- Native filesystem edge cases on Windows, macOS, and Linux; packaging/resource loading outside the source checkout.

CI should run locked uv installs, `ruff check`, `ruff format --check`, and pytest on all three target OSes using Python
3.14. GUI checks may require platform-specific display setup; retain native desktop smoke tests rather than assuming
headless tests prove packaging works.

Build wheels and source distributions first. Verify that `legacy/`, development secrets, and repository-only resources
are excluded while packaged profiles/maps are included. Test the CLI in a clean environment and GUI bundles on clean
target systems without Python installed.

Prototype PyInstaller directory bundles separately on each target OS. Validate Python 3.14, PySide6, Qt plugins,
architecture, licensing notices, and resource discovery early. One-file bundles, signing/notarization, installers, and
automatic updates are separate decisions after directory bundles pass smoke tests. Do not assume one platform's artifact
runs on another.

## 11. Implementation milestones and acceptance gates

| Milestone                   | Deliverable                                                                                                                                  | Completion gate                                                                                                                                          |
|-----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0. Bootstrap                | Confirm scope; document legacy observations; configure uv/Ruff/pytest; typed settings; CLI and GUI launchers; packaging compatibility spike. | Python 3.14 environment works; CLI launches headlessly; minimal GUI starts; initial CI passes; packaging blockers recorded.                              |
| 1. Shared safety foundation | Snapshots, operation variants, planner validation, approval, executor, journal, cancellation, and saved-plan schema.                         | Tests demonstrate no mutation during preview, no overwrite, approval enforcement, stale-plan handling, and partial-result reporting on native platforms. |
| 2. Organizer vertical slice | Validated bundled profile, organizer planner, CLI preview/apply, and minimal shared GUI preview/apply.                                       | Same fixture produces equivalent plans and outcomes through both interfaces; nested categories and collisions behave predictably.                        |
| 3. Offline utility suite    | Transliteration and empty-directory cleanup using shared execution and both adapters.                                                        | Map edge cases and bottom-up cleanup pass integration tests; root/link protections hold; all three tools support review and cancellation.                |
| 4. Offline release          | User configuration, help/README, packaged data, CI matrix, installable package and desktop artifacts.                                        | Fresh installs work outside checkout; all supported OS smoke tests pass; limitations and journal locations are documented.                               |
| 5. Media core               | Deterministic parser, naming, manual title workflow, and shared rename proposals.                                                            | Parser/naming fixtures pass without network or Qt; media proposals obey existing safety rules in both interfaces.                                        |
| 6. Media metadata           | TMDB adapter, scoring, cache, fallback provenance, candidate review UI/CLI.                                                                  | Mocked provider tests cover ambiguity and failures; unresolved matches cannot be applied; credentials and distribution requirements are documented.      |
| 7. Later extensions         | Consider translation models, safe staged renames, recovery tooling, cross-volume moves, or additional utilities individually.                | Each extension has explicit semantics and tests; no relaxation of existing guarantees by accident.                                                       |

## 12. Decisions to validate during implementation

The plan can proceed with the defaults above. Resolve these at the indicated milestones rather than blocking the initial
scaffold:

1. **Bootstrap:** supported OS versions and CPU architectures; exact Python 3.14/PySide6 packaging compatibility; GUI
   extra installation workflow.
2. **Safety foundation:** native no-replace implementations and supported filesystems; saved-plan lifetime and journal
   retention; portable-name policy defaults.
3. **Offline utilities:** which existing maps to ship after review, desired compound-extension conventions, and whether
   automatic collision suffixing belongs in the first release.
4. **Release:** distribution channels, signing/notarization, support expectations for network shares, and user-facing
   recovery documentation.
5. **Media milestone:** TMDB credential ownership and attribution, language defaults, calibrated confidence thresholds,
   and whether transliteration fallback should be enabled by default.

The rewrite is successful when another utility can supply options and a planner, reuse validation/execution/reporting,
and appear in both interfaces without duplicating filesystem mutation logic.
