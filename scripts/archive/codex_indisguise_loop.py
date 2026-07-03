#!/usr/bin/env python3
"""
codex_indisguise_loop.py  -- hand-off harness (2026-06-19)

Continuously discovers IN-DISGUISE SMV/Nimble capital allocators by driving the
Codex CLI (gpt-5.5, danger-full-access) one round at a time, until the vein is
extinguished (N consecutive rounds with ZERO new strict-gate survivors).

The LOOP + dedup + stop-condition live here (deterministic). Codex does the
discovery + web-verification + adversarial confirm each round, on ChatGPT quota.

WHAT THIS DOES NOT DO: it never edits the atlas. Survivors land only in the
review pile under data/runtime/codex_indisguise/ for operator approval.

Methodology (identical to the Claude pilot that produced the 6 good examples):
  STRICT all-four gate, ALL required:
    1. small fund   (< ~$75M)
    2. small checks (< ~$3M)
    3. stated sub-unicorn target (ARR goal / profitability / $50-500M exit / niche leadership)
    4. regional or vertical-niche market (smaller TAM)
  PLUS: real firm + capital allocator + tech-enabled.
  PLUS: a second-skeptic confirm pass per survivor (try to prove fund>$75M /
        pro-unicorn / not-an-allocator); keep only if it survives.
  Every firm must be web-verified with an EXACT verbatim quote. No hallucination,
  no typosquats, no parked/dead domains. Empty array > one unverified firm.

Usage:
    python scripts/codex_indisguise_loop.py            # run until dry
    python scripts/codex_indisguise_loop.py --max-rounds 40
    python scripts/codex_indisguise_loop.py --dry-stop 5

Stop it any time with Ctrl-C; state persists, so re-running resumes.
"""
import argparse, csv, json, os, re, shutil, subprocess, sys, time, io
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN_DIR = os.path.join(REPO, "data", "runtime", "codex_indisguise")
ROUNDS_DIR = os.path.join(RUN_DIR, "rounds")
BLOCKLIST = os.path.join(RUN_DIR, "blocklist.json")
SEED_BLOCKLIST = os.path.join(REPO, "data", "runtime", "_blocklist_2026-06-19b.json")
SEED_PILE = os.path.join(REPO, "data", "runtime", "review_pile_indisguise_2026-06-19.json")
PILE_JSON = os.path.join(RUN_DIR, "review_pile_codex.json")
PILE_MD = os.path.join(RUN_DIR, "review_pile_codex.md")
LOG = os.path.join(RUN_DIR, "log.txt")
STATE = os.path.join(RUN_DIR, "state.json")
REJECTED_JSON = os.path.join(RUN_DIR, "rejected_duplicates.json")
REPO_KNOWN_JSON = os.path.join(RUN_DIR, "repo_known_names.json")
KNOWN_CSV_NAME_COLUMNS = {
    "name", "firm_name", "entity_name", "company_name", "fund_name",
    "display_name", "canonical_name",
}

