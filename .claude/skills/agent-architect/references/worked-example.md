# Worked Example: Acceptance Testing Generator

Reference file loaded by agent-architect only when a build needs a full example of the 5-phase process. The phase rules themselves live in SKILL.md.

---

### Worked Example: Acceptance Testing Generator (Full 5-Phase Process)

This example demonstrates how to build a complex agent using all 5 phases. The agent generates acceptance testing documents from PRDs for a pharmacy/fulfillment software team.

---

#### Pre-Flight Assessment

| Question | Answer | Result |
|----------|--------|--------|
| Can I describe the ONE job in ≤10 words? | "Generate acceptance tests from PRD" — but actually involves parsing, analyzing, comparing, generating, and gap analysis | **Full Process** |
| Tools needed? | `Read` (PRD, templates, examples), `mcp__*__figma` (optional), `Write` (output) | 3+ tools |
| Easy to catch mistakes? | No — incorrect tests could miss critical functionality, cause compliance issues | **Critical** |

**Decision:** Full 5-Phase Process required.

---

#### Phase 1: DISCOVER (4D Canvas)

**Discovery Questions Asked:**
1. "What is this agent's ONE job?" → Generate comprehensive acceptance test documents from PRDs
2. "What does a perfect output look like?" → [User provided existing acceptance testing docs as examples]
3. "What must it NEVER do?" → Invent requirements not in PRD, miss PRD requirements, produce untestable criteria

**D1 — DEMAND:**
- **Primary Job:** Transform PRD requirements into testable acceptance criteria organized by category
- **Scope Boundary:** Does NOT execute tests, does NOT modify PRDs, does NOT approve releases
- **Input:** PRD document, optional Figma mocks, target folder path
- **Output:** Markdown acceptance testing document following team template
- **Success Criteria:** Every PRD requirement has ≥1 test; tests are specific and binary; gaps are flagged

**D2 — DATA:**
| Data Needed | Source | Availability | Layer |
|-------------|--------|--------------|-------|
| PRD content | User-provided file | Always | Domain |
| Figma mocks | User-provided link | Sometimes | Domain |
| Acceptance Testing Template | Workspace file | Always | Rules |
| Existing examples (2-3) | Workspace files | Always | Domain |
| FPSE Project Workflow | Workspace file | Always | Rules |

**D3 — DISCOVERY:**
| Data | Strategy | Tool |
|------|----------|------|
| PRD content | User provides path → Read | `Read` |
| Template | Read from known path | `Read` |
| Examples | Search for existing docs | `Glob` → `Read` |
| Figma | MCP integration (optional) | `mcp__*__figma` (e.g., `get_figma_data`) |
| Output | Write to user-specified path | `Write` |

