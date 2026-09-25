# Weekly GitHub development summary

An importable n8n workflow that reports a repository's activity over the previous seven days: commits, closed issues (excluding pull requests), and merged pull requests. It uses public GitHub REST endpoints and asks Claude Code to write the summary in English or French. Discord and Slack incoming webhooks are supported.

## Setup and run

1. Use Node.js 24 or later, install a self-hosted n8n version that supports the Execute Command node, and install Claude Code on the same machine. This workflow has been exercised with n8n 2.40.7 and Node.js 26.9.0.
2. Sign in to Claude Code on that machine, then confirm `claude --model claude-sonnet-4-6 -p "Reply with READY" --tools '' --no-session-persistence --max-turns 1` works. The workflow removes API-key variables before invoking the CLI; it uses the local Claude Code sign-in and its applicable subscription/quota.
3. On a private, single-user n8n host, enable Execute Command while keeping the local file trigger excluded. For example, set `NODES_EXCLUDE=["n8n-nodes-base.localFileTrigger"]` in the n8n process environment. Do not expose an instance with host-shell workflows to untrusted users. n8n Cloud does not provide Execute Command.
4. Import `solutions/weekly-dev-summary/workflow.json`. In **Set Options**, set `repo` to `owner/repository`, choose `en` or `fr`, set `destinationType` to `discord` or `slack`, and paste the matching incoming webhook URL. Keep `sendDelivery` false while reviewing the first manual run.
5. Run **Run Manually** and review the generated summary. When ready, set `sendDelivery` true and activate the workflow. It runs Friday at 17:00 UTC; Discord uses `content`, Slack uses `text`.

The starter webhook is a placeholder and delivery is off by default. Each GitHub request currently reads one page (up to 100 records); repositories with more than 100 weekly records in a category need pagination before relying on totals. GitHub's unauthenticated API rate limit applies.

The bounty originally specified `claude-sonnet-4-20250514`. Anthropic retired that model on 2026-06-15 and recommends `claude-sonnet-4-6`; this workflow uses that supported successor and does not claim to run the retired model. See [Anthropic's model deprecation notice](https://platform.claude.com/docs/en/about-claude/model-deprecations).

## Local checks

```sh
cd solutions/weekly-dev-summary
npm test
npm run build:workflow
```

`npm test` validates date filtering, exclusion of closed-but-unmerged PRs, prompt bounds, webhook host checks, and default-off delivery. The workflow JSON is self-contained; the small build script embeds the reviewed Code node sources into it.
