#!/usr/bin/env python3
"""Scrub the shareable-sync export buffer before it is pushed.

Runs on the export copy only, never on the workspace, so every skill keeps working
with real names, links, and figures internally. Usage:

    shareable-scrub.py <export-buffer-dir> <private-config-dir>

The private config dir (never published) holds:
  names.tsv        full/first<TAB>name<TAB>role. Names become "[role]".
  directories.txt  stakeholder directories read on every run. Each full name in them is
                   scrubbed to its role, unless names.tsv already sets one.
  phrases.tsv      literal<TAB>replacement, applied first.
  scale.txt        the factor dollar figures are multiplied by.
  README.md        copied to the export root.
  Reading-List.md  copied to AI-Learning/.
  link-stubs/      pointer files copied into the export at the same paths, in place of
                   excluded copies of other people's articles.

Exits 1 and prints what it found if any known name, work email, internal link,
confidentiality label, or listed phrase survives the scrub.
"""
import json
import os
import re
import sys

BUF, PRIV = sys.argv[1], sys.argv[2]

# Dollar figures in these files are public numbers and stay as written.
KEEP_DOLLARS = {
    "Templates/Example-ML-Docs/Babushkin-Kravchenko-Retail-Demand-Forecasting-Design.md",
}

STUB_NOTE = "This file is omitted from the public copy because it holds internal company material."

FILE_STUBS = {
    ".claude/skills/make-deck/references/hims-hers-style-guide.md":
        "# Brand style guide\n\n" + STUB_NOTE + " The make-deck skill reads the company's brand fonts, palette, "
        "and confidentiality footer from this file. Swap in your own brand guide to use the skill.\n",
    ".claude/skills/feature-brief-writer/references/exemplar-fast-prescribe.md":
        "# Doc exemplar\n\n" + STUB_NOTE + " The private version holds a full feature brief, written by Danny "
        "about an unreleased product, that the skill uses as its model of a good brief.\n",
    ".claude/skills/journey-map/references/examples/patient-provider-journey.json":
        json.dumps({"_note": STUB_NOTE + " The private version is a full journey-map spec built from real "
                    "research quotes and metrics, used as the skill's worked example.", "phases": []}, indent=2) + "\n",
    ".claude/skills/meeting-transcription/profiles/speaker-profiles.json":
        json.dumps({"_note": STUB_NOTE + " The private version maps each meeting speaker's voice to their name "
                    "and role, built up across meetings by the speaker-mapping skill.",
                    "profiles": {}}, indent=2) + "\n",
}

SECTION_STUBS = [
    ("danny-voice-exemplar.md", "## Doc exemplar:", "## Work-register exemplars",
     "## Doc exemplar (omitted from the public copy)\n\n"
     "The private version of this file opens with a full doc exemplar: the summary of an internal feature brief "
     "Danny wrote, set beside an AI draft of the same content. Each is annotated with what to imitate and what went "
     "wrong. The brief covers an unreleased product, so the public copy leaves it out. The work-register excerpts "
     "below show the same voice in shorter pieces.\n\n---\n\n"),
]

COPIES = [("README.md", "README.md"), ("Reading-List.md", "AI-Learning/Reading-List.md")]

INTERNAL_HOST = (r"https?://(?:[\w-]+\.)*(?:docs\.google\.com|drive\.google\.com|mail\.google\.com|"
                 r"atlassian\.net|looker\.com|slack\.com|figma\.com|loom\.com)(?:/[^\s)\]>\"'`|]*)?"
                 r"|https?://github\.com/your-org(?:/[^\s)\]>\"'`|]*)?")
MD_LINK = re.compile(r"\[([^\[\]\n]*)\]\(\s*(?:" + INTERNAL_HOST + r")\s*\)")
BARE = re.compile(INTERNAL_HOST)
FOOTER = re.compile(r"Confidential (?:&|&amp;|and) Proprietary Information of Hims (?:&|&amp;|and) Hers Health,? Inc\.? ?"
                    r"(?:\"\s*\"|\s*)?(?:External\s+Distribution\s+Prohibited\.?)?")