# region x vertical x instrument x disguise angles; cycled one-per-round
ANGLES = [
    "CEE (Poland/Czechia/Hungary/Romania) small B2B SaaS or fintech VC, sub-$75M funds, $0.25-3M checks, DFI/PFR/EBRD backed.",
    "Nordic (Sweden/Denmark/Finland/Norway) micro-VC and capital-efficient seed funds with niche regional theses.",
    "Baltics (Estonia/Latvia/Lithuania) small tech seed funds with sub-unicorn / profitable-growth framing.",
    "Iberia (Spain & Portugal) vertical-SaaS / fintech small funds writing small checks into domestic-first markets.",
    "Italy & Southern Europe revenue-based financing or small-equity funds for SaaS/eCommerce SMBs.",
    "DACH Mittelstand-tech small funds backing profitable B2B software (not blitzscale).",
    "Africa (West & East) fintech / digital-infrastructure seed funds, DFI-backed, small fund size, sub-unicorn targets.",
    "India / South Asia small SaaS-focused micro-funds targeting capital-efficient profitable companies.",
    "Southeast Asia vertical-SaaS or fintech small funds (sub-$75M) with regional-leadership (not global-unicorn) theses.",
    "Latin America (Brazil/Mexico/Colombia) capital-efficient or revenue-based tech funds for profitable regional winners.",
    "US non-coastal / Midwest / Southeast micro-funds backing capital-efficient vertical software.",
    "Global revenue-based financing / non-dilutive growth funds for small SaaS (Nimble-lean), quick realization.",
    "Govtech / regtech / public-sector SaaS small funds (procurement TAM structurally capped).",
    "Healthtech / health-IT small funds targeting profitability or mid-size acquisition exits, not unicorns.",
    "DISGUISE-HUNTER A: funds using unicorn/scale/blitzscale/exit language on their site BUT whose fund size + check size + niche market make power-law math impossible. Quote both the conventional language AND the structural figures.",
    "Climate / energy / industrial-tech SMALL regional funds with ARR or mid-size-exit targets.",
    "Agritech / foodtech / supplychain small vertical funds in emerging or regional markets.",
    "Logistics / mobility vertical-SaaS small funds with niche, bounded markets.",
    "Edtech / workforce / HR-tech small funds targeting sustainable niche outcomes.",
    "Legaltech / proptech / insurtech vertical micro-funds writing sub-$3M checks.",
    "Cybersecurity / devtools niche small funds with disciplined capital and bounded verticals.",
    "Family-office-backed small tech investment vehicles deploying own capital into profitable niche software.",
    "MENA / Gulf small tech funds with regional-champion (not global-unicorn) theses.",
    "Australia / New Zealand capital-efficient small tech funds with niche domestic focus.",
    "Canada regional small tech funds (non-Toronto/Vancouver) backing profitable vertical SaaS.",
    "Japan / Korea / Taiwan small tech funds with niche B2B and sub-unicorn outcomes.",
    "Accelerator-funds or studios that take small equity in niche tech and target sustainable exits.",
    "Structured / redeemable-equity or shared-earnings funds for SaaS (Earnest/Calm-style but NOT already known ones).",
    "DISGUISE-HUNTER B: emerging-market or regional funds that claim 'the next [region] unicorn' yet write tiny checks from tiny funds into capped markets -- the rhetoric vs the math mismatch.",
    "Vertical-AI applied small funds backing profitable niche AI tools (not foundation-model moonshots).",
]

