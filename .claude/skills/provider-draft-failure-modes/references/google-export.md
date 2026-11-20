# Google export

How Step 5 pushes the cluster report and CSV to Google Docs and Sheets, so the Evals team can open them without the repo.

> **Source:** Round 3 Step 5 Google push (2026-10-21); `google-workspace` MCP tool behavior observed that session. Checked `.claude/skills/synced/.../google-workspace/SKILL.md` and its references for applicable guidance: that skill covers the Drive/Docs/Sheets editor connectors (`create_file`, `read_file_content`, direct edit requests), not the `import_to_google_doc` / `import_to_google_sheets` tools this step uses, so nothing from it overrides the steps below. Its one transferable point is already general practice here: when a required connector or tool is missing, say so and ask, rather than building a workaround (root `AGENTS.md` MCP no-inference rule covers this).

## 1. Stage the files

The `google-workspace` MCP's import tools read only from `/Users/dpedrini/.workspace-mcp/attachments`. Copy the report markdown and the CSV there before calling either import tool.

- The copy needs the Bash sandbox override (`dangerouslyDisableSandbox: true`); it writes outside the allowed paths. Ask through the normal permission prompt, do not bypass it.
- Use the round's own file names so a later round doesn't collide with this one (for example `Round-3-Failure-Mode-Cluster-Analysis.md`, `round-3-rating-rows.csv`), per `round.json` `report.file` and `report.csv`.

## 2. Clean the markdown before import

The cluster report has in-doc anchors and anchor links (`<a id="tr-...">`, `[tr-...](#tr-...)`) that the trace appendix and failure-mode cards use for cross-references. Google Docs import does not preserve anchor links as working links.

- Strip every `<a id="...">` tag.
- Replace every in-doc anchor link (`[text](#anchor)`) with plain text, or with a link to the companion Sheet row if the target is in the rating/trace table rather than the appendix. Do this on the staged copy only; never edit the round folder's canonical report file to remove its anchors.
- Blockquotes (patient and provider message text, draft text) become plain paragraphs on import; Google Docs has no blockquote style to map onto. Leave them as blockquotes in the markdown and accept the plain-paragraph result, or flatten them yourself first if indentation matters for the reader; either way, verify after import (step 4).

## 3. Import

- `import_to_google_doc` for the cleaned report markdown, `user_google_email: you@example.com`.
- `import_to_google_sheets` for the CSV, same `user_google_email`.
- Retry once on failure. On a second failure, stop, tell the product owner which tool and file failed and why, and deliver the local files with a note that the push didn't happen; do not substitute a different Google tool or build the doc by hand with edit requests.

## 4. Format the Sheet

After import, the Sheet is a flat data dump. Fix the header row so the Evals team can use it immediately:

- Bold the header row.
- Freeze the header row.
- Set sensible column widths (trace IDs and the message/draft columns need more room than verdict or date columns).

## 5. Read both back to verify

- Read the Doc back and confirm the heading count matches the report's own section count (Key findings, 1 through 7 as laid out in `cluster-report-spec.md`).
- Read the Sheet back and confirm the row count matches the CSV's row count (192 rating rows plus the header, in the Round 3 shape; the count scales with the round's rating total).
- A mismatch on either count means the import truncated or merged something; do not report the push as done until both counts match.

## 6. Record the links

Write both resulting URLs into `round.json` under `report.google_doc_url` and `report.google_sheet_url`, and add a line to `STATUS.md` noting the push date and both links. These are the links the product owner and the Evals team use from then on; the local markdown and CSV stay in the round folder as the source of truth if either Google copy ever drifts.
