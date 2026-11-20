# Google Docs build (Steps 5 and 6)

Build the update natively in its dated tab, then render the tab and check it. Every call below was verified in Cursor on 2026-11-05 on a scratch doc, which was trashed afterward.

## Connector map

Preflight (Step 1) confirms every capability in the runtime's column is in the tool list. A missing capability is a stop: name it and the runtime.

| Capability | Cursor (verified) | Claude Code (unverified) |
| --- | --- | --- |
| List tabs, read a tab with element and cell indexes, get the revision ID | Docs `read_document` | `google-workspace` connector: confirm at preflight that a tool reads one tab and returns indexes |
| Append text with a paragraph style | Docs `insert_text` (omit `index`) | same check |
| Insert text at an index | Docs `insert_text` (`index`, `requiredRevisionId`) | same check |
| Find text, including in table cells | Docs `find_text` | the handoff says anchor search can't see table cells |
| Insert a table | Docs `insert_table` (omit `index` to append) | same check |
| Column widths | Docs `set_table_column_width` | same check |
| Header shading | Docs `set_table_cell_shading` | same check |
| Bold, italic, size, links | Docs `apply_text_style` | `format_text` per the handoff |
| Bullets and numbered lists, with nesting | Docs `create_list` | `create_bullet_list` per the handoff |
| Delete a range | Docs `delete_content` | same check |
| Read comments and replies | Drive `list_comments` | `read_file_content` with comments per the handoff |
| PDF export | Drive `export_file` (`application/pdf`); a large result is saved to a file | same check |

The handoff's Claude Code tools write whole documents, not tabs. If preflight finds no tab-targeted write in Claude Code, stop and tell Danny to run the skill in Cursor.

### Services with two connectors

Cursor has two connectors for some services, listed here in the order to try them. If the first fails after its retry, try the second the same way. Record the one that works in `sources.md`. Stop only when both fail, and report each one's error.

| Service | Cursor, in order |
| --- | --- |
| Jira and Confluence | `plugin-atlassian-atlassian`, then `user-Atlassian-MCP-Server` |
| Slack | `plugin-slack-slack`, then `user-slack` |

Google Docs, Drive and Sheets have one connector each. In Claude Code, confirm at preflight which connectors exist; this map doesn't carry over.

## Rules

- **Write only into the new dated tab.** Never touch another tab, the title, sharing or comments. Never set `suggest`.
- **Find the tab by exact title.** `read_document` with no `tabId` lists every tab. The title must equal the date in `feature.json` `doc.tab_title_format`. Zero matches or two matches is a stop.
- **The tab must be empty.** Its only element is one empty paragraph. Anything else is a stop: Danny decides.
- **Fresh indexes for every index-based write.** Take indexes from the latest `read_document` or `find_text`. Pass `requiredRevisionId` from that read or from the previous write's response (`revisionId`, or `writeControl.requiredRevisionId`). Append-mode `insert_text` and `insert_table` guard themselves.
- **On a revision mismatch** (a 400 because the doc changed), re-read the tab and compare it with `build-log.md`. Any change the skill didn't write, in the new tab or elsewhere in the doc, is a stop: tell Danny what changed and ask him to pause edits. Retry with fresh indexes only after his go.
- **Danny's edits in the tab.** Before any write after the read-back (Step 6 fixes, Step 7), re-read the tab and compare it with `readback.json`. Text you didn't write is Danny's edit. Rename `update-agent.md` to `update-agent-<n>.md` as the base, then copy his edit into `update.md` and save the result as `update-danny-<n>.md` (SKILL.md hard constraints). Never write over his text; if a fix would change it, stop and ask.
- **Log every write** in `build-log.md`: section, call, range, revision ID in and out.

## Build order

Build top-down, one section at a time, then style that section before moving on.

1. **Paragraphs.** Append each paragraph with `insert_text`, ending in `\n`. Pass `paragraphStyle` on every call so no paragraph keeps the previous one's style: `HEADING_1` for the H1, `HEADING_2` for sections, `NORMAL_TEXT` for body.
2. **Lists.** Append the items as paragraphs, one per line. Prefix a nested item with one tab per level. Then call `create_list` with the first and last item's text (`BULLET_DISC_CIRCLE_SQUARE` or `NUMBERED_DECIMAL_ALPHA_ROMAN`). The leading tabs become nesting and are removed.
3. **Tables.**
   - Append with `insert_table` (rows include the header). A key-value table (doc-spec) has an empty header line in `update.md` and no header row in the tab: insert only its data rows. It adds an empty paragraph above the table. After filling the table, append one empty paragraph so text below doesn't sit flush against it.
   - `read_document` returns the table's `start` and each cell's `start`. Insert each cell's text at its cell `start`.
   - Fill cells from the last cell to the first (bottom-to-top, right-to-left), so earlier cell indexes stay valid. Chain each write's `revisionId` into the next.
4. **Styles**, after a fresh read of the section:
   - Bold lead sentences and bold cells: `find_text`, then `apply_text_style` `bold`.
   - Links: `find_text` on the linked phrase (works inside cells), then `apply_text_style` `linkUrl`. When a phrase occurs more than once, pick the match by its `paragraph_text`.
   - Italic quotes: `apply_text_style` `italic` on the quote's range.
   - Header rows: one `apply_text_style` `bold` call over the header row's range (a range can span cells), then `set_table_cell_shading` on row 0 across every column (`#EFEFEF`). In a key-value table, shade column 0 down every row instead, and leave it unbolded.
   - Wide tables (6 or more columns): one `apply_text_style` `fontSize: 9` over the whole table's cell range.
   - Column widths: `set_table_column_width` per column. Widths in a table sum to `feature.json` `doc.text_width_pt`. Start count columns at 45 points and short-label columns at 60, give the widest text column the rest, then widen any column whose header word would break mid-word.

## Read-back (end of Step 5)

Re-read the tab. Check every section's text is present in order and every table has the rows and columns `update.md` specifies (a key-value table has one row fewer than its markdown, since it has no header). Record the result in `readback.json`: tab ID, revision ID, the tab's text, element count, table shapes, and any difference; refresh it after each later write. A difference is fixed before Step 6.

## Render (Step 6)

1. Export the doc with Drive `export_file` as PDF. A large result is saved to a file; pass that file to the renderer.
2. Run `swift <skill>/scripts/render_pdf.swift <export-file> /tmp/ai-pilot-update/<feature-slug>/<date>/render 2`. It writes page images, page text and `links.tsv`. Never write renders into the repo.
3. Run `python3 -I <skill>/scripts/compare_tab.py --render <render dir> --update update.md --feature <feature.json>`. It finds the new tab's pages by its H1 and checks every text unit and link. Exit 2 (the H1 isn't in the export) is a stop: tell Danny the export didn't include the new tab. Whether a PDF export includes tabs after the first is unverified until the first run with two tabs.
4. Hand the page images to the Gate 3 grader (qa-briefs.md).

## Known limits to tell Danny

- Margins are set for the whole doc and carry over from the first update. *Example (Round 1): the Week 1 export renders with 54-point margins on US Letter, a 504-point text width.*
- The connector has no tool for cell padding, borders, pinned header rows, paragraph spacing or row settings. The handoff's Week 1 fixes included all of these. List the ones the render shows are needed at Gate 3. If a table row breaks across pages, Danny can turn off "Allow row to overflow across pages" in Table properties.
- The connector can't create tabs. Danny adds the blank dated tab at Gate 2.
- The connector can't insert person chips. Owners go in as names with mailto links; Danny converts them to chips by hand if he wants them. *Example (Round 1): the Week 1 tab shows content-change owners as chips.*