**D4 — DEFENSE:**
- **Pre-Checks:** PRD file exists and is readable; Template exists
- **Post-Checks:** Every PRD requirement traced to ≥1 test; output matches template structure
- **Stop paths:** If no Figma link is given → proceed with PRD only; if a given Figma link fails → stop and report; if example docs are not found → stop and report (they are an Always input in D2)
- **Failure Modes:**
  1. FM1: Missing PRD requirement (no test covers it) — CRITICAL
  2. FM2: Invented requirement (test for something not in PRD) — HIGH
  3. FM3: Vague test criteria (not binary pass/fail) — MEDIUM
  4. FM4: PRD/Figma discrepancy not flagged — MEDIUM
  5. FM5: Wrong output format (doesn't match template) — LOW

**Complexity Assessment:**
- **Distinct Responsibilities:** 6 (gather inputs, read references, analyze PRD, analyze Figma, generate tests, gap analysis)
- **Critical Responsibilities:** Requirement coverage (FM1), accuracy (FM2)
- **Recommended Pattern:** Sequential Pipeline (each step feeds the next)

---

#### Phase 2: DESIGN (Architecture)

**Decomposition Decision:**
- Responsibilities: 6 (>3 threshold)
- Critical responsibilities compete for attention
- **Decision: Single prompt with internal phases** (not multi-agent)
- **Rationale:** Steps are tightly coupled; user needs single coherent interaction; internal step structure provides sufficient attention management

**Pattern Selected:** Single prompt with explicit internal workflow (Steps 1-10)

**Context Architecture:**
| Layer | Content | Tokens |
|-------|---------|--------|
| Intent | User request + target folder | ~50 |
| Domain | PRD content, Figma data, examples | Variable (loaded at runtime) |
| Rules | Template structure, quality standards, category definitions | ~800 |
| Environment | Current file paths, workspace structure | ~50 |

**Attention Strategy:**
- **Primary Focus:** Step-by-step workflow (Steps 1-10) in task_instructions
- **Repeated Constraints:** "PRD is source of truth" (appears 4x); "Be specific and testable"
- **Position:** Core workflow at start; quality checks before output; Remember section at end

**Tool Architecture:**
| Tool | Use When | On Failure |
|------|----------|------------------|
| `Read` | Loading PRD, template, examples | Ask user to confirm path |
| `Glob` | Finding example docs | Stop and report; examples are an Always input |
| `mcp__*__figma` | User provides Figma link | Stop and report the link and error |
| `Write` | Saving output | Stop, report the error, and give the output in chat |

**QA Strategy:** Include QA subagent: Yes. Critical output with 5 failure modes (Step 2.6).

---

#### Phase 3: DRAFT (Condensed)

The full prompt is 681 lines. Key structural decisions:

```xml
<system_role>
You are a specialized agent for generating comprehensive Acceptance Testing 
documents for the FPSE team at Hims & Hers...
</system_role>

<hard_constraints>
NEVER:
- Invent specific thresholds not in PRD (use "acceptable time")
- Miss any PRD requirement without a test case
- Produce vague, untestable criteria

ALWAYS:
- PRD is source of truth for requirements
- Flag PRD/Figma discrepancies
- Include UI Design Verification tests
</hard_constraints>

<workflow>
## Core Workflow (10 Steps)
### Step 1: Gather Inputs [ask user for PRD, Figma, target folder]
### Step 2: Read Reference Materials [template, examples, workflow doc]
### Step 3: Analyze the PRD [extract requirements by category]
### Step 4: Analyze Figma Mocks [extract UI implementation details]
### Step 5: Flag Discrepancies [PRD vs Figma table]
### Step 6: Generate Test Cases [organized by 25 categories]
### Step 7: Quality Checks [coverage, naming, consolidation]
### Step 8: Gap Analysis [what we tested beyond PRD; what we didn't test]
### Step 9: Generate the Document [following template]
### Step 10: Present and Save [summary + confirmation + save]
</workflow>

<categories>
[25 test categories with guidance on when to use each]
</categories>

<quality_standards>
[Good/bad test case examples, naming conventions, environment guidelines]
</quality_standards>

<patterns>
[Common patterns for Queue Views, Detail Pages, Search Pages, etc.]
</patterns>
```

**Token Efficiency Decisions:**
- Categories defined once with guidance, not repeated
- Patterns section provides reusable templates by feature type
- Quality standards use good/bad examples instead of prose

---

#### Phase 4: EVALUATE

| Criterion | Pass/Fail | Evidence |
|-----------|-----------|----------|
| Clarity | ✅ Pass | 10-step workflow is explicit |
| Structure | ✅ Pass | XML sections, numbered steps |
| Hard Constraints | ✅ Pass | "PRD is source of truth" is specific |
| Context Layers | ✅ Pass | Steps 1-2 load context explicitly |
| Examples | ✅ Pass | Good/bad test case examples in quality standards |
| Output Schema | ✅ Pass | Template in Step 9 is exact |
| Error Handling | ✅ Pass | Stops on a failed Figma link or missing examples; PRD only when no link is given |
| Failure Modes | ✅ Pass | FM1-FM5 all addressed |
| Tools | ✅ Pass | Step 2 specifies which files to read |
| Token Efficiency | ✅ Pass | Categories defined once; patterns reusable |
| Producer/Grader | ✅ Pass | The orchestrator writes the document; the QA subagent only reports |

**Failure Mode Coverage:**
| FM | Addressed | How |
|----|-----------|-----|
| FM1: Missing requirement | ✅ | Step 7 checklist: "Every PRD requirement has ≥1 test" |
| FM2: Invented requirement | ✅ | Step 8 distinguishes "Test Cases Beyond PRD" from actual requirements |
| FM3: Vague criteria | ✅ | Quality Standards: good/bad examples; Step 7 checklist |
| FM4: Discrepancy not flagged | ✅ | Step 5 explicitly creates discrepancy table |
| FM5: Wrong format | ✅ | Step 9 provides exact template |

**Verdict:** All criteria PASS → QA subagent reports no failures → Proceed to DELIVER

---

#### Phase 5: DELIVER (Summary)

**Agent:** Acceptance Testing Generator
**Location:** `.claude/skills/acceptance-testing-generator/SKILL.md`
**Lines:** ~681 (complex agent with patterns library)

**Quick Start:** Generates comprehensive acceptance testing documents from PRDs following FPSE best practices.

**Test Cases:**
1. **Happy Path:** PRD with 15 requirements, Figma provided → 40-60 tests across 8 categories
2. **Edge Case:** PRD without Figma → Tests generated from PRD only; Design Verification section notes "Figma not provided"
3. **Error Case:** PRD file not found → Agent asks user to confirm path

**Key Design Decisions:**
- Single prompt with internal phases (not decomposed) because steps are tightly coupled
- 25 category library enables consistent test organization
- Gap analysis distinguishes "tested beyond PRD" from "needs PRD decision"
- "PRD is source of truth" repeated 4x for emphasis

---

**Takeaways from This Example:**

1. **Pre-Flight caught the complexity** — 6 responsibilities + critical failure modes → Full Process
2. **Decomposition decision was nuanced** — >3 responsibilities but tightly coupled → single prompt with phases
3. **Failure modes drove design** — FM1 (missing requirement) and FM2 (invented requirement) shaped the gap analysis structure
4. **Token efficiency** — Category library and patterns reduce redundancy while maintaining coverage
5. **Domain-specific patterns** — Queue views, detail pages, search pages have reusable test patterns
