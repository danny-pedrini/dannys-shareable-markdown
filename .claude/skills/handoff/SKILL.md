---
name: handoff
description: Writes a session handoff into Session-Handoffs/ so the next session can resume. Use when Danny types /handoff or asks to hand off, pause, or resume a session.
---

# Handoff

Write one markdown file at `Session-Handoffs/<YYYY-MM-DD>-<HHMM>-<topic>.md`. Create the directory if it is missing. The directory is gitignored. Do not commit the file.

The file has these sections, in this order, and nothing else:

1. **Decisions.** One bullet per decision. Use the words that settled it, and name who decided.
2. **Quotes.** Exact quotes worth keeping, each with the speaker. If there are none, write "None."
3. **Open questions.** Unresolved questions only.
4. **Next action.** One bullet. The first thing the next session should do.

Rules:

- Copy decisions and quotes from this conversation. Do not write a quote you cannot point to in the thread.
- Do not paste raw tool output, MCP results, or patient data.
- Keep each section to what the next session needs.
- After writing, reply with the file path and the decision count.