PROMPT_TMPL = """You are a rigorous capital-markets research agent. Find IN-DISGUISE SMV/Nimble \
capital allocators for the Post-Unicorn Finance atlas review pile.

DEFINITION. An in-disguise fund is a CAPITAL ALLOCATOR (deploys its own or LPs' capital via \
equity/debt/revenue-share/acquisition, OR builds-and-owns its own companies) that is STRUCTURALLY \
sub-unicorn even though its website may use ordinary VC language (scale, exit, market leadership). \
The FUND MATH -- not the slogans -- classifies it.

STRICT ALL-FOUR GATE (every one REQUIRED, each backed by a verbatim quote):
  1. small fund   < ~$75M
  2. small checks < ~$3M
  3. a stated SUB-UNICORN target (ARR goal / profitability / $50-500M exit / niche leadership)
  4. regional or vertical-niche market (structurally smaller TAM)
ALSO REQUIRED: real live firm + genuine allocator + tech-enabled.

SECOND-SKEPTIC CONFIRM (per survivor): before you keep a firm, actively try to KILL it -- prove ONE of:
(a) fund/AUM is actually > ~$75M; (b) it actually has an explicit unicorn/power-law/global-scale-exit \
thesis; (c) it is not really an allocator (marketplace/broker/advisory/no-capital accelerator/solo maker). \
Keep it ONLY if you cannot establish any of those.

ANTI-HALLUCINATION (non-negotiable): WEB-VERIFY every firm -- open its real website (web search and/or \
curl) and capture an EXACT verbatim quote. NEVER invent firms. Reject typosquats, vaporware, AI-prototype \
sites, and parked/dead domains. IT IS BETTER TO RETURN AN EMPTY ARRAY THAN TO INCLUDE ONE FIRM YOU COULD \
NOT OPEN AND QUOTE. Reject pure PE, search funds/ETA, marketplaces, brokers, non-allocators, solo indie makers.

THIS ROUND'S ANGLE: {angle}

DO NOT return any firm whose name appears in this CURRENT REVIEW PILE list (already accepted in this run):
{avoid}

The full parent-side duplicate blocklist is stored at:
{blocklist_path}
You may inspect it if useful, but the parent harness will enforce it deterministically after your round.

OUTPUT: write a JSON array to EXACTLY this path: {outpath}
Each element: {{"name","website","hq_region","fund_size","check_size","target_signal","market_niche",\
"instrument","proposed_class"("SMV"|"Nimble"),"confidence"("high"|"med"|"low"),"evidence"(verbatim quotes \
backing all four signals + allocator + tech),"disguise_note"}}. Include ONLY firms that pass the strict \
gate AND survive the second-skeptic confirm. Aim for 2-6 genuinely strong, fully-verified firms; fewer is \
fine. Write the file even if the array is empty ([]). Output nothing else of consequence; the file is the deliverable.
"""


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def log(msg):
    line = f"[{now()}] {msg}"
    print(line, flush=True)
    with io.open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_json(path, default):
    try:
        with io.open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def norm_name(name):
    text = str(name or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def save_json(path, obj):
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def mojibake_score(text):
    return sum(text.count(marker) for marker in ("Ã", "Â", "â", "�"))


def fix_text(text):
    if not isinstance(text, str) or not mojibake_score(text):
        return text
    try:
        candidate = text.encode("latin-1").decode("utf-8")
    except Exception:
        return text
    return candidate if mojibake_score(candidate) < mojibake_score(text) else text


def fix_obj_text(obj):
    if isinstance(obj, str):
        return fix_text(obj)
    if isinstance(obj, list):
        return [fix_obj_text(x) for x in obj]
    if isinstance(obj, dict):
        return {k: fix_obj_text(v) for k, v in obj.items()}
    return obj


def codex_command():
    return shutil.which("codex.cmd") or shutil.which("codex.exe") or shutil.which("codex")


def collect_json_names(obj):
    names = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in KNOWN_CSV_NAME_COLUMNS and isinstance(value, str):
                n = norm_name(value)
                if n:
                    names.add(n)
            names.update(collect_json_names(value))
    elif isinstance(obj, list):
        for value in obj:
            names.update(collect_json_names(value))
    return names


def collect_repo_known_names():
    """Collect known names from durable evidence/intake surfaces, excluding this run dir."""
    names = set()
    evidence_dir = os.path.join(REPO, "data", "evidence")
    if os.path.isdir(evidence_dir):
        for fn in os.listdir(evidence_dir):
            if not fn.lower().endswith(".csv"):
                continue
            path = os.path.join(evidence_dir, fn)
            try:
                with io.open(path, newline="", encoding="utf-8-sig") as fh:
                    reader = csv.DictReader(fh)
                    if not reader.fieldnames:
                        continue
                    fields = [f for f in reader.fieldnames if norm_name(f) in KNOWN_CSV_NAME_COLUMNS]
                    if not fields and len(reader.fieldnames) >= 2:
                        fields = [reader.fieldnames[1]]
                    for row in reader:
                        for field in fields:
                            n = norm_name(row.get(field, ""))
                            if n and len(n) >= 3:
                                names.add(n)
            except Exception:
                continue

    runtime_dir = os.path.join(REPO, "data", "runtime")
    runtime_seed_files = [
        "_blocklist_2026-06-19b.json",
        "_indisguise_pilot_2026-06-19.json",
        "review_pile_indisguise_2026-06-19.json",
        "firms_final_consolidated.json",
        "firms_wave1_consolidated.json",
    ]
    for fn in runtime_seed_files:
        path = os.path.join(runtime_dir, fn)
        if not os.path.exists(path):
            continue
        names.update(collect_json_names(load_json(path, None)))

    save_json(REPO_KNOWN_JSON, sorted(names))
    return names


def existing_round_numbers():
    nums = []
    if not os.path.isdir(ROUNDS_DIR):
        return nums
    for fn in os.listdir(ROUNDS_DIR):
        m = re.fullmatch(r"round_(\d+)\.json", fn)
        if m:
            nums.append(int(m.group(1)))
    return nums


def write_pile_markdown():
    pile = load_json(PILE_JSON, [])
    lines = ["# In-Disguise SMV/Nimble -- Codex Continuous Discovery (review pile)", "",
             "STRICT all-four gate + second-skeptic confirm. REVIEW PILE ONLY -- not in the atlas.", "",
             f"Total: {len(pile)} firms.  Gate legend not abbreviated; see evidence per firm.", "",
             "| # | Firm | Class | Conf | Round | Link |", "|---|------|-------|------|-------|------|"]
    for i, f in enumerate(pile, 1):
        lines.append("| %d | %s | %s | %s | %s | %s |" % (
            i, f.get("name", "?"), f.get("proposed_class", "?"), f.get("confidence", "?"),
            f.get("_round", "?"), f.get("website", "")))
    lines += ["", "---", ""]
    for i, f in enumerate(pile, 1):
        lines.append("## %d. %s -- %s (%s)" % (i, f.get("name", "?"), f.get("proposed_class", "?"), f.get("confidence", "?")))
        lines.append("- Site: %s" % f.get("website", ""))
        lines.append("- Region/Niche: %s / %s" % (f.get("hq_region", "?"), f.get("market_niche", "?")))
        lines.append("- Fund: %s | Check: %s | Target: %s | Instrument: %s" % (
            f.get("fund_size", "?"), f.get("check_size", "?"), f.get("target_signal", "?"), f.get("instrument", "?")))
        lines.append("- Evidence: %s" % str(f.get("evidence", "")).replace("\n", " "))
        if f.get("disguise_note"):
            lines.append("- Disguise: %s" % str(f.get("disguise_note", "")).replace("\n", " "))
        lines.append("")
    with io.open(PILE_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def init_state():
    os.makedirs(ROUNDS_DIR, exist_ok=True)
    repo_known = collect_repo_known_names()
    if not os.path.exists(BLOCKLIST):
        seed = load_json(SEED_BLOCKLIST, [])
        save_json(BLOCKLIST, sorted({str(x).strip().lower() for x in seed if str(x).strip()}))
        log(f"seeded blocklist with {len(seed)} names from {os.path.basename(SEED_BLOCKLIST)}")
    blocklist = set(load_json(BLOCKLIST, []))
    before = len(blocklist)
    blocklist.update(repo_known)
    if len(blocklist) != before:
        save_json(BLOCKLIST, sorted(blocklist))
        log(f"merged {len(repo_known)} repo-known names into blocklist ({before}->{len(blocklist)})")
    if not os.path.exists(PILE_JSON):
        seed_pile = load_json(SEED_PILE, [])
        seeded = []
        if isinstance(seed_pile, list):
            for f in seed_pile:
                if not isinstance(f, dict) or not str(f.get("name", "")).strip():
                    continue
                item = dict(f)
                item.setdefault("_round", 0)
                item.setdefault("_found", "2026-06-19 Claude pilot")
                item.setdefault("fund_size", "see evidence")
                item.setdefault("check_size", "see evidence")
                item.setdefault("target_signal", "see evidence")
                item.setdefault("market_niche", "see evidence")
                item.setdefault("instrument", "see evidence")
                seeded.append(item)
        save_json(PILE_JSON, seeded)
        blocklist = set(load_json(BLOCKLIST, []))
        blocklist.update(str(f.get("name", "")).strip().lower() for f in seeded if str(f.get("name", "")).strip())
        save_json(BLOCKLIST, sorted(blocklist))
        log(f"seeded review pile with {len(seeded)} firms from {os.path.basename(SEED_PILE)}")
        write_pile_markdown()
    elif not os.path.exists(PILE_MD):
        write_pile_markdown()
        log("rebuilt missing markdown review pile from JSON state")


def run_codex_round(rnd, angle, avoid_names, timeout):
    outpath = os.path.join(ROUNDS_DIR, f"round_{rnd:03d}.json")
    if os.path.exists(outpath):
        os.remove(outpath)
    avoid = ", ".join(sorted(avoid_names))
    prompt = PROMPT_TMPL.format(
        angle=angle,
        avoid=avoid,
        blocklist_path=BLOCKLIST.replace("\\", "/"),
        outpath=outpath.replace("\\", "/"),
    )
    cmd = codex_command()
    if not cmd:
        log(f"round {rnd}: codex executable not found")
        return None
    log(f"round {rnd}: {os.path.basename(cmd)} exec -- angle: {angle[:70]}...")
    stdout_path = os.path.join(ROUNDS_DIR, f"round_{rnd:03d}.stdout.txt")
    try:
        result = subprocess.run(
            [cmd, "exec", "--cd", REPO, "--skip-git-repo-check", "-"],
            input=prompt, text=True, encoding="utf-8",
            timeout=timeout, cwd=REPO,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        with io.open(stdout_path, "w", encoding="utf-8", errors="replace") as fh:
            fh.write(result.stdout or "")
        if result.returncode != 0:
            log(f"round {rnd}: codex exited with code {result.returncode}; stdout={stdout_path}")
            return None
    except subprocess.TimeoutExpired:
        log(f"round {rnd}: TIMEOUT after {timeout}s")
        return None
    except Exception as e:
        log(f"round {rnd}: codex error: {e}")
        return None
    if not os.path.exists(outpath):
        log(f"round {rnd}: codex produced no output file")
        return None
    found = load_json(outpath, None)
    if not isinstance(found, list):
        log(f"round {rnd}: output file is not a JSON array")
        return None
    found = fix_obj_text(found)
    save_json(outpath, found)
    return found


def append_pile(new_firms, rnd):
    pile = load_json(PILE_JSON, [])
    for f in new_firms:
        f = fix_obj_text(f)
        f["_round"] = rnd
        f["_found"] = now()
        pile.append(f)
    save_json(PILE_JSON, pile)
    write_pile_markdown()


def repair_duplicate_round_entries():
    repo_known = set(load_json(REPO_KNOWN_JSON, [])) or collect_repo_known_names()
    pile = load_json(PILE_JSON, [])
    kept = []
    rejected = load_json(REJECTED_JSON, [])
    removed = []
    for f in pile:
        n = norm_name(f.get("name", ""))
        if f.get("_round", 0) and n in repo_known:
            item = dict(f)
            item["_rejected_at"] = now()
            item["_rejected_reason"] = "duplicate_existing_repo_or_seed_name"
            rejected.append(item)
            removed.append(f.get("name", "?"))
            continue
        kept.append(f)
    if removed:
        save_json(PILE_JSON, kept)
        save_json(REJECTED_JSON, rejected)
        write_pile_markdown()
        blocklist = set(load_json(BLOCKLIST, []))
        blocklist.update(norm_name(x) for x in removed)
        save_json(BLOCKLIST, sorted(blocklist))
        log(f"repair: removed {len(removed)} duplicate round survivor(s) from pile: {', '.join(removed)}")
    return removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-stop", type=int, default=5, help="consecutive empty rounds = extinguished")
    ap.add_argument("--max-rounds", type=int, default=60, help="hard backstop against runaway")
    ap.add_argument("--timeout", type=int, default=2400, help="per-round codex timeout (s)")
    args = ap.parse_args()

    init_state()
    removed_duplicates = repair_duplicate_round_entries()
    blocklist = set(load_json(BLOCKLIST, []))
    pile = load_json(PILE_JSON, [])
    state = load_json(STATE, {})
    if removed_duplicates and not state:
        last_existing = max(existing_round_numbers() + [0])
        accepted_in_last = any(int(f.get("_round", 0) or 0) == last_existing for f in pile)
        if last_existing and not accepted_in_last:
            state = {
                "last_round": last_existing,
                "next_round": last_existing + 1,
                "consecutive_empty": 1,
                "updated_at": now(),
                "pile_count": len(pile),
                "note": "initialized after duplicate-only validation round repair",
            }
            save_json(STATE, state)
            log(f"repair: initialized state as empty round {last_existing} after duplicate-only cleanup")
    last_seen_round = max([f.get("_round", 0) for f in pile] + existing_round_numbers() + [state.get("last_round", 0), 0])
    rnd = max(last_seen_round + 1, int(state.get("next_round", 1) or 1))
    consec_empty = int(state.get("consecutive_empty", 0) or 0)
    log(f"START dry-stop={args.dry_stop} max-rounds={args.max_rounds} blocklist={len(blocklist)} pile={len(pile)} first-round={rnd}")

    while consec_empty < args.dry_stop and rnd <= args.max_rounds:
        angle = ANGLES[(rnd - 1) % len(ANGLES)]
        prompt_avoid_names = {str(f.get("name", "")).strip() for f in load_json(PILE_JSON, []) if str(f.get("name", "")).strip()}
        found = run_codex_round(rnd, angle, prompt_avoid_names, args.timeout)
        if found is None:
            log(f"round {rnd}: infrastructure/model failure; stopping without counting this as an empty discovery round")
            break
        fresh = []
        skipped = []
        for f in found:
            if not isinstance(f, dict):
                continue
            k = norm_name(f.get("name", ""))
            if not k or k in blocklist:
                if k:
                    skipped.append(f.get("name", k))
                continue
            blocklist.add(k)
            fresh.append(f)
        if fresh:
            append_pile(fresh, rnd)
            save_json(BLOCKLIST, sorted(blocklist))
            consec_empty = 0
            log(f"round {rnd}: +{len(fresh)} NEW survivors -> pile now {len(load_json(PILE_JSON, []))} "
                f"({', '.join(x.get('name','?') for x in fresh)})")
        else:
            consec_empty += 1
            save_json(BLOCKLIST, sorted(blocklist))
            log(f"round {rnd}: 0 new (consecutive empty {consec_empty}/{args.dry_stop})")
        if skipped:
            log(f"round {rnd}: skipped {len(skipped)} duplicate/known candidate(s): {', '.join(skipped)}")
        save_json(STATE, {
            "last_round": rnd,
            "next_round": rnd + 1,
            "consecutive_empty": consec_empty,
            "updated_at": now(),
            "pile_count": len(load_json(PILE_JSON, [])),
        })
        rnd += 1

    total = len(load_json(PILE_JSON, []))
    if consec_empty >= args.dry_stop:
        log(f"DONE: vein extinguished after {consec_empty} consecutive empty rounds. Total survivors: {total}.")
    else:
        log(f"STOP: hit max-rounds backstop. Total survivors: {total}. Re-run to continue.")


if __name__ == "__main__":
    main()
