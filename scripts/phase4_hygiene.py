"""
Phase 4 Atlas Hygiene — execute the 8-step plan from Tier 3 taxonomy critique.

Steps executed:
  1. SNAPSHOT evidence CSVs to data/runtime/snapshot_pre_phase4_2026-06-01/
  2. BUILD hygiene lists (purge / ecosystem / reclassify / venture-studio)
  3. APPLY purge  (remove UVC + clear non-allocators from industry_entities.csv)
  4. SWEEP orphan entity_claims (FK trap per CLAUDE.md)
  5. MOVE ecosystem entities to ecosystem_entities.csv
  6. RECLASSIFY remaining flagged entities
  7. CREATE Venture Studio class; migrate 30 Portfolio Capital studios
  8. LOG everything; print summary

Run from project root:
    python scripts/phase4_hygiene.py
"""

import csv, json, os, shutil, glob, re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────
ROOT              = Path(".")
EVIDENCE          = ROOT / "data" / "evidence"
RUNTIME           = ROOT / "data" / "runtime"
SNAPSHOT_DIR      = RUNTIME / "snapshot_pre_phase4_2026-06-01"
PROFILE_DIR       = RUNTIME / "phase3_profiles"
CLUSTER_DIR       = RUNTIME / "phase3_cluster_findings"

ENTITIES_CSV      = EVIDENCE / "industry_entities.csv"
CLAIMS_CSV        = EVIDENCE / "entity_claims.csv"
ECOSYSTEM_CSV     = EVIDENCE / "ecosystem_entities.csv"
LOG_FILE          = EVIDENCE / "manual_changes_2026-06-01.log"
ORPHAN_LOG        = EVIDENCE / "orphan_claims_purged_2026-06-01.csv"

