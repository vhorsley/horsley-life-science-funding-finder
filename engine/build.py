#!/usr/bin/env python3
"""Build the Life Science Funding Finder.

Reads   catalog/programs/*.json  (one program per file, or a list per file)
        catalog/notes.json       (per-stage tips and the "What's changed" panel)
Writes  data/programs.json       (the whole catalog as one list)
        index.html               (single self-contained page with the data embedded)

Usage:  python3 engine/build.py [--check]
"""
import json, glob, os, re, sys, datetime

# Programs in the first release are not tagged New; later additions are.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENG = os.path.join(ROOT, "engine")
TODAY = datetime.date.today().isoformat()

TYPES = {"Research grant", "Career award", "Postdoc fellowship", "Graduate fellowship",
         "Undergraduate program", "Prize", "Pilot / seed", "Training & travel",
         "Translational / startup", "Resources & compute"}
FIELDS = {"all", "cell", "stem", "neuro", "imm", "cancer", "gen", "micro", "struct", "comp", "eco",
          "trans", "derm", "aging", "metab", "repro", "fib", "cardio", "bioeng"}
STAGES = {"ug", "gr", "pd", "tt", "ten"}
# disease/topic tags shown as chips; keep in sync with TOPICS in engine/template.html
TOPICS = {"melanoma", "blood-cancer", "pancreatic", "prostate", "pediatric-cancer", "lupus", "scleroderma",
          "psoriasis", "arthritis", "ibd", "cf", "alzheimers", "parkinsons", "mental-health", "eye",
          "diabetes", "liver", "menopause", "pregnancy", "plant", "global-health"}
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
KEEP = ["id", "n", "f", "c", "s", "d", "dt", "a", "e", "u", "fields", "stages", "us", "nom", "cd", "t",
        "yale", "unv", "added", "checked"]


def load_rows():
    rows = []
    for fp in sorted(glob.glob(os.path.join(ROOT, "catalog", "programs", "*.json"))):
        x = json.load(open(fp, encoding="utf-8"))
        rows.extend(x if isinstance(x, list) else [x])
    return rows


def clean(x, problems):
    pid = x.get("id", "?")
    r = {k: x[k] for k in KEEP if k in x and x[k] not in (None, "", [])}
    r.setdefault("d", None)
    if not r.get("n") or not r.get("u", "").startswith("https://"):
        problems.append(f"{pid}: missing name or https link"); return None
    if r.get("c") not in TYPES:
        problems.append(f"{pid}: unknown type {r.get('c')!r}")
    r["fields"] = [f for f in x.get("fields", []) if f in FIELDS] or ["all"]
    bad = [t for t in x.get("t", []) if t not in TOPICS]
    if bad:
        problems.append(f"{pid}: unknown topic {bad}")
    r["t"] = [t for t in x.get("t", []) if t in TOPICS]
    if not r["t"]:
        r.pop("t")
    r["stages"] = [s for s in x.get("stages", []) if s in STAGES]
    if not r["stages"]:
        problems.append(f"{pid}: no career stage"); return None
    r["us"], r["nom"] = bool(x.get("us")), bool(x.get("nom"))
    if x.get("cd"):
        r["cd"] = True
    else:
        r.pop("cd", None)
    d = r.get("d")
    if d and not ISO.match(str(d)):
        problems.append(f"{pid}: bad date {d}"); r["d"] = None
    if r.get("s") not in ("open", "rolling", "watch"):
        r["s"] = "watch"
    # a passed deadline: the program recurs, so keep it on watch with no date
    if r["d"] and r["d"] < TODAY:
        r["s"], r["d"] = "watch", None
    if r["s"] == "open" and not r["d"]:
        r["s"] = "watch"
    y = x.get("yale")
    if isinstance(y, dict) and (y.get("t") or y.get("d")):
        yd = y.get("d") if y.get("d") and ISO.match(str(y.get("d"))) else None
        r["yale"] = {"d": yd, "t": y.get("t", ""), "u": y.get("u", "") if str(y.get("u", "")).startswith("https://") else ""}
    else:
        r.pop("yale", None)
    return r


def css():
    """Shared styles, with theme tokens added for dark mode."""
    tpl = open(os.path.join(ENG, "styles.css"), encoding="utf-8").read()
    return "<style>\n" + tpl + "\n</style>"


def main(check=False):
    problems, seen, seen_u, out = [], set(), {}, []
    for x in load_rows():
        r = clean(x, problems)
        if not r:
            continue
        if r["id"] in seen:
            problems.append(f"{r['id']}: duplicate id (kept first)"); continue
        seen.add(r["id"]); out.append(r)
    out.sort(key=lambda r: r["id"])
    notes = json.load(open(os.path.join(ROOT, "catalog", "notes.json"), encoding="utf-8"))
    checked = max((r.get("checked", "") for r in out), default=TODAY)
    snap = {"programs": out, "status": {"lastChecked": checked, "launch": "2026-11-05"}, "notes": notes, "updated": TODAY}
    for p in problems:
        print("note:", p)
    print(f"{len(out)} programs")
    if check:
        return
    json.dump(out, open(os.path.join(ROOT, "data", "programs.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    html = open(os.path.join(ENG, "template.html"), encoding="utf-8").read()
    payload = json.dumps(snap, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = (html.replace("/*CSS*/", css())
                .replace("/*EXPORT*/", open(os.path.join(ENG, "export_mod.js"), encoding="utf-8").read())
                .replace("{{snapshot}}", payload))
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    # artifact.html: the same page without the document wrapper, for publishing as a claude.ai artifact
    body = html.split("<body>", 1)[1].rsplit("</body>", 1)[0]
    head = re.search(r"<title>.*?</title>\s*<meta name=\"description\"[^>]*>", html, re.S).group(0)
    open(os.path.join(ROOT, "artifact.html"), "w", encoding="utf-8").write(
        head + '\n<meta name="claude:viewport-fit-sides" content="cover">\n' + body)
    json.dump({"built": TODAY, "programs": len(out)}, open(os.path.join(ROOT, "version.json"), "w"))


if __name__ == "__main__":
    main("--check" in sys.argv)
