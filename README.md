# Reus File Utils

## Development and versioning

Install development dependencies with `uv sync --dev`. Use Conventional Commits;
`uv run cz commit` provides an interactive commit prompt.

Commitizen reads the project version from `pyproject.toml` and updates both that
file and `uv.lock` using its
[uv version provider](https://commitizen-tools.github.io/commitizen/config/version_provider/#uv).
Tags use `v<version>`. Preview the next bump with `uv run cz bump --dry-run --yes`.

The **Bump version** GitHub Actions workflow runs on pushes to `main` and can also
be dispatched manually on `main`. It determines the increment from commit history,
creates a version commit and tag, and pushes them together. Runs without eligible
changes succeed without creating a release. The `v2` development branch is not
automatically versioned.

Before the first version tag exists, Commitizen considers the full commit history;
the legacy `beta` tag does not serve as a `v<version>` baseline. Subsequent bumps
consider changes since the current version tag.

The workflow uses the built-in `GITHUB_TOKEN` with `contents: write`. Repository
rules must permit its version commit and tag pushes. It does not publish packages
or create GitHub Releases. Pushes made with this token do not trigger subsequent
push-based workflows; add release steps explicitly if needed later.
