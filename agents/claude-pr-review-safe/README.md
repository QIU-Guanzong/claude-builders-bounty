# Claude PR Review

A small CLI that reads a public GitHub pull request diff and asks Claude Code for a structured review comment. It prints the comment for review; posting is a separate, explicit `--post` action that shows the exact text and requires an interactive `y` confirmation.

## Install

Requirements: Python 3.10+, GitHub CLI (`gh`) only if you want to post, and an installed, authenticated Claude Code CLI.

```sh
cd agents/claude-pr-review-safe
python -m pip install .
```

The package has no Python runtime dependencies. Claude Code uses the user's existing sign-in. API calls are bounded by a default `$0.50` ceiling; change it with `--budget-usd`. Subscription quotas may apply separately.

## Review a pull request

```sh
claude-review --pr https://github.com/owner/repo/pull/123
```

The output contains a two- or three-sentence summary, risks with severity and changed-file locations, improvement suggestions, and a Low / Medium / High confidence rating. To save machine-readable output:

```sh
claude-review --pr https://github.com/owner/repo/pull/123 --format json
```

The command accepts public `github.com` pull requests only. It rejects oversized diffs instead of silently reviewing a partial patch. The default limit is 256,000 bytes; `--max-diff-bytes` changes it. No private repository, PR discussion, checks, or customer data is fetched.

## Post a comment

Review the printed text first, then opt in:

```sh
claude-review --pr https://github.com/owner/repo/pull/123 --post
```

The command asks for confirmation in the terminal before using the existing `gh` sign-in to post one issue comment. It refuses to post in a non-interactive run. It does not add a GitHub Action or post comments automatically.

## Guardrails

- Claude Code runs in a temporary directory, receives only the PR URL and diff, has no tools or MCP servers enabled, and does not persist a session.
- The diff is treated as untrusted input. Claude is told to ignore instructions embedded in code and to report only findings supported by changed lines.
- Claude Code's structured-output schema is checked again locally before Markdown is rendered.
- The model cannot read files, execute commands, change code, or post anything. GitHub posting is handled separately through `gh` and requires the explicit confirmation above.
- A review is advisory. Its confidence label describes coverage of the supplied diff; it is not a test result or a merge recommendation.

## Development checks

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
```

The public PR examples under `samples/` were reviewed from [PR #4455](https://github.com/claude-builders-bounty/claude-builders-bounty/pull/4455) and [PR #4442](https://github.com/claude-builders-bounty/claude-builders-bounty/pull/4442). They are diff-only illustrations, not Claude-generated output. In this checkout, the CLI boundary was exercised against those live diffs with a stub Claude Code process because no Claude Code account was signed in.
