"""Gate 3 check: the pushed tab, as rendered, carries every text unit and link in update.md (G3-1, G3-4).

Run from the update folder, after render_pdf.swift:
    python3 -I <skill>/scripts/compare_tab.py --render <render dir> [--update update.md]
        [--feature ../../feature.json]

Finds the new tab's pages: the first page whose text holds update.md's H1, through the page before
the next page that holds another update's H1 (feature.json updates[].h1), or the last page.
Exits 2 when no page holds the H1: the export did not include the new tab, so stop and report it.

Checks every heading, paragraph, list item and table cell of update.md (markdown stripped, quote
marks normalized, whitespace ignored, since PDF text adds spaces around italic runs) appears in
those pages' text, and every link URL in
update.md appears in links.tsv on those pages. Prints links on the tab's pages that update.md
lacks as warnings (Danny may have added them). Exits 1 on any missing unit or link.
"""
import argparse
import glob
import json
import os
import re
import sys

LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")


def norm(s):
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u25cf", " ").replace("\u25cb", " ").replace("\u25a0", " ").replace("\\", "")
    return re.sub(r"\s+", " ", s).strip()


def plain(s):
    s = LINK.sub(lambda m: m.group(1), s)
    s = re.sub(r"\*\*|__|(?<!\w)[*_](?!\s)|(?<!\s)[*_](?!\w)|`", "", s)
    return norm(s)


def units(md):
    out = []
    for line in md.split("\n"):
        l = line.strip()
        if not l or re.match(r"^\|\s*:?-{3}", l) or l.startswith("> **Source:**"):
            continue
        if l.startswith("|"):
            out += [plain(c) for c in l.strip("|").split("|") if plain(c)]
            continue
        l = re.sub(r"^#+\s*", "", l)
        l = re.sub(r"^(?:[-*]|\d+\.)\s+", "", l)
        l = re.sub(r"^>\s*", "", l)
        if plain(l):
            out.append(plain(l))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", required=True)
    ap.add_argument("--update", default="update.md")
    ap.add_argument("--feature", default="../../feature.json")
    a = ap.parse_args()
    md = open(a.update).read()
    h1 = next((plain(l[2:]) for l in md.split("\n") if l.startswith("# ")), None)
    if not h1:
        print("compare_tab.py: update.md has no H1")
        return 2
    pages = sorted(glob.glob(os.path.join(a.render, "page-*.txt")))
    texts = [norm(open(p).read()) for p in pages]
    others = []
    if os.path.exists(a.feature):
        others = [norm(u.get("h1", "")) for u in json.load(open(a.feature)).get("updates", []) if u.get("h1") and norm(u["h1"]) != h1]
    start = next((i for i, t in enumerate(texts) if h1 in t), None)
    if start is None:
        print(f"compare_tab.py: no rendered page holds the H1 {h1!r}; the export did not include the new tab. Stop and report.")
        return 2
    end = len(texts)
    for i in range(start + 1, len(texts)):
        if any(o and o in texts[i] for o in others):
            end = i
            break
    tab_text = re.sub(r"\s+", "", " ".join(texts[start:end]))
    problems = []
    for u in units(md):
        if re.sub(r"\s+", "", u) not in tab_text:
            problems.append(f"missing text: {u[:100]!r}")
    tab_pages = set(range(start + 1, end + 1))
    rendered_links = set()
    lt = os.path.join(a.render, "links.tsv")
    if os.path.exists(lt):
        for line in open(lt).read().split("\n")[1:]:
            if "\t" in line:
                p, u = line.split("\t", 1)
                if p.isdigit() and int(p) in tab_pages:
                    rendered_links.add(u.strip().rstrip("/"))
    md_links = {m.group(2).rstrip("/") for m in LINK.finditer(md)}
    for u in sorted(md_links):
        if u not in rendered_links:
            problems.append(f"missing link: {u}")
    for u in sorted(rendered_links - md_links):
        print(f"WARN: link on the tab's pages that update.md lacks: {u}")
    print(f"compare_tab.py: tab on pages {start + 1} to {end} of {len(texts)}; "
          f"{len(units(md))} text units, {len(md_links)} links; {len(problems)} problem(s)")
    for p in problems:
        print(" -", p)
    print("PASS" if not problems else "FAIL")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
