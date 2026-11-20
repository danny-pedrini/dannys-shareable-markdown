# Design notes: feature-brief-writer

The v1.1 section at the end replaces several v1.0 decisions: the job, FM2, the Gate 1 framing, the options header, the Appendix defaults, and the tool list. Read it first. Everything between here and that section is the verbatim record of the v1.0 build conversation, kept as history and not edited.

# v1.0 build record (verbatim, Nov 18, 2026)

===== 85 assistant.message =====
I can't continue without your original message. My context reset partway through, and the session log never recorded what you asked.

**What I could recover from the log:**
- I started from the `agent-architect` skill and was in its Phase 1. So the task looks like building a new agent or skill, not editing the doc.
- I read your example doc (`10Tx82VVDOmAUDN8jw-uVNql_x-lbcw2rHFDjrXnoA1g`, with "Feature Brief" and "Appendix" tabs) as the reference for what the output should look like.
- I'd finished best-practice research on feature briefs and pitches. Two sources loaded fully: [Shape Up's "Write the Pitch"](https://basecamp.com/shapeup/1.5-chapter-06) and [Working Backwards PR/FAQ](https://workingbackwards.com/resources/working-backwards-pr-faq/). The Intercom, SVPG and Lenny's pages either didn't load or were paywalled, so I won't use them.

**What I don't know, and won't guess:**
- What the agent should produce. A new feature brief in the format of your example doc is my best guess, but I can't confirm it.
- What it takes as input, and any constraints you gave me.

Can you paste your original request again? Once I have it, I'll re-read the example doc and pick up Phase 1 where I stopped.

===== 87 user.message =====
Use the agent-architect skill (.claude/skills/agent-architect/SKILL.md) to build a new skill that writes feature briefs. Use the Full Process, not the Fast Path. Discovery is partly done; my answers so far are below.

## Discovery answers so far
1. Job: Write a feature brief that follows product management best practice. Get that best practice from the most credible sources on the web, such as Marty Cagan/SVPG, Amazon's working backwards PR/FAQ, Intercom, Basecamp's Shape Up and Lenny Rachitsky. Don't take it from my repo.
2. Perfect output: my recent feature brief, (internal link) It has two tabs, and you must read both.
3. Must never: go outside the brief template, or break the writing rules in AGENTS.md, CLAUDE.md, forbidden-writing-patterns.md and danny-voice-exemplar.md.
4. External data: yes, from any of my MCPs. If any MCP the run needs fails in a session, stop all work and report what failed.

## Decisions already made
- This is a new skill in .claude/skills/.
- Research best practice from credible web sources once, during this build, rather than on every run. Turn it into one feature brief template saved in Templates/. Base the template on that research and on my example doc. Cite the sources for the template's structure.
- The skill fills in that template on every run.

## Next steps
1. Read both tabs of the example doc with the Google Workspace MCP. If the read fails, retry once. If it fails again, stop and tell me which tool and error. Don't fall back to the browser, web fetch or repo context.
2. Research feature brief best practice from credible sources. Cite every source you use.
3. Finish the Discovery Gap Check, then give me the Step 4 "confirm understanding" summary. Wait for my confirmation before Phase 2 (Design).

===== 160 assistant.message =====
I've read both tabs and finished the research. The Gap Check comes out to 4 of 6 required fields clear. Three questions below block Phase 2, so I'm holding there until you answer and confirm.

## Research: where each part of your brief comes from

Your example already follows the strongest parts of these sources, so the template keeps your section order and cites these sources for each section.

| Brief section | Best practice it follows | Source |
| --- | --- | --- |
| **Summary**: the evidence, the proposal, and why the brief exists | The PR summary paragraph sums up the product and its benefit. Cagan ends his assessment with a go or no-go recommendation, and your purpose line ("validate feasibility before investing") is that ask. | [Working Backwards PR/FAQ](https://www.workingbackwards.com/concepts/working-backwards-pr-faq-process); [Cagan, Assessing Product Opportunities](https://www.svpg.com/assessing-product-opportunities/) |
| **What is X?**: today's experience, then the new one | Shape Up says the best problem statement is one specific story showing why today doesn't work. Amazon's solution paragraph starts from what customers do today. | [Shape Up, Write the Pitch](https://basecamp.com/shapeup/1.5-chapter-06); PR/FAQ |
| **Why would we do X?** | Cagan's questions on the problem, how big the opportunity is, and how we'll measure success. Lenny's "How do we know this is a real problem and worth solving?" | Cagan; Lenny's 1-pager template |
| **What could go wrong?** | Cagan's four risks: value, usability, feasibility and viability, where viability includes legal. Amazon's "top three reasons this product will not succeed." Shape Up's rabbit holes. | [Cagan, The Four Big Risks](https://www.svpg.com/four-big-risks/); PR/FAQ; Shape Up |
| **What are our other options?** | A good FAQ shows "that multiple options were considered." | PR/FAQ |
| **Critical discovery questions**, grouped by stakeholder | The internal FAQ anticipates questions "from every department," including legal and operations. Cagan says to tackle value and business risk early. | PR/FAQ; Four Big Risks |
| **Appendix** visuals labeled "not for copy or design approval" | Shape Up says to help people see the idea without over-specifying it, and to add a disclaimer that designers have latitude. | Shape Up |
| (How a scenario is framed) | Job stories put the situation, the motivation and the outcome in one sentence, without personas. | [Intercom, Designing features using Job Stories](https://www.intercom.com/blog/using-job-stories-design-features-ui-ux/) |

Intercom's one-page "Intermission" brief came back empty twice (one fetch error, one 404), so the only Intercom source here is job stories. If you have a working link, I'll add it.

## Discovery Gap Check

| Field | Status | What I have |
| --- | --- | --- |
| Job | ✅ | Write a feature brief that follows the cited best practice and sounds like the Feature X brief. |
| Input format and source | ❓ | See question 1. |
| Output format | ❓ | See question 2. |
| Failure modes | ✅ | (1) A number, quote, name or link that no source the run read backs up. (2) The solution comes first and the evidence never appears. (3) A section added or dropped outside the template. (4) A writing-rule violation, especially compressed shorthand and AI slop. (5) The run keeps going after an MCP failure. |
| Context needed | ✅ | The new template in `Templates/`, `AGENTS.md`, `forbidden-writing-patterns.md` (70 lines), and `danny-voice-exemplar.md` (225 lines). `CLAUDE.md` is a symlink to `AGENTS.md`, so it's the same file. Possibly `Stakeholder Management/stakeholder-directory.md` for the named stakeholders (see question 1). |
| Tools needed | ✅ | The Google Workspace MCP to read sources and build the doc, plus the Confluence, Jira and Slack MCPs when you pass those sources in. There's no web research at run time. On any MCP failure, retry once, then stop and report. |
| Example output | ✅ | Feature Brief: Feature X, both tabs. |

## Questions

1. **What will you give the skill on each run?** My guess is a short pitch of the idea plus links to the evidence (analyses, decks, Jira, Slack). Should the skill take stakeholder names from `stakeholder-directory.md`, or only from what you pass in?
2. **What should it produce?** A native Google Doc with two tabs, "Feature Brief" and "Appendix," like your example? Or should it also save a markdown copy in the repo?
3. **Should the template add three sections the sources call for that your example doesn't have?** The three are an appetite, meaning how much we'll invest (Shape Up); no-gos, meaning what's out of scope (Shape Up); and a success measure (Lenny, Cagan). My recommendation is to fold the success measure into "Why would we do X?" and skip the other two. A feasibility brief is asking whether to invest at all, so a time budget comes too early.

## Step 4: Confirm understanding

- **Job:** Draft a feature brief in your template and voice that gets cross-functional stakeholders to answer feasibility questions before anyone invests in building it.
- **Input:** Pending question 1.
- **Output:** Pending question 2. Each run fills in the one template, which I'll build from this research and your example and save in `Templates/`.
- **Must never:** Go outside the template, break the rules in `AGENTS.md`, `forbidden-writing-patterns.md` or `danny-voice-exemplar.md`, or keep working after an MCP failure.
- **Tools needed:** The Google Workspace MCP, plus whichever MCPs your sources come from. Every one is retried once, then the run stops.
- **Example:** Feature X.

Answer the three questions and confirm, and I'll start Phase 2 (Design).

===== 162 user.message =====
1. That sounds right - probably a verbal brain durmp, some discovery notes, maybe a prototype, Slack convos, etc.--really nothing is off the table
2. No, local markdown file in my repo (I can push to Google or Confluence as I see fit)
3. Aligned with your recommendation

Everything else looks good. May need to be able to push to Confluence too.

===== 207 assistant.message =====
Discovery is confirmed, so here is the Phase 2 design. Before I draft anything I need answers to three questions (at the end), plus your OK on four defaults.

## 4D Canvas

**D1 Demand**
- **Job:** Turn whatever Danny gives it into a feature brief, in the fixed brief template, where every claim has a source and the evidence comes before the proposal.
- **Scope boundary:** It doesn't write PRDs, acceptance criteria or decks. It doesn't decide whether an idea is worth a brief. It never pushes anywhere unless Danny asks.
- **Input:** Any mix of a brain dump, notes, a prototype, Slack threads, Confluence pages, Google Docs, sheets and Figma.
- **Output:** One local markdown file holding the Brief and its Appendix. A Confluence push happens only when Danny asks for it.
- **Success:** Every applicable QA check and eval passes, and Danny approves the brief at the final gate without rewriting a section.

**D2 Data**

| Data | Source | Availability | Sensitivity | Layer |
| --- | --- | --- | --- | --- |
| Feature idea and framing | Danny's brain dump or invocation | Always | Internal | Intent |
| Evidence (analyses, metrics, quotes) | Docs, Sheets, Slack, Confluence, Looker | Sometimes | Internal; PHI is never copied | Domain |
| Today's patient or provider copy | Prototype, Figma, screenshots or a pasted copy | Sometimes | Internal | Domain |
| Names and owners | Inputs, plus `Stakeholder Management/stakeholder-directory.md` | Always | Internal | Domain |
| Template | `Templates/Feature-Brief-Template.md` (new) | Always | Public sources | Rules |
| Writing rules | `AGENTS.md`, `forbidden-writing-patterns.md`, `danny-voice-exemplar.md` | Always | Internal | Rules |
| Run date and author | System | Always | Internal | Environment |

**D3 Discovery:** The skill takes direct input from Danny and calls MCP tools for every link he gives. It runs no RAG and no web search, because the best practice is built into the template, not looked up on each run.

**D4 Defense**
- **Pre-checks:**
  - A preflight tests every connector and link before any work starts.
  - Every template section has a source, an answer, or an owned `[TBD: …]`.
- **Post-checks:**
  - A script checks the template, the forbidden-pattern searches and the plain-word bans.
  - Independent graders check fidelity, evidence order and voice.
  - Every link in the draft is opened.
- **Stop paths:** Any tool, file or link that fails gets one retry, then the run stops and reports.
- **Failure modes (confirmed):**
  1. FM1: an unsourced number, quote, name or link.
  2. FM2: the solution comes before the evidence.
  3. FM3: a section added or dropped outside the template.
  4. FM4: a writing-rule violation.
  5. FM5: the run continues after an MCP failure.

## Step 2.0 Decomposition

The skill has seven responsibilities, so it has to be decomposed (rule 1):

| # | Responsibility | Critical? |
| --- | --- | --- |
| 1 | Preflight and read every source | Yes (FM5) |
| 2 | Build an evidence ledger (each claim with its source) | Yes (FM1) |
| 3 | Ask gap questions mapped to template sections | No |
| 4 | Draft the brief and appendix | Yes (FM2, FM3, FM4) |
| 5 | QA and evals | Yes |
| 6 | Log and verify the trace | No |
| 7 | Push to Confluence on request | Yes (it changes external state) |

**Pattern:** a gated sequential pipeline with an iterative QA loop. It runs only when Danny invokes it.

One change from `prd-generator`: there, subagents draft the PRD. Under the current agent-architect rule, the orchestrator writes the brief and subagents only grade it. A brief is short enough that this costs nothing.

## Workflow

| Step | What happens | Who |
| --- | --- | --- |
| 0 | Ask for the feature name, inputs, output path and anything missing (one batch) | Orchestrator |
| 1 | Preflight: test each connector the inputs need and open every link. Any failure stops the run. | Orchestrator |
| 2 | Read each source and save a copy to `<run>/sources/`. Capture prototype screens. | Orchestrator |
| 3 | Write `<run>/ledger.md`, one row per claim, number, quote, name and link, each with its source | Orchestrator; a `local-grader` checks every row against the saved copies |
| 4 | Gap questions for template sections the ledger can't fill, in one batch | Orchestrator |
| Gate 1 | Danny approves the framing: the evidence that leads, the proposal, fallback options and question owners | Danny |
| 5 | Draft the brief from the template and the ledger only | Orchestrator |
| 6 | QA loop of at most 3 rounds: a script (FM3, mechanical FM4), Fidelity judge (FM1, FM2), Writing judge (judgment FM4). The orchestrator also opens every link in the draft. | Script and `local-grader` judges; orchestrator fixes |
| 7 | Run the evals, write the log and trace, then a verifier checks it. A script checks FM5 against the trace. | Script and `local-grader` |
| Gate 2 | Present the brief with any QA flags | Danny |
| 8 | Push to Confluence, only when asked | Orchestrator, after Danny confirms the parent page and title |

## Tools and stop messages

| Tool | Use | When not to use | On failure |
| --- | --- | --- | --- |
| Read / Write / Edit | Inputs, run folder, the brief | Never write under `Repos/` | Stop and report the path |
| Google Docs / Sheets MCP | Doc and sheet links | Don't use it for Slack or Confluence links | "Stopped. Google [tool] failed on [ID]: [error]. Fix access or paste the source, and I'll resume." |
| Slack MCP | Thread links | Never use search to substitute for a thread that failed | Same stop message |
| Atlassian MCP (read) | Confluence and Jira links | Never as a write during Steps 0 to 7 | Same stop message |
| Figma / Chrome DevTools | Mocks and prototypes | Don't use it on a local prototype that has a source path; read `src/` through a subagent | Same stop message |
| Atlassian MCP (write) | Step 8 only. Load `getContentFormatGuide`, then `getConfluenceSpace`, then `createConfluenceContent`. | Never without an explicit ask | Report the error and give the brief in chat |

## QA and human-in-the-loop

**QA will be included.** There are five failure modes and the brief goes to Legal and Clinical leaders, so a self-check isn't enough. Danny can change this.
- **Fix scope:** sourcing tags, the order of sentences within a section, wording that trips a writing rule, and section headers that drifted from the template.
- **Fix boundary:** the proposal, fallback options, question owners, and adding or cutting a section.

| Decision point | Class |
| --- | --- |
| Preflight, source reads, ledger | Ag

(The v1.0 record is cut off here in the saved session log.)

# v1.1 changes (Nov 18, 2026)

## Why

Danny said v1.0 was overfit to its one example. Feature X was a feasibility check with Legal, Clinical, and Care Ops, but that is only one use of a feature brief. A brief is a one-pager on something we plan to build, explore further, or solution on. Danny also said evidence-first doesn't belong as a top-line rule, and that what he wants is a well-written brief that uses the context he provides and has good insight.

## What changed, and what it replaces

| Area | v1.0 decision | v1.1 decision |
|---|---|---|
| Job (D1) | Evidence comes before the proposal, and the brief asks Legal, Clinical, and Care Ops whether the most impactful version is feasible | A one-pager that helps its readers make the next decision. The purpose is picked per run: a feasibility check, discovery, solutioning, or a build proposal (template, "Purpose and readers") |
| FM2 | The solution comes before the evidence | The brief doesn't tell its readers why to care, or what it needs from them, before asking them to take in the solution. G4 is renamed "Reader-first order." Opening with evidence, the problem, or "We propose X because Y" can all pass |
| Insight | Not covered | Step 4 looks for something the sources show together that none of them says alone. Danny approves it at Gate 1, and G7 checks the brief carries it |
| Gate 1 | Lead evidence, the proposal, Fallback A and B, question owners, the fallback header, and the Appendix list | The purpose and readers, the insight, the opening, the proposal, the options, question owners, the options header, and the Appendix list |
| Summary paragraph 2 | The Feature X feasibility line, adapted | Fits the Gate 1 purpose. The feasibility line is one example |
| Options header | One of three fixed wordings ("isn't feasible", "legally", "clinically") | Any wording that starts "What are our other options" and ends "?". The script reads it from `Options header:` in `gate-1.md` |
| Options | Less risky, less impactful fallbacks | Fallbacks, different approaches, a smaller first step, or doing nothing, each with what it gives up or gains |
| Appendix | Feature X's five sub-sections as the default list | A menu of common types, chosen from the material the run has |
| Intake (Step 0) | Question 5 asked which functions must weigh in | Question 5 asks for the purpose, readers, and ask. A new question 6 asks what to look up beyond the inputs |
| Tools (D3) | Slack read only. No code access | Slack search, only when Danny asks. Code Explorer for how today's system behaves, only when Danny names a service, flow, or screen, or says yes to question 6. Code facts need a `read_source` read and use a `code: <repo>/<path>` ledger link |
| Graders | The writing judge read the brief as a Legal, Clinical, or Care Ops leader | The writing judge reads the brief as one of the readers named in `gate-1.md` |

## What stayed the same

The canonical headers stayed the same, apart from the options header wording. These are also unchanged: the ledger, the MCP stop rule, the QA loop, the observability setup, and the rule that "Today" comes before "With X." Describing the problem before the solution holds for every kind of brief, so that rule stays.

## Open

- `slack_search_public_and_private` was written from memory. Check it against the Slack connector's tool name on the first run that searches.
- No real brief has run on v1.1 yet. The G4 example still comes only from Feature X, and G3 and G7 have no examples, so add them from the first discovery or solutioning brief.