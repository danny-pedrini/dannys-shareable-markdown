"""Write raw thread-blocks/<code>.md from export/<code>.md, one block per trace cited in a
ticket's Evidence list (excluding "Also:" lines). Scans every `ticket-drafts*.md` file in the
round folder except `ticket-drafts-blind.md` (per-batch drafts, the merged file, or both, in
whatever state Step 3 has reached).

Earlier-round traces (v2.4). A bullet that starts `- Earlier round:` cites a trace from a round
listed in round.json `prior_rounds`. Its record comes from that round's `export/*.md`, and its
block goes to `thread-blocks/EARLIER.md` (it belongs to no batch of this round). Every other
cited trace must be in this round's export.

Output matches the structure Round 3 hand-built: a header line ("Names must be anonymized before
use. One block per trace."), then one "### `tr-<10 hex>` (<action>)" section per trace with
"Messages before the draft" (role, then a blockquote per message) and "Draft" (blockquoted).
Paragraph breaks inside the export's single-line message and draft text are reconstructed with a
heuristic (the Doc that produced export/ collapses paragraph breaks); treat this as best effort,
not an exact transcription. The heuristic never cuts inside a URL or a word (v2.4): it breaks
only at a sentence end, after a closing bracket, at an inserted `{{provider_intro}}` token, and
after the greeting comma. The output is RAW: names are not yet anonymized. Anonymization is a
separate pass before `add_threads.py` runs.
Run from the round folder:  python3 -I <skill>/scripts/make_thread_blocks.py
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.getcwd()
sys.path.insert(0, HERE)
import round_config as RC  # noqa: E402

EARLIER_CODE = "EARLIER"
EARLIER_RE = re.compile(r"^-\s+Earlier round:")
TRACE_HEADER_RE = re.compile(r"^\*Trace (tr-[0-9a-fA-F]{32})\s*·\s*Medication: [^*]*\*", re.M)
MSG_HEADER_RE = re.compile(r"\*\*([^*]+?)\*\*\*\s*\(([^)]*)\)\*\n\n(.*?)(?=\n\n\*\*|\Z)", re.S)
# A URL ends before trailing sentence punctuation or a closing bracket, so "(https://x.co/a)." keeps ")." outside it.
URL_RE = re.compile(r"https?://[^\s<>\"]*[^\s<>\".,;:!?)\]]")
GREETING_RE = re.compile(r"^([^,\n]{0,60},)(?=[A-Z])", re.M)  # "Hi NAME,Thanks ..." -> a greeting line (first one only)


def split_paragraphs(text):
    """Best-effort reconstruction of paragraph breaks collapsed by the source Doc export.

    A URL is masked first and restored last, so no rule can cut inside it. No rule cuts between a
    lowercase letter and a capital: that join is how a brand or product name is written
    (KwikPen, OxyContin, LillyDirect, ColonBroom), and no export in any round has used it as a
    paragraph break."""
    urls = []

    def mask(m):
        urls.append(m.group(0))
        return f"{len(urls) - 1}"

    text = URL_RE.sub(mask, text)
    text = text.replace("{{provider_intro}}", "\n{{provider_intro}}\n")
    text = re.sub(r"(?<=[\)\]])(?=[A-Z][a-z])", "\n", text)        # a closing bracket straight into a capitalized word
    text = re.sub(r"(?<=[.!?])\s+(?=[A-Z\[—-])", "\n", text)       # sentence end, then a new sentence, placeholder or dash
    text = GREETING_RE.sub(lambda m: m.group(1) + "\n", text, count=1)  # a "Hi NAME," greeting line
    text = re.sub("(\\d+)", lambda m: urls[int(m.group(1))], text)
    return [p.strip() for p in text.split("\n") if p.strip()]


def as_blockquote(text):
    paras = split_paragraphs(text)
    lines = []
    for i, p in enumerate(paras):
        if i:
            lines.append(">")
        lines.append(f"> {p}")
    return "\n".join(lines) if lines else "> "


def records_from_text(text):
    out = {}
    for part in re.split(r"\n(?=## \d+\. )", text)[1:]:
        m = TRACE_HEADER_RE.search(part)
        if m:
            out[m.group(1)] = part
    return out


def export_records(code):
    path = os.path.join("export", f"{code}.md")
    if not os.path.exists(path):
        return {}
    return records_from_text(open(path).read())


def evidence_traces():
    """(this-round trace IDs, earlier-round trace IDs, files scanned). Reads each ticket's
    "## Evidence" list across every ticket-drafts file, and each comment's evidence bullets in
    ticket-comments.md (which carry no "## Evidence" heading of their own). Excludes "Also:"
    lines in both. A bullet starting `- Earlier round:` feeds the earlier-round list.
    build_cluster_analysis.py's report appendix renders a thread block for every trace any unit
    cites, filed ticket or comment, so comments are in scope here too."""
    traces, earlier = [], []

    def add(line):
        dest = earlier if EARLIER_RE.match(line) else traces
        for t in re.findall(r"tr-[0-9a-fA-F]{10}", line):
            if t not in dest:
                dest.append(t)

    files = sorted(f for f in glob.glob("ticket-drafts*.md") if "blind" not in f)
    for path in files:
        text = open(path).read()
        for part in re.split(r"\n(?=### T-\d+\. )", text):
            if "## Evidence" not in part:
                continue
            ev = part.split("## Evidence", 1)[1].split("\n## ", 1)[0]
            for line in ev.split("\n"):
                if line.startswith("- ") and not line.lower().startswith("- also"):
                    add(line)
    if os.path.exists("ticket-comments.md"):
        files = files + ["ticket-comments.md"]
        for part in re.split(r"\n(?=### C-\d+\. )", open("ticket-comments.md").read()):
            for line in part.split("\n"):
                if (line.startswith("- `tr-") or EARLIER_RE.match(line)) and not line.lower().startswith("- also"):
                    add(line)
    return traces, earlier, files


def block_for(full_trace, action, record_text):
    msgs = []
    for m in MSG_HEADER_RE.finditer(record_text.split("**Provider draft**", 1)[0]):
        role, _meta, body = m.groups()
        msgs.append((role.strip(), body.strip()))
    draft_m = re.search(r"\*\*Provider draft\*\*\n\n(.*?)\n\n\*\*Explanation\*\*", record_text, re.S)
    draft = draft_m.group(1).strip() if draft_m else ""
    L = [f"### `{full_trace[:13]}` ({action})", "", "**Messages before the draft**", ""]
    for i, (role, body) in enumerate(msgs):
        if i:
            L.append("")
        L += [f"*{role}:*", "", as_blockquote(body)]
    L += ["", "**Draft**", "", as_blockquote(draft)]
    return "\n".join(L)


def write_file(code, header_note, blocks):
    L = [f"# Thread blocks: {code}", "", header_note, ""]
    for b in blocks:
        L += [b, ""]
    os.makedirs("thread-blocks", exist_ok=True)
    open(os.path.join("thread-blocks", f"{code}.md"), "w").write("\n".join(L).rstrip() + "\n")


def main():
    cfg = RC.load(os.path.join(ROOT, "round.json"))
    codes = RC.batch_codes(cfg)
    actions = RC.action_map(cfg)
    traces, earlier, files = evidence_traces()
    if not files:
        print("make_thread_blocks.py: no ticket-drafts*.md files found; nothing to do")
        return 0
    trace_to_code, trace_to_full = {}, {}
    for c in codes:
        for full in export_records(c):
            if full[:13] in traces:
                trace_to_code[full[:13]] = c
                trace_to_full[full[:13]] = full
    missing = [t for t in traces if t not in trace_to_code]
    by_code = {}
    for t in traces:
        if t in trace_to_code:
            by_code.setdefault(trace_to_code[t], []).append(t)
    written = 0
    for c, ts in by_code.items():
        records = export_records(c)
        blocks = [block_for(trace_to_full[t], actions.get(c, c), records[trace_to_full[t]]) for t in ts]
        write_file(c, "Names must be anonymized before use. One block per trace.", blocks)
        written += len(blocks)
    # Earlier-round traces: one record each from a prior round's export, one shared file.
    n_earlier, missing_earlier = 0, []
    if earlier:
        prior = RC.prior_round_exports(cfg)
        by_short = {full[:13]: full for full in prior}
        blocks = []
        for t in earlier:
            full = by_short.get(t)
            if not full:
                missing_earlier.append(t)
                continue
            path, action = prior[full]
            blocks.append(block_for(full, action, records_from_text(open(path).read())[full]))
        if blocks:
            write_file(EARLIER_CODE, "Names must be anonymized before use. One block per trace. "
                       "Each trace comes from a round in round.json prior_rounds.", blocks)
        n_earlier = len(blocks)
    else:
        stale = os.path.join("thread-blocks", f"{EARLIER_CODE}.md")
        if os.path.exists(stale):  # the last Earlier round: bullet is gone, so its block file is too
            os.remove(stale)
    print(f"wrote thread-blocks for {written} traces across {len(by_code)} batches and {n_earlier} earlier-round "
          f"traces, from {len(files)} ticket file(s)")
    if missing:
        print("MISSING (cited but no export record found):", missing)
    if missing_earlier:
        print("MISSING (cited as an earlier round's trace but not found in any prior_rounds export):", missing_earlier)
    return 1 if (missing or missing_earlier) else 0


if __name__ == "__main__":
    sys.exit(main())