TODAY = "2026-06-01"
VENTURE_STUDIO_CLASS = "Venture Studio"

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def norm_name(n: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", (n or "").lower())).strip()

def domain_of(url: str) -> str:
    try:
        d = urlparse((url or "").strip().lower()).netloc.replace("www.", "")
        return d.split(":")[0].strip("/")
    except Exception:
        return ""

def read_csv(path: Path) -> list:
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def write_csv(path: Path, rows: list, fieldnames=None):
    if not rows:
        return
    fns = fieldnames or list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def append_log(msg: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


# ══════════════════════════════════════════════
# STEP 1 — SNAPSHOT
# ══════════════════════════════════════════════
def step1_snapshot():
    print("\n[STEP 1] Snapshotting evidence CSVs ...")
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    for src in EVIDENCE.glob("*.csv"):
        dst = SNAPSHOT_DIR / src.name
        shutil.copy2(src, dst)
    count = len(list(SNAPSHOT_DIR.glob("*.csv")))
    print(f"  Snapshot complete: {count} files -> {SNAPSHOT_DIR}")
    append_log(f"[{TODAY}] SNAPSHOT: {count} CSVs -> {SNAPSHOT_DIR}")


# ══════════════════════════════════════════════
# STEP 2 — BUILD HYGIENE LISTS
# ══════════════════════════════════════════════
def step2_build_lists():
    print("\n[STEP 2] Building hygiene lists ...")

    # Load all profiles
    profiles = []
    for fp in sorted(PROFILE_DIR.glob("batch_*_profiles.json")):
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
        batch = data if isinstance(data, list) else data.get("profiles", [])
        profiles.extend(batch)
    print(f"  Profiles loaded: {len(profiles)}")

    # Load all cluster reclassification flags
    flags = []
    for fp in sorted(CLUSTER_DIR.glob("cluster_*.json")):
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
        cn = data.get("class_name", "")
        for flag in data.get("reclassification_flags", []):
            flags.append({
                "name":         flag.get("name", "").strip(),
                "current_class":flag.get("current_class", cn).strip(),
                "should_be":    flag.get("should_be", "").strip(),
                "why":          flag.get("why", ""),
                "source_cluster": cn,
            })
    print(f"  Cluster reclass flags loaded: {len(flags)}")

    # Load Portfolio Capital cluster for Venture Studio members
    vs_members = set()
    pc_path = CLUSTER_DIR / "cluster_Portfolio_Capital.json"
    if pc_path.exists():
        with open(pc_path, encoding="utf-8") as f:
            pc_data = json.load(f)
        for sc in pc_data.get("sub_clusters", []):
            if "studio" in sc.get("sub_cluster_id", "").lower() or "studio" in sc.get("label", "").lower():
                for m in sc.get("members", []):
                    name = m.get("name", m) if isinstance(m, dict) else m
                    vs_members.add(norm_name(str(name)))
    print(f"  Venture Studio members: {len(vs_members)}")

    # Build keyed sets
    uvc_flag_names = {norm_name(f["name"]) for f in flags if f["should_be"] in ("UVC", "REMOVE")}
    eco_flag_names = {norm_name(f["name"]) for f in flags if f["should_be"] == "ECOSYSTEM"}

    # Purge = UVC-flagged by cluster OR allocator_verdict=no AND suggested UVC/ECOSYSTEM
    purge_names = set(uvc_flag_names)
    for p in profiles:
        nn = norm_name(p["name"])
        if p.get("allocator_verdict") == "no" and p.get("suggested_class") in ("ECOSYSTEM", "UVC"):
            purge_names.add(nn)

    # Ecosystem = ECOSYSTEM-flagged, minus hard-purge UVC entries
    eco_names = set(eco_flag_names)
    for p in profiles:
        nn = norm_name(p["name"])
        if p.get("allocator_verdict") == "no" and p.get("suggested_class") == "ECOSYSTEM":
            eco_names.add(nn)
    eco_names -= uvc_flag_names  # UVC goes to purge, not ecosystem

    # Reclassify = flags to valid allocator classes
    VALID_ALLOC = {
        "Patient Capital", "Portfolio Capital", "LMV", "SMV",
        "Search/ETA", "Sovereign Capital", "Venture Studio"
    }
    reclass_map = {}
    for f in flags:
        if f["should_be"] in VALID_ALLOC:
            nn = norm_name(f["name"])
            if nn not in purge_names and nn not in eco_names:
                reclass_map[nn] = {
                    "name": f["name"],
                    "from_class": f["current_class"],
                    "to_class": f["should_be"],
                    "why": f["why"],
                }

    print(f"  PURGE list:        {len(purge_names)}")
    print(f"  ECOSYSTEM list:    {len(eco_names)}")
    print(f"  RECLASSIFY list:   {len(reclass_map)}")
    print(f"  VENTURE STUDIO:    {len(vs_members)}")

    return purge_names, eco_names, reclass_map, vs_members, profiles


# ══════════════════════════════════════════════
# STEPS 3 + 5 + 6 + 7 — MUTATE industry_entities.csv
# ══════════════════════════════════════════════
def step3567_mutate_entities(purge_names, eco_names, reclass_map, vs_members):
    print("\n[STEPS 3/5/6/7] Mutating industry_entities.csv ...")
    rows = read_csv(ENTITIES_CSV)
    fieldnames = list(rows[0].keys()) if rows else []

    purged_rows = []
    eco_moved_rows = []
    reclassed_rows = []
    vs_migrated_rows = []
    kept_rows = []

    for row in rows:
        nn = norm_name(row.get("name", "") or row.get("legal_name", ""))
        cur_class = row.get("primary_asset_class", "").strip()

        # Priority 1: purge
        if nn in purge_names:
            purged_rows.append(row)
            continue

        # Priority 2: ecosystem move
        if nn in eco_names:
            eco_moved_rows.append(row)
            continue

        # Priority 3: venture studio migration
        if nn in vs_members and cur_class in ("Portfolio Capital", "LMV"):
            old = cur_class
            row = dict(row)
            row["primary_asset_class"] = VENTURE_STUDIO_CLASS
            vs_migrated_rows.append({"name": row.get("name",""), "from": old, "to": VENTURE_STUDIO_CLASS})
            kept_rows.append(row)
            continue

        # Priority 4: reclassify
        if nn in reclass_map:
            entry = reclass_map[nn]
            old = cur_class
            row = dict(row)
            row["primary_asset_class"] = entry["to_class"]
            reclassed_rows.append({
                "name": row.get("name",""),
                "from": old,
                "to": entry["to_class"],
                "why": entry["why"][:120]
            })
            kept_rows.append(row)
            continue

        kept_rows.append(row)

    write_csv(ENTITIES_CSV, kept_rows, fieldnames)

    print(f"  Purged:           {len(purged_rows)}")
    print(f"  Ecosystem moved:  {len(eco_moved_rows)}")
    print(f"  Reclassified:     {len(reclassed_rows)}")
    print(f"  Studio migrated:  {len(vs_migrated_rows)}")
    print(f"  Final kept:       {len(kept_rows)}")

    for r in purged_rows:
        append_log(f"[{TODAY}] PURGE | {r.get('name','')} | class={r.get('primary_asset_class','')} | reason=UVC_or_non_allocator")
    for r in eco_moved_rows:
        append_log(f"[{TODAY}] ECOSYSTEM | {r.get('name','')} | class={r.get('primary_asset_class','')} | moved to ecosystem_entities.csv")
    for rc in reclassed_rows:
        append_log(f"[{TODAY}] RECLASS | {rc['name']} | {rc['from']} -> {rc['to']} | {rc['why']}")
    for vs in vs_migrated_rows:
        append_log(f"[{TODAY}] VENTURE_STUDIO | {vs['name']} | {vs['from']} -> {vs['to']}")

    return purged_rows, eco_moved_rows, reclassed_rows, vs_migrated_rows, kept_rows


# ══════════════════════════════════════════════
# STEP 4 — SWEEP ORPHAN entity_claims
# ══════════════════════════════════════════════
def step4_sweep_orphans(purged_rows, eco_moved_rows):
    print("\n[STEP 4] Sweeping orphan entity_claims ...")
    if not CLAIMS_CSV.exists():
        print("  entity_claims.csv not found — skipping")
        return

    removed_names = {
        norm_name(r.get("name","") or r.get("legal_name",""))
        for r in purged_rows + eco_moved_rows
    }
    removed_ids = {
        r.get("entity_id", r.get("id","")).strip()
        for r in purged_rows + eco_moved_rows
        if r.get("entity_id") or r.get("id")
    }

    claims = read_csv(CLAIMS_CSV)
    orphan_claims = []
    clean_claims = []

    for c in claims:
        eid = c.get("entity_id","").strip()
        ename_norm = norm_name(c.get("entity_name", c.get("name", "")))
        is_orphan = (eid and eid in removed_ids) or (ename_norm and ename_norm in removed_names)
        (orphan_claims if is_orphan else clean_claims).append(c)

    if orphan_claims:
        fns = list(orphan_claims[0].keys())
        write_csv(ORPHAN_LOG, orphan_claims, fns)
        if clean_claims:
            write_csv(CLAIMS_CSV, clean_claims, list(clean_claims[0].keys()))
        print(f"  Orphan claims swept: {len(orphan_claims)} -> {ORPHAN_LOG.name}")
        append_log(f"[{TODAY}] ORPHAN_SWEEP | {len(orphan_claims)} orphan claims removed -> {ORPHAN_LOG}")
    else:
        print("  No orphan claims found.")


# ══════════════════════════════════════════════
# STEP 5b — EXTEND ecosystem_entities.csv
# ══════════════════════════════════════════════
def step5_extend_ecosystem(eco_moved_rows):
    print("\n[STEP 5] Extending ecosystem_entities.csv ...")
    existing = read_csv(ECOSYSTEM_CSV) if ECOSYSTEM_CSV.exists() else []
    existing_names = {norm_name(r.get("name","") or r.get("legal_name","")) for r in existing}

    new_entries = []
    for r in eco_moved_rows:
        nn = norm_name(r.get("name","") or r.get("legal_name",""))
        if nn not in existing_names:
            new_entries.append(r)
            existing_names.add(nn)

    if new_entries:
        all_eco = existing + new_entries
        fns = list(all_eco[0].keys())
        write_csv(ECOSYSTEM_CSV, all_eco, fns)
        print(f"  Added {len(new_entries)} new ecosystem entries (total: {len(all_eco)})")
        append_log(f"[{TODAY}] ECOSYSTEM_EXTEND | +{len(new_entries)} entries -> {ECOSYSTEM_CSV.name}")
    else:
        print("  No new ecosystem entries to add.")


# ══════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════
def summary():
    print("\n" + "="*60)
    print("PHASE 4 HYGIENE COMPLETE")
    print("="*60)
    entities = read_csv(ENTITIES_CSV)
    class_counts = {}
    for r in entities:
        c = r.get("primary_asset_class", "")
        class_counts[c] = class_counts.get(c, 0) + 1
    print(f"\nAtlas entities: {len(entities)}")
    print("\nClass distribution:")
    for k, v in sorted(class_counts.items(), key=lambda x: -x[1]):
        print(f"  {k:<32} {v:>4}")
    claims_count = len(read_csv(CLAIMS_CSV)) if CLAIMS_CSV.exists() else 0
    eco_count = len(read_csv(ECOSYSTEM_CSV)) if ECOSYSTEM_CSV.exists() else 0
    print(f"\nentity_claims:      {claims_count}")
    print(f"ecosystem_entities: {eco_count}")
    print(f"\nLog: {LOG_FILE}")
    print(f"Snapshot: {SNAPSHOT_DIR}")


# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════
if __name__ == "__main__":
    append_log(f"\n{'='*60}\n[{TODAY}] PHASE 4 HYGIENE RUN START\n{'='*60}")

    step1_snapshot()
    purge_names, eco_names, reclass_map, vs_members, profiles = step2_build_lists()
    purged, eco_moved, reclassed, vs_migrated, kept = step3567_mutate_entities(
        purge_names, eco_names, reclass_map, vs_members
    )
    step4_sweep_orphans(purged, eco_moved)
    step5_extend_ecosystem(eco_moved)
    summary()

    append_log(
        f"[{TODAY}] PHASE 4 HYGIENE RUN COMPLETE "
        f"| purged={len(purged)} eco={len(eco_moved)} "
        f"reclass={len(reclassed)} studio={len(vs_migrated)}"
    )
    print("\nDone.")