LABEL = "External Distribution " + "Prohibited"  # Split so this file never trips its own check.
DOLLAR = re.compile(r"\$(\d[\d,]*(?:\.\d+)?)(\s?)(K|M|B|million|billion|/hr|/hour)(?![\w])"
                    r"|\$(\d{1,3}(?:,\d{3})+(?:\.\d+)?)()()(?![\d,])")
EMAIL_WORK = re.compile(r"[\w.+-]+@forhims\.com")
DOUBLE_BRACKET_MAILTO = re.compile(r"\[\[([^\[\]\n]+)\]\]\(mailto:[^)\s]*\)")
DOUBLE_BRACKET = re.compile(r"\[\[([^\[\]\n]+)\]\]")
# Altered figures keep their ratios to each other, so worked examples still add up.
SCALE = float(open(os.path.join(PRIV, "scale.txt")).read().strip())


def load_tsv(name, cols):
    rows = []
    for line in open(os.path.join(PRIV, name), encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        parts = line.rstrip("\n").split("\t")
        if len(parts) == cols:
            rows.append(parts)
    return rows


def load_directories():
    """Full names and short roles from the stakeholder directories, read fresh each run."""
    skip_name = re.compile(r"\(|team|Sync|Weekly|Standups|Prioritization|Monthly|PMO|et al|Practice|"
                           r"(?:Product|Experience|Success|Growth|Design|Analytics|Engineering|Backend|Ops|Pharmacy)$", re.I)
    skip_role = re.compile(r"^(?:Weekly|Monthly|Daily|Bi-?weekly)\b", re.I)
    found = {}
    for line in open(os.path.join(PRIV, "directories.txt"), encoding="utf-8"):
        path = line.strip()
        if not path or path.startswith("#"):
            continue
        if not os.path.exists(path):
            print("SCRUB_CHECK_FAILED")
            print(f"stakeholder directory missing: {path}")
            sys.exit(1)
        for name, role in re.findall(r"^\| \*\*([^*|]+)\*\* \| ([^|]*)\|", open(path, encoding="utf-8").read(), re.M):
            name, role = name.strip(), role.replace("`[Needs validation]`", "").strip()
            if name == "Danny Pedrini" or " " not in name or name in found:
                continue
            if skip_name.search(name) or skip_role.search(role):
                continue
            role = re.split(r";|\(| — ", role)[0].strip().rstrip(",")
            if not role or re.fullmatch(r"[A-Z][a-z]+ [A-Z][a-z]+", role):
                role = "teammate"  # The role column held a manager's name, not a role.
            found[name] = role
    return found


PHRASES = load_tsv("phrases.tsv", 2)
NAMES = load_tsv("names.tsv", 3)
_listed = {n for k, n, _ in NAMES if k == "full"}
NAMES += [["full", n, r] for n, r in load_directories().items() if n not in _listed]
# One-word "full" entries (people listed by first name only) follow the first-name rule.
FULL = sorted([(n, r) for k, n, r in NAMES if k == "full" and " " in n], key=lambda x: -len(x[0]))
FIRST = sorted([(n, r) for k, n, r in NAMES if k == "first" or (k == "full" and " " not in n)],
               key=lambda x: -len(x[0]))
FULL_RE = [(re.compile(r"(?<![\w])" + re.escape(n) + r"(?![\w])"), f"[{r}]") for n, r in FULL]
HYPHEN_RE = [(re.compile(r"(?<![\w])" + re.escape(n.replace("Dr. ", "").replace(" ", "-")) + r"(?![\w])"),
              r.replace(" ", "-").replace("&", "and")) for n, r in FULL if " " in n.replace("Dr. ", "")]
# A first name followed by a capitalized word is someone else (or a full name to add to names.tsv), so skip it.
FIRST_RE = [(re.compile(r"(?<![\w@.-])" + re.escape(n) + r"(?![\w@]|-[a-z]+\.\w|['’]t\b| [A-Z][a-z])"), f"[{r}]") for n, r in FIRST]


def scale_dollar(m):
    if m.group(1):
        raw, space, unit = m.group(1), m.group(2), m.group(3)
    else:
        raw, space, unit = m.group(4), "", ""
    value = float(raw.replace(",", ""))
    decimals = len(raw.split(".")[1]) if "." in raw else 0
    new = value * SCALE
    while decimals < 3 and round(new, decimals) == 0:
        decimals += 1
    text = f"{new:,.{decimals}f}" if "," in raw else f"{new:.{decimals}f}"
    return f"${text}{space}{unit}"


def scrub(rel, text):
    for old, new in PHRASES:
        text = text.replace(old, new)
    text = EMAIL_WORK.sub("teammate@example.com", text)
    text = MD_LINK.sub(lambda m: m.group(1), text)
    text = BARE.sub("(internal link)", text)
    text = FOOTER.sub("[Company confidentiality footer]", text)
    for rx, rep in FULL_RE:
        text = rx.sub(rep, text)
    for rx, rep in HYPHEN_RE:
        text = rx.sub(rep, text)
    for rx, rep in FIRST_RE:
        text = rx.sub(rep, text)
    text = DOUBLE_BRACKET_MAILTO.sub(r"[\1]", text)
    text = DOUBLE_BRACKET.sub(r"[\1]", text)
    if rel not in KEEP_DOLLARS:
        text = DOLLAR.sub(scale_dollar, text)
    return text


def check(rel, text):
    found = []
    for n, _ in FULL:
        if re.search(r"(?<![\w])" + re.escape(n) + r"(?![\w])", text):
            found.append(n)
    for old, _ in PHRASES:
        if old in text:
            found.append("phrase: " + old[:40])
    if EMAIL_WORK.search(text):
        found.append("work email")
    if BARE.search(text):
        found.append("internal link")
    if LABEL in text:
        found.append("confidentiality label")
    return found


def text_files():
    for root, dirs, files in os.walk(BUF):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            path = os.path.join(root, f)
            if os.path.islink(path):
                continue
            yield os.path.relpath(path, BUF), path


def main():
    for src, dest in COPIES:
        target = os.path.join(BUF, dest)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(os.path.join(PRIV, src), encoding="utf-8") as i, open(target, "w", encoding="utf-8") as o:
            o.write(i.read())
    stubs = os.path.join(PRIV, "link-stubs")
    for root, _, files in os.walk(stubs):
        for f in files:
            src = os.path.join(root, f)
            target = os.path.join(BUF, os.path.relpath(src, stubs))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(src, encoding="utf-8") as i, open(target, "w", encoding="utf-8") as o:
                o.write(i.read())
    for rel, content in FILE_STUBS.items():
        path = os.path.join(BUF, rel)
        if os.path.exists(path):
            with open(path, "w", encoding="utf-8") as o:
                o.write(content)
    for rel, start, end, replacement in SECTION_STUBS:
        path = os.path.join(BUF, rel)
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read()
        if start in text and end in text:
            text = text[:text.index(start)] + replacement + text[text.index(end):]
            with open(path, "w", encoding="utf-8") as o:
                o.write(text)
    problems = []
    for rel, path in text_files():
        try:
            text = open(path, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        new = scrub(rel, text)
        if new != text:
            with open(path, "w", encoding="utf-8") as o:
                o.write(new)
        for item in check(rel, new):
            problems.append(f"{rel}: {item}")
    if problems:
        print("SCRUB_CHECK_FAILED")
        print("\n".join(problems[:200]))
        sys.exit(1)
    print("SCRUB_OK")


if __name__ == "__main__":
    main()
