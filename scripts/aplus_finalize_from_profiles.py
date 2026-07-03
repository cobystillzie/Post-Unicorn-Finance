"""
A+ corpus finalization — apply validated phase-3 self-description profiles to the atlas.

User-directed 2026-06-01 (scope choice 'A+ Finalize from profiles'):
  "apply the EXISTING, already-validated phase-3 profiles ... demote allocator_verdict=no
   entities to ECOSYSTEM, right-size Patient Capital's 198-entity LONG_HOLD catch-all via
   cluster_hints, fix clear misclassifications. NO new web verification."

Default mode is --preview (READ-ONLY): prints buckets + projected distribution and writes a
preview JSON. --apply mutates the authority CSVs (snapshot first, log every change, sweep
orphan claims, quarantine suggested-UVC rather than hard-delete).

Decision rules (per atlas entity, matched to its phase-3 profile by normalized name):
  protected (Capricorn, Generation Investment Mgmt) ......... keep (CLAUDE.md)
  no profile (recent round-10 promotions) .................. keep
  allocator_verdict == 'no'  OR suggested_class == ECOSYSTEM  demote -> ecosystem_entities.csv
  suggested_class == 'UVC' ................................. quarantine -> removed_uvc CSV (out of atlas)
  suggested_class in 7 atlas classes & != current:
        allocator_verdict == 'uncertain' .................. flag only (no move on weak evidence)
        else ............................................. reclassify in place
  suggested_class in ('', 'uncertain') .................... flag (if Patient Capital) else keep
  else (suggested == current) ............................. keep

Run from project root:
    python scripts/aplus_finalize_from_profiles.py --preview
    python scripts/aplus_finalize_from_profiles.py --apply
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
from collections import Counter
from pathlib import Path

EVID = Path("data/evidence")
ENT = EVID / "industry_entities.csv"
CLAIMS = EVID / "entity_claims.csv"
ECO = EVID / "ecosystem_entities.csv"
LOG = EVID / "manual_changes_2026-06-01.log"
PROFDIR = Path("data/runtime/phase3_profiles")
PREVIEW = Path("data/runtime/aplus_reclass_preview_2026-06-01.json")
QUARANTINE = EVID / "removed_uvc_2026-06-01.csv"
ORPHAN_LOG = EVID / "orphan_claims_aplus_2026-06-01.csv"
SNAPDIR = Path("data/runtime/snapshot_pre_aplus_2026-06-01")
TODAY = "2026-06-01"

ATLAS_CLASSES = {
    "Patient Capital", "Portfolio Capital", "SMV", "LMV",
    "Search/ETA", "Sovereign Capital", "Venture Studio",
}
PROTECTED = {"capricorn investment group", "generation investment management"}
# Weak-evidence markers: a suggested-UVC call resting on these is downgraded to a flag,
# never a removal (CLAUDE.md: "unverifiable != fabricated; do not purge thin pages").
WEAK_UVC = re.compile(r"\b(thin|appears|likely|unclear|seems|possibly|may be|might be)\b", re.I)


def norm(n: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", (n or "").lower())).strip()


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def load_profiles() -> dict[str, dict]:
    m: dict[str, dict] = {}
    for f in sorted(os.listdir(PROFDIR)):
        if not f.endswith(".json"):
            continue
        d = json.load(open(PROFDIR / f, encoding="utf-8"))
        for p in d.get("profiles", []):
            if isinstance(p, dict) and p.get("name"):
                m.setdefault(norm(p["name"]), p)
    return m


def load_locked() -> set[str]:
    """Names already adjudicated by a NEWER in-session manual change (phase4a/b/c, round-10,
    Q-audit). These decisions are authoritative over the older phase-3 profiles, so A+ must
    not undo them. Parsed from manual_changes log lines of form '... | <name> | ...'."""
    locked: set[str] = set()
    if not LOG.exists():
        return locked
    for line in open(LOG, encoding="utf-8"):
        if "|" not in line:
            continue
        parts = line.split("|")
        if len(parts) >= 2:
            cand = parts[1].strip()
            if cand and len(cand) < 80 and "SUMMARY" not in cand and "=" not in cand:
                locked.add(norm(cand))
    return locked


def decide(row: dict, prof: dict | None, locked: set[str]) -> tuple[str, str, str]:
    """Return (action, target_class, reason). action in keep/reclass/demote_ecosystem/remove_uvc/flag."""
    nn = norm(row.get("name", ""))
    cur = row.get("primary_asset_class", "")
    if nn in PROTECTED:
        return "keep", cur, "protected per CLAUDE.md (never reclassify)"
    if cur == "Venture Studio":
        return "keep", cur, "Venture Studio assigned this session; phase-3 profiles predate this class and cannot suggest it"
    if nn in locked:
        return "keep", cur, "newer in-session manual reclassification is authoritative over older phase-3 profile"
    if not prof:
        return "keep", cur, "no phase-3 profile (recent round-10 promotion)"
    sug = (prof.get("suggested_class") or "").strip()
    av = (prof.get("allocator_verdict") or "").strip()
    reason = re.sub(r"\s+", " ", (prof.get("reason") or "")).strip()[:240]
    if av == "no" or sug == "ECOSYSTEM":
        return "demote_ecosystem", "ECOSYSTEM", f"allocator_verdict={av or 'n/a'}; suggested={sug or 'n/a'}; {reason}"
    if sug == "UVC":
        if av == "uncertain" or WEAK_UVC.search(reason):
            return "flag", cur, f"suggested UVC but weak/thin evidence — kept+flagged not removed; {reason}"
        return "remove_uvc", "UVC", f"suggested UVC (classic unicorn VC, out of atlas scope); {reason}"
    if sug in ATLAS_CLASSES and sug != cur:
        if av == "uncertain":
            return "flag", cur, f"suggested {sug} but allocator_verdict uncertain — no move on weak evidence; {reason}"
        return "reclass", sug, reason
    if sug in ("", "uncertain"):
        act = "flag" if cur == "Patient Capital" else "keep"
        return act, cur, f"suggested={sug or 'blank'}; {reason}"
    return "keep", cur, "suggested_class == current"


def build_plan():
    profs = load_profiles()
    locked = load_locked()
    rows = read_csv(ENT)
    plan = []
    for r in rows:
        prof = profs.get(norm(r.get("name", "")))
        action, target, reason = decide(r, prof, locked)
        plan.append({
            "entity_id": r.get("entity_id", ""),
            "name": r.get("name", ""),
            "current_class": r.get("primary_asset_class", ""),
            "action": action,
            "target_class": target,
            "allocator_verdict": (prof or {}).get("allocator_verdict", "NO_PROFILE"),
            "cluster_hint": (prof or {}).get("cluster_hint", ""),
            "reason": reason,
        })
    return rows, plan


def summarize(plan: list[dict]) -> None:
    actions = Counter(p["action"] for p in plan)
    print("=== ACTION BUCKETS ===")
    for k, v in actions.most_common():
        print(f"  {v:>4}  {k}")
    proj = Counter()
    for p in plan:
        if p["action"] in ("keep", "flag"):
            proj[p["current_class"]] += 1
        elif p["action"] == "reclass":
            proj[p["target_class"]] += 1
    print("\n=== PROJECTED ATLAS DISTRIBUTION ===")
    print(f"  TOTAL {sum(proj.values())}")
    for k, v in proj.most_common():
        print(f"  {v:>4}  {k}")
    print("\n=== RECLASS (current -> target) ===")
    moves = Counter((p["current_class"], p["target_class"]) for p in plan if p["action"] == "reclass")
    for (a, b), v in moves.most_common():
        print(f"  {v:>4}  {a} -> {b}")
    for act in ("demote_ecosystem", "remove_uvc"):
        sample = [p for p in plan if p["action"] == act]
        print(f"\n=== {act}: {len(sample)} ===")
        for p in sample[:12]:
            print(f"   - {p['name']} (was {p['current_class']}) :: {p['reason'][:88]}")


def do_preview() -> None:
    rows, plan = build_plan()
    print(f"Atlas entities: {len(rows)}\n")
    summarize(plan)
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    json.dump(plan, open(PREVIEW, "w", encoding="utf-8"), indent=1)
    print(f"\nPreview written: {PREVIEW}")
    print("READ-ONLY — no CSVs were modified. Re-run with --apply to execute.")


def snapshot() -> None:
    SNAPDIR.mkdir(parents=True, exist_ok=True)
    csvs = list(EVID.glob("*.csv"))
    for p in csvs:
        shutil.copyfile(p, SNAPDIR / p.name)
    print(f"Snapshot of {len(csvs)} evidence CSVs -> {SNAPDIR}")


def append_log(msg: str) -> None:
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def do_apply() -> None:
    rows, plan = build_plan()
    snapshot()
    by_id = {p["entity_id"]: p for p in plan}
    ent_fields = list(rows[0].keys())

    kept_rows, demoted_rows, removed_rows = [], [], []
    reclassed = 0
    removed_ids: set[str] = set()
    append_log(f"\n[{TODAY}] ===== A+ FINALIZE FROM PROFILES =====")

    for r in rows:
        p = by_id.get(r.get("entity_id", ""))
        act = p["action"] if p else "keep"
        if act == "reclass":
            old = r["primary_asset_class"]
            r = dict(r)
            r["primary_asset_class"] = p["target_class"]
            note = f"[A+ {TODAY}] reclass {old}->{p['target_class']}: {p['reason']}"
            r["notes"] = (r.get("notes", "") + " | " + note).strip(" |")
            reclassed += 1
            append_log(f"[{TODAY}] RECLASS | {r['name']} | {old} -> {p['target_class']} | A+ suggested_class | {p['reason'][:160]}")
            kept_rows.append(r)
        elif act == "flag":
            r = dict(r)
            r["notes"] = (r.get("notes", "") + f" | [A+ {TODAY} FLAG] {p['reason']}").strip(" |")
            kept_rows.append(r)
        elif act == "demote_ecosystem":
            demoted_rows.append(r)
            removed_ids.add(r.get("entity_id", ""))
            append_log(f"[{TODAY}] ECOSYSTEM | {r['name']} | {r['primary_asset_class']} -> ECOSYSTEM | A+ non-allocator | {p['reason'][:160]}")
        elif act == "remove_uvc":
            removed_rows.append(r)
            removed_ids.add(r.get("entity_id", ""))
            append_log(f"[{TODAY}] REMOVE_UVC | {r['name']} | {r['primary_asset_class']} -> quarantine | A+ suggested UVC | {p['reason'][:160]}")
        else:
            kept_rows.append(r)

    write_csv(ENT, kept_rows, ent_fields)

    if demoted_rows:
        eco = read_csv(ECO)
        eco_fields = list(eco[0].keys()) if eco else ent_fields
        existing = {norm(e.get("name", "")) for e in eco}
        add = [d for d in demoted_rows if norm(d.get("name", "")) not in existing]
        write_csv(ECO, eco + add, eco_fields)
        print(f"Ecosystem: +{len(add)} (now {len(eco) + len(add)})")

    if removed_rows:
        write_csv(QUARANTINE, removed_rows, ent_fields)
        print(f"UVC quarantined: {len(removed_rows)} -> {QUARANTINE}")

    claims = read_csv(CLAIMS)
    cfields = list(claims[0].keys())
    keep_ids = {r.get("entity_id", "") for r in kept_rows}
    orphans = [c for c in claims if c.get("entity_id", "") in removed_ids and c.get("entity_id", "") not in keep_ids]
    survivors = [c for c in claims if c.get("entity_id", "") not in removed_ids or c.get("entity_id", "") in keep_ids]
    if orphans:
        prev = read_csv(ORPHAN_LOG)
        write_csv(ORPHAN_LOG, prev + orphans, cfields)
        write_csv(CLAIMS, survivors, cfields)
        print(f"Swept {len(orphans)} orphan claims (logged -> {ORPHAN_LOG})")

    append_log(f"[{TODAY}] A+ SUMMARY reclass={reclassed} demote_ecosystem={len(demoted_rows)} remove_uvc={len(removed_rows)} orphan_claims_swept={len(orphans)}")
    print(f"\nApplied: reclass={reclassed} demote_ecosystem={len(demoted_rows)} remove_uvc={len(removed_rows)} orphans={len(orphans)}")
    print(f"Atlas now: {len(kept_rows)} entities")
    for k, v in Counter(r["primary_asset_class"] for r in kept_rows).most_common():
        print(f"  {v:>4}  {k}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Mutate authority CSVs (default is read-only preview).")
    args = ap.parse_args()
    do_apply() if args.apply else do_preview()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
