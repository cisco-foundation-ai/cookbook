# Antares Quickstart Guide

Run a focused Antares investigation, inspect its JSON report, and expand to a
small repository-aware sweep. Once your inference connection is available, this
guide should take about 10–15 minutes, excluding endpoint cold starts.

The [Antares model collection](https://huggingface.co/collections/fdtn-ai/antares)
contains two vulnerability-localization models:
[Antares-350M](https://huggingface.co/fdtn-ai/antares-350m) and
[Antares-1B](https://huggingface.co/fdtn-ai/antares-1b). This guide focuses on
Antares-1B.

Antares performs model-assisted, file-level vulnerability localization. The
CLI displays candidate repository-relative file paths and associated Common
Weakness Enumeration (CWE) IDs in a terminal summary, and saves the full
results as `report.json`, `report.md`, and `report.sarif`.

## What you will do

1. Install and configure the Antares CLI.
2. Preview a bounded set of repository-relevant CWE checks locally.
3. Run one focused CWE query.
4. Review the saved `report.json` and verify candidates against source.
5. Run a small automatic sweep.

## Before you start

You need:

- macOS or Linux;
- Python 3.11 or later;
- [`uv`](https://docs.astral.sh/uv/);
- `unzip`;
- access to the gated
  [`fdtn-ai/antares-1b`](https://huggingface.co/fdtn-ai/antares-1b/tree/main)
  repository and its downloaded `assets/antares-cli.zip` file;
- access to your configured Python package index, unless the CLI's dependencies
  are already available in a `uv` cache;
- a streaming OpenAI-compatible inference endpoint implementing
  `POST /v1/completions`;
- the exact model ID served by that endpoint;
- a bearer token when endpoint authentication is required;
- [`jq`](https://jqlang.org/), which the report-review commands below use; and
- standard POSIX inspection utilities. [`ripgrep`](https://github.com/BurntSushi/ripgrep)
  (`rg`) and `tree` are recommended.

The endpoint must expose the full `/v1/completions` route. A chat-completions
route is not equivalent because its server-side chat template changes the raw
Antares tool prompt. Antares supports an optional `Authorization: Bearer`
credential; custom authentication headers and basic authentication are not
configurable.

### Choose local paths

Choose the target repository and a report directory outside that repository:

```bash
export ANTARES_TARGET_REPOSITORY="/absolute/path/to/project"
export ANTARES_REPORT_ROOT="/absolute/path/outside/project/antares-reports"

test -d "$ANTARES_TARGET_REPOSITORY"
mkdir -p "$ANTARES_REPORT_ROOT"
```

The `test` command should complete without an error. Keep report directories
outside the target so generated artifacts cannot become scan inputs.

### Understand the data boundary

`plan` profiles the repository locally and does not contact the inference
endpoint.

`query` and `sweep` create a temporary read-only repository snapshot. They may
send the Antares tool prompt and CWE/request instructions to the configured
endpoint. Later model turns may also send repository-relative paths, directory
listings, and source excerpts returned by model-requested inspection. Only scan
code you are authorized to send there. Antares does not control endpoint-side
logging or retention.

Antares also keeps private run history and investigation traces under
`~/.local/share/antares-cli` by default, or under `ANTARES_DATA_DIR` when set.
These files persist locally and may contain prompts, model responses, tool
arguments, repository paths, and source excerpts. Protect that directory.
If the default location has no writable parent, Antares falls back to
`.antares-data` in the current directory. Set `ANTARES_DATA_DIR` to a private
directory outside the target repository when that fallback would be unsafe.
`--no-report` does not disable private history or traces.

Repository `.gitignore` rules are not automatically used as Antares exclusions.
Before scanning, open `$ANTARES_TARGET_REPOSITORY/.antares.toml` and merge in
any sensitive, generated, or irrelevant paths. Do not overwrite existing
project settings. Patterns are relative to the target repository:

```toml
ignore_paths = [
  ".env",
  "secrets/**",
  "generated/**",
]
```

Do not put secrets in `--query` instructions, reports, screenshots, or shared
trace material.

## 1. Install Antares

Sign in to Hugging Face, accept the repository's access conditions, and wait
for access approval. Then download
[`assets/antares-cli.zip`][antares-cli-zip] from the repository's Files
section.

Set the downloaded archive path and a new extraction path that does not already
exist. Extract the archive, confirm that it contains the source package, and
install that package:

```bash
export ANTARES_CLI_ARCHIVE="/absolute/path/to/antares-cli.zip"
export ANTARES_CLI_SOURCE="/absolute/path/to/new/antares-cli"

test -f "$ANTARES_CLI_ARCHIVE"
unzip "$ANTARES_CLI_ARCHIVE" -d "$ANTARES_CLI_SOURCE"
test -f "$ANTARES_CLI_SOURCE/pyproject.toml"
uv tool install "$ANTARES_CLI_SOURCE"
```

Make the `uv` tool directory available in this shell, then verify the CLI:

```bash
export PATH="$(uv tool dir --bin):$PATH"
command -v antares
antares --version
antares --help
```

If `uv tool install` warned that its executable directory was not on `PATH`,
`uv tool update-shell` can make the change persistent for future terminals.
`antares --help` and `antares COMMAND --help` are the authoritative references
for the installed version's current commands and options.

For a no-install invocation, use `uvx`:

```bash
uvx --from "$ANTARES_CLI_SOURCE" antares --version
```

The remaining examples assume `antares` is installed as a tool. If you use
`uvx`, replace `antares` with
`uvx --from "$ANTARES_CLI_SOURCE" antares` in each command.

## 2. Configure the supplied inference connection

Create the configuration directory with access limited to the current user:

```bash
mkdir -p "$HOME/.antares"
chmod 700 "$HOME/.antares"
```

Open `~/.antares/profiles.toml` in an editor and add the block below without
removing any existing profiles. Replace the model placeholder before
continuing:

```toml
[profiles.quickstart]
display_name = "Antares Quickstart"
model = "REPLACE_WITH_EXACT_SERVED_MODEL_ID"
backend = "remote"
endpoint_env = "ANTARES_ENDPOINT"
api_key_env = "ANTARES_API_KEY"
```

Set the endpoint to the full completions route:

```bash
export ANTARES_ENDPOINT="https://inference.example.test/v1/completions"
unset ANTARES_MODEL

case "${ANTARES_ENDPOINT%/}" in
  http://*/v1/completions|https://*/v1/completions)
    echo "ANTARES_ENDPOINT has the expected route suffix"
    ;;
  *)
    echo "ANTARES_ENDPOINT must be a full HTTP(S) /v1/completions URL" >&2
    false
    ;;
esac
```

Replace the example host with the full completions URL supplied by the endpoint
owner. `ANTARES_MODEL` is cleared because an ambient value overrides the model
in a named profile during `query` and `sweep`.

Load `ANTARES_API_KEY` with your approved secret-management workflow when the
endpoint requires bearer authentication. Do not paste the token into
`profiles.toml` or a command argument. Confirm that the variable is available
without printing its value:

```bash
if [ -n "${ANTARES_API_KEY:-}" ]; then
  echo "ANTARES_API_KEY is set"
else
  echo "ANTARES_API_KEY is not set"
fi
```

If the endpoint does not require authentication, set `api_key_env = ""` in the
profile and clear the ambient default key:

```bash
unset ANTARES_API_KEY
```

Omitting `api_key_env` selects the `ANTARES_API_KEY` default, so keep the field
present and empty.

The exports in this guide apply only to the current terminal session. Reload
the endpoint and credential through your approved workflow when you open a new
terminal, and clear `ANTARES_MODEL` again before using this profile.

Protect the user-owned configuration and confirm that Antares discovers it:

```bash
chmod 600 ~/.antares/profiles.toml
antares models list
```

Confirm that the output contains a `quickstart` profile, the exact model ID, the
intended endpoint host, and an endpoint other than `not configured`.
`antares models list` does not contact the endpoint and intentionally
abbreviates its path. The check above catches a wrong route suffix; the first
`query` validates the complete URL, connectivity, and authentication.

Running `antares` without a subcommand opens an optional interactive command
builder when stdin and stdout are terminals. It selects an existing profile; it
does not create the connection configuration.

## 3. Choose the right command

| Command | Use it when |
| --- | --- |
| `antares plan PATH` | You want to preview automatic CWE coverage locally. |
| `antares query PATH --cwe CWE-...` | You want to investigate a specific CWE. |
| `antares sweep PATH` | You want independent investigations across several selected CWEs. |

Start with `plan`, continue with one focused `query`, and broaden to a bounded
`sweep` only after reviewing the focused result.

## 4. Preview automatic coverage locally

Limit the first portfolio to five CWE checks:

```bash
antares plan "$ANTARES_TARGET_REPOSITORY" --max-cwes 5
```

`plan` is a local selection preview, not a vulnerability scan. It:

1. profiles repository languages and security-relevant surfaces such as
   authentication, request input, secrets, network access, and deserialization;
2. starts with eligible entries from the bundled MITRE CWE taxonomy;
3. ranks exact source-pattern evidence before broader category evidence, MITRE
   relationship expansion, platform compatibility, and taxonomy tie-breakers;
4. applies the requested automatic limit; and
5. prints why each CWE was selected.

A `repository-specific` check has positive direct, category, or MITRE
relationship evidence from the repository. The label means the check may be
relevant; it does not mean Antares found that vulnerability. Selection
`confidence` and `score` describe repository relevance and ranking, not the
probability that a vulnerability exists.

Inspect the evidence fields as JSON when you want more detail:

```bash
antares plan "$ANTARES_TARGET_REPOSITORY" \
  --max-cwes 5 \
  --format json |
jq '.selected_checks[] | {
  cwe: .cwe_ids[0],
  title,
  tier: .selection_tier,
  direct: .repository_specific_evidence_score,
  category: .repository_category_evidence_score,
  relationship: .repository_relationship_evidence_score,
  reasons,
  evidence
}'
```

With an unchanged repository, CLI version, selection options, and Antares
configuration and environment, an automatic `sweep` uses the same selected CWE
portfolio.

## 5. Run one focused query

Choose a CWE that is relevant to your application or one of the IDs shown by
`plan`. This example uses SQL injection; replace it when another CWE is more
appropriate:

```bash
export ANTARES_FOCUS_CWE="CWE-89"

antares query "$ANTARES_TARGET_REPOSITORY" \
  --cwe "$ANTARES_FOCUS_CWE" \
  --profile quickstart \
  --output "$ANTARES_REPORT_ROOT/first-query"
```

Use a new output directory name for each run you want to retain; reusing one
replaces its report files. A completed run, and many incomplete runs, save
`report.json`, `report.md`, and `report.sarif` in the output directory. This
quickstart uses `report.json` for review.

Exit code `0` means the requested work completed. Exit code `2` means the
invocation was invalid or the result is incomplete; if `report.json` exists,
inspect it for partial results and warnings. Exit code `1` is not expected here
because this command does not use `--fail-on-findings`.

Do not add `--fail-on-findings` to the first local run. First establish that the
endpoint, model, and review workflow behave as expected.

## 6. Review `report.json`

Set the report path and verify that the file exists:

```bash
export ANTARES_QUERY_REPORT="$ANTARES_REPORT_ROOT/first-query/report.json"
test -f "$ANTARES_QUERY_REPORT"
```

Start with the outcome and operational signals:

```bash
jq '{
  summary,
  warnings: (.warnings // [])
}' "$ANTARES_QUERY_REPORT"
```

For a complete query, expect `warnings` to be `[]`,
`summary.generation_errors` and `summary.failed_workers` to be `0`, and
`summary.incomplete_reason` to be `null`. Treat any other values as incomplete,
even when findings are present.

Check the requested coverage. Use `metadata.cwe_ids`, not
`summary.cwe_ids_triggered`:

```bash
jq '.metadata | {
  mode,
  model,
  profile,
  target,
  cwe_ids,
  terminal_call_budget
}' "$ANTARES_QUERY_REPORT"
```

`summary.cwe_ids_triggered` contains only CWE IDs attached to returned findings.
It is not the list of checks Antares attempted.

List the candidate files:

```bash
jq '.findings[]? | {
  file_path,
  cwe_ids,
  title,
  submission_rank,
  likelihood_of_exploit
}' "$ANTARES_QUERY_REPORT"
```

Each `file_path` is relative to `$ANTARES_TARGET_REPOSITORY`.

Interpret these fields carefully:

- `submission_rank` is the model's one-based order within one investigation. It
  is not a probability, severity, or global sweep score.
- `likelihood_of_exploit` is MITRE taxonomy metadata. It is not model confidence
  in this particular candidate. MITRE provides this metadata for only a subset
  of CWEs, so the value can be an empty string.

## 7. Run a bounded automatic sweep

Preview the exact automatic-selection options again:

```bash
antares plan "$ANTARES_TARGET_REPOSITORY" --max-cwes 5
```

Set one shared output directory before choosing a sweep mode:

```bash
export ANTARES_SWEEP_OUTPUT="$ANTARES_REPORT_ROOT/first-sweep"
```

The commands below select up to five CWEs with `--max-cwes 5`, while
`--workers 2` allows at most two CWE investigations to run simultaneously.
`--workers` controls concurrency, not coverage, so all five selected
investigations still run in batches. Two workers is a conservative first-run
setting that limits load on the inference endpoint. Use `--workers 5` only when
the endpoint is provisioned for five simultaneous investigations.

Choose one sweep mode; do not run both examples. Start with the interactive
TUI:

```bash
antares sweep "$ANTARES_TARGET_REPOSITORY" \
  --max-cwes 5 \
  --workers 2 \
  --profile quickstart \
  --output "${ANTARES_SWEEP_OUTPUT:?Set ANTARES_SWEEP_OUTPUT}"
```

The TUI overview shows one row per selected CWE on the left and accumulated
findings on the right. Each row shows the investigation's status, tool-call
count, elapsed time, finding count, and latest tool call. Use the up and down
arrow keys to select a CWE, then press `Enter` to open its investigation.

The investigation view shows the activity stream on the left, including model
progress, terminal commands, and command results. Candidate findings appear on
the right with their title, repository-relative file path, submission rank,
CWE IDs, and likelihood of exploit. Press `Esc` to return to the overview, use
the left and right arrow keys to move between investigations, or press `?` to
view all keyboard shortcuts.

To use a headless terminal summary instead, run this command in place of the
TUI command:

```bash
antares sweep "$ANTARES_TARGET_REPOSITORY" \
  --max-cwes 5 \
  --workers 2 \
  --profile quickstart \
  --output "${ANTARES_SWEEP_OUTPUT:?Set ANTARES_SWEEP_OUTPUT}" \
  --no-tui
```

Each selected CWE receives its own investigation and repository-inspection
budget. In the TUI, wait until the footer shows `s save · q quit` before pressing
`q`. Closing the TUI early can leave the sweep incomplete. The sweep has the
same exit-code meanings as the focused query.

Review the sweep outcome and each worker:

```bash
export ANTARES_SWEEP_REPORT="$ANTARES_SWEEP_OUTPUT/report.json"

jq '{
  summary,
  warnings: (.warnings // []),
  coverage: .metadata.cwe_ids,
  selected_cwes: .metadata.selection.selected_cwe_ids,
  per_cwe_results: (.per_cwe_results // [])
}' "$ANTARES_SWEEP_REPORT"
```

For a complete sweep, also confirm that every
`per_cwe_results[].error_message` is `null`. Review candidate files with:

```bash
jq '.findings[]? | {
  file_path,
  cwe_ids,
  title,
  submission_rank,
  likelihood_of_exploit
}' "$ANTARES_SWEEP_REPORT"
```

Ranks from separate CWE workers are local to those workers and must not be
compared as a global ordering.

## Troubleshooting

### `uv` is unavailable

Install `uv` using your organization's approved method, then confirm:

```bash
uv --version
```

### `antares` is not found after installation

Add `uv`'s tool executable directory to the current shell and verify it:

```bash
export PATH="$(uv tool dir --bin):$PATH"
command -v antares
antares --version
```

Run `uv tool update-shell` if you want `uv` to add that directory to future
shell sessions, then follow its instruction to restart or reload your shell.

### The `quickstart` profile is missing or invalid

Confirm the filename and inspect profile discovery:

```bash
ls -l ~/.antares/profiles.toml
antares models list
```

The filename must be exactly `~/.antares/profiles.toml`.

If you receive a TOML parse error, correct the syntax described by that
diagnostic. For a generic profile-validation error, compare the entire
`[profiles.quickstart]` block with the supplied example, including field names
and value types. Then rerun `antares models list`.

If the endpoint is `not configured` after opening a new terminal, reload
`ANTARES_ENDPOINT` and any required `ANTARES_API_KEY`, then run:

```bash
unset ANTARES_MODEL
antares models list
```

### Authentication or permission fails

Check that the credential variable exists without printing it:

```bash
if [ -n "${ANTARES_API_KEY:-}" ]; then
  echo "ANTARES_API_KEY is set"
else
  echo "ANTARES_API_KEY is not set"
fi
```

Confirm that the credential is intended for this endpoint and that
`ANTARES_ENDPOINT` contains the full `/v1/completions` route. Antares sends the
credential as a bearer token; endpoints requiring another authentication
scheme need an external adapter or gateway.

### The first request is slow

Hosted endpoints may need several minutes to start. The profile uses the
Antares cold-start timeout unless you explicitly configure
`remote_timeout_seconds`. Ask the endpoint owner before changing connection
settings.

### The sweep is too large

If the sweep covers too many CWEs, reduce `--max-cwes` to decrease the total
number of investigations:

```bash
antares plan "$ANTARES_TARGET_REPOSITORY" --max-cwes 3

antares sweep "$ANTARES_TARGET_REPOSITORY" \
  --max-cwes 3 \
  --workers 2 \
  --profile quickstart \
  --output "$ANTARES_REPORT_ROOT/retry-sweep" \
  --no-tui
```

Tune `--workers` separately to match the inference deployment's capacity.
Increasing it can reduce sweep wall-clock time when the deployment can process
more requests concurrently. Reduce it if requests contend for resources, are
queued, time out, or encounter rate limits. Ask the endpoint owner how many
simultaneous requests the deployment supports when that limit is unknown.

### The TUI does not work in this terminal

Use `--no-tui` for a headless terminal summary. Use `--format json` only when
you need JSON on stdout; saved reports are still created unless
`--no-report` is also present.

### No report was created

Some configuration, path, and hard endpoint failures happen before Antares can
write a report. Read the terminal error, correct that problem, and rerun with a
new output directory. If the command exited `2` and `report.json` does exist,
review it as an incomplete result instead of discarding it.

## Next steps

Use `antares COMMAND --help` for the installed version's full option reference.
The extracted CLI's top-level `README.md` documents the complete configuration,
repository-isolation, output, and history contracts.

Later cookbook additions will cover inference deployment and adoption into CI
and pull-request workflows. Those operational decisions are intentionally
separate from this first local scan.

[antares-cli-zip]: https://huggingface.co/fdtn-ai/antares-1b/blob/main/assets/antares-cli.zip
