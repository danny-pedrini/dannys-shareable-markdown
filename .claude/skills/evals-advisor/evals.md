# Evals: evals-advisor

These evals check one evals-advisor run: its transcript, the saved report, the handoff file and any `evals.md` it wrote. SKILL.md has no eval runner step, so each eval runs when Danny asks for it or in a validation replay. Code-based evals read the Claude Code transcript for the run. "Saved report" means the file Step 4 writes under `observability/evals-advisor/` (or the target's run folder).

## Active Evals

| ID | Name | Type | Check | Added | Last Result |
|----|------|------|-------|-------|-------------|
| EA-01 | No evals.md write before acceptance | Generalization | Code | 2026-11-06 | not run |
| EA-02 | Saved report is complete and its count matches | Generalization | Code | 2026-11-06 | not run |
| EA-03 | Every Observed line names a file and section read | Generalization | Code | 2026-11-06 | not run |
| EA-04 | Reads of the run output cover every line | Generalization | Code | 2026-11-06 | not run |
| EA-05 | evals.md is consistent after adoption | Generalization | Code | 2026-11-06 | not run |
| EA-06 | Step 6 handoff names everything pending | Generalization | Code | 2026-11-06 | not run |
| EA-07 | No finding repeats an issue Danny already flagged | Generalization | Judge | 2026-11-06 | not run |
| EA-08 | Coverage Check lists every D4 failure mode | Generalization | Code | 2026-11-06 | not run |
| EA-09 | No idle background subagent after handback | Generalization | Code | 2026-11-06 | not run |
| EA-10 | Chat or returned findings match the saved report | Generalization | Code | 2026-11-06 | not run |

## Definitions

### EA-01: No evals.md write before acceptance

**Pass:** every Write or Edit to a file named `evals.md` comes after a user turn that names at least one report ID to adopt. Step 6 writes no `evals.md`.
**Fail:** any Write or Edit to `evals.md` with no earlier user turn that names an ID to adopt, or any `evals.md` write made by the close step.
**Check type:** Code-based

```check
Type: absence
Source field: transcript tool calls (Write and Edit targets) and user turns, in order
Target field: Write and Edit calls whose target path ends in evals.md
Logic: for each such call, find the nearest earlier user turn. FAIL if that turn contains no report ID (regex \b[SGE]\d+\b) and no adopt word. Also FAIL if any such call falls inside Step 6. Detail = the call's position and the nearest user turn's position.
```

**Source:** Token-efficiency plan for evals-advisor, changes B, C and E (acceptance gate held fixed). **Added:** 2026-11-06

### EA-02: Saved report is complete and its count matches

**Pass:** the saved post-run report has the title line, "Run analyzed", "Issues found", and the Specification Issues, Generalization Issues and Clean Areas sections as Step 4 specifies. The N in "Issues found" equals the number of S and G items listed, and the X specification and Y generalization counts match the items under each heading.
**Fail:** a missing line or section, or a count that differs from the items listed.
**Check type:** Code-based

```check
Type: structural
Source field: saved report file (post-run reports only; design-time reports use their own structure)
Target field: header lines, section headings, and item headings of the form **[S1]: or **S1: and **[G1]: or **G1:
Logic: grep for each required line and heading. Count S and G item headings. Parse N, X and Y from the "Issues found" line. FAIL on any missing element or any count mismatch. Detail = the missing element or the two counts.
```

**Source:** Token-efficiency plan for evals-advisor, changes D, E and G (report must stay whole when saved, indexed or returned by the restricted agent). **Added:** 2026-11-06

### EA-03: Every Observed line names a file and section read

**Pass:** each S and G item's "Observed" line names a file and a section of it, the transcript shows the agent read that file, and the section heading exists in the file.
**Fail:** an Observed line that names no file or section, names a file the agent never read, or names a section that is not in the file.
**Check type:** Code-based

```check
Type: comparison
Source field: Observed lines in the saved report; Read and Grep tool calls in the transcript
Target field: file paths and section headings named in each Observed line
Logic: extract each path and quoted heading from the Observed line. FAIL if the path has no matching Read or Grep call, or if the heading is not found by grep in that file. Detail = the item ID and the missing path or heading.
```

**Source:** Token-efficiency plan for evals-advisor, changes F, G and H (section-first reads, restricted agent and fresh-subagent runs must stay grounded). **Added:** 2026-11-06

### EA-04: Reads of the run output cover every line

**Pass:** the Read calls on the run output, taken together, cover every line of the file.
**Fail:** any line of the run output that no Read call covers.
**Check type:** Code-based

```check
Type: comparison
Source field: line count of the run output file (wc -l)
Target field: offset and limit of each Read call on that file in the transcript
Logic: build the union of line ranges from the Read calls. A Read with no offset and limit counts as the lines its result returned. FAIL if the union misses any line from 1 to the file's line count. Detail = the first uncovered range.
```

**Source:** Token-efficiency plan for evals-advisor, change F (section-first reading must not skip text between headings). **Added:** 2026-11-06

### EA-05: evals.md is consistent after adoption

**Pass:** `python3 -I .claude/skills/evals-advisor/scripts/check_evals_md.py <evals.md>` exits 0 on every `evals.md` the run wrote.
**Fail:** the script exits non-zero on any such file.
**Check type:** Code-based

```check
Type: structural
Source field: each evals.md the run wrote or edited
Target field: script exit code and output
Logic: run check_evals_md.py on each file. FAIL on any non-zero exit. Detail = the script's first 5 output lines.
```

**Source:** Token-efficiency plan for evals-advisor, changes C and I. **Added:** 2026-11-06

### EA-06: Step 6 handoff names everything pending

**Pass:** when Step 6 offers a handoff and Danny accepts, the handoff file names the saved report path, every ID adopted in the run, every S item not yet applied, and every background agent still running.
**Fail:** the handoff omits any of those four.
**Check type:** Code-based

```check
Type: presence
Source field: saved report path; adopted IDs from the adoption turn; S item IDs in the saved report not marked applied; background agent descriptions from the transcript
Target field: the handoff file written with the handoff skill (Session-Handoffs/)
Logic: grep the handoff file for the exact report path, each adopted ID, each unapplied S ID and each running agent description. FAIL on any miss. Detail = the list of missing items. Skip (no result) when no handoff was written.
```

**Source:** Token-efficiency plan for evals-advisor, change B. **Added:** 2026-11-06

### EA-07: No finding repeats an issue Danny already flagged

**Pass:** no S or G item restates an issue that the brief lists as already flagged by Danny in the thread.
**Fail:** one or more items restate a listed issue.
**Check type:** LLM judge

```judge
Criterion: does any finding in the saved report restate an issue that the brief lists as already flagged by Danny?
Pass definition: every finding is about an issue that is not on the brief's already-flagged list.
Fail definition: at least one finding describes the same issue as an entry on the already-flagged list, even in different words.
Examples: [add Pass and Fail examples from your own runs, do not fabricate]
```

**Source:** Token-efficiency plan for evals-advisor, change H. Matching an issue to a finding needs interpretation, so code cannot do it. **Added:** 2026-11-06

### EA-08: Coverage Check lists every D4 failure mode

**Pass:** the design-time report's Coverage Check table has one row for each D4 failure mode in the brief, and each row names an eval ID or marks a gap.
**Fail:** a D4 failure mode with no row, or a row with neither an eval ID nor a gap marker.
**Check type:** Code-based

```check
Type: comparison
Source field: D4 failure mode list in the brief
Target field: rows of the Coverage Check table in the design-time report
Logic: for each D4 failure mode, grep the table for a row naming it. FAIL if no row exists, or if the row's Covered By cell is empty and its Gap cell does not start with Yes. Detail = the failure mode and the problem.
```

**Source:** Token-efficiency plan for evals-advisor, change H (Mode 3 report must hold when run in a fresh subagent). **Added:** 2026-11-06

### EA-09: No idle background subagent after handback

**Pass:** no background subagent records an API request more than 15 minutes after its last handback, unless the parent sent it a message after that handback.
**Fail:** any such request with no later parent message to that agent.
**Check type:** Code-based

```check
Type: absence
Source field: transcript timestamps for each background subagent (api-request records and last handback) and the parent's SendMessage calls
Target field: api-request records after the last handback
Logic: for each background subagent, take the last handback timestamp. FAIL if an api-request record is more than 15 minutes later and the parent made no SendMessage to that agent after the handback. Detail = agent ID and the first offending timestamp.
```

**Source:** Token-efficiency plan for evals-advisor, change S1 (AGENTS.md rule to stop finished background subagents). **Added:** 2026-11-06

### EA-10: Chat or returned findings match the saved report

**Pass:** every finding ID in the saved report appears in what Danny saw (the Mode 1 chat index or the Mode 2 returned report), and every finding ID Danny saw appears in the saved report.
**Fail:** an ID on one side with no match on the other.
**Check type:** Code-based

```check
Type: comparison
Source field: finding IDs (S and G) in the saved report
Target field: finding IDs in the Mode 1 chat index or the Mode 2 returned report in the transcript
Logic: extract both ID sets with regex \b[SG]\d+\b and compare in both directions. FAIL on any ID in one set and not the other. Detail = the unmatched IDs.
```

**Source:** Token-efficiency plan for evals-advisor, changes C and D. **Added:** 2026-11-06
