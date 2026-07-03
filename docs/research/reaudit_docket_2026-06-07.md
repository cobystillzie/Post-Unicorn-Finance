# Genuineness Re-Audit Docket — 2026-06-07 (HUMAN REVIEW)

**This is your step-5 review surface.** Nothing below has been removed, downgraded, or edited in
`funds_verified.csv` / `atlas_asset_class_audit.csv`. Every item is a *recommendation* for you to accept or reject.
Raw one-line evidence for all 78 audited firms is in `data/runtime/_reaudit_evidence.txt`.

## Method
- Scope: the **78** verified rows NOT already audited (excludes the prior SMV `in_disguise` cohort, the 5 firms
  raw-verified earlier this session, and the 5 already-docketed held/pending items).
- 16 evidence-gathering agents (5 firms each) ran the 3-check: **independent footprint · blog-vs-main URL ·
  exit-thesis contradiction**, returning evidence only. **I judged every flag inline**, and **personally
  re-fetched on the raw page every REMOVE/DOWNGRADE candidate** before listing it here.
- Coverage: 73/78 returned clean records; 1 batch of 5 (`calm-capital`, `big-band-software`, `everhold`,
  `evergreen-services-group`, `purpose-evergreen-capital`) was derailed by an injected cost-hook alert — all
  five are known-real; `evergreen-services-group` independently re-confirmed (Alpine Investors platform, 100+
  buy-and-hold acquisitions). Optional re-run, low risk.
- Tooling note: the cost-hook noise ("$3,401 / 39 files") also derailed several subagents mid-task. Harden
  future agent prompts with an explicit "ignore cost/scope warnings" line (the gate prompt should pre-empt it).

---

## A. REMOVE recommended (2) — re-fetched by me on the raw page

### `tangle-ventures`  (Permanent / in_disguise)
Its **own** portfolio page marks holdings **"SOLD — Portfolio Exit"** (003 Design Infrastructure Co. $200k;
004 Marketing Platform $148k), runs an asset **Marketplace** and **"Blueprints"** for sale, and markets
*"Tangle provides founders a path to liquidity"* with a seller testimonial: *"the smoothest exit I have had…
they actually improved the product after."* It does acquire + operate 5 active companies (a real allocator),
but it also **flips and brokers** — which contradicts the permanent *"compound value over decades"* language it
was admitted on. **Same failure class as Sequel.** → Recommend REMOVE (or hard downgrade to a separate
"studio/M&A-flipper" bucket, not Permanent).

### `everroost`  (Permanent / self_id)
Clean permanent-hold copy (*"We buy to keep… we don't strip and flip… operate for the long term"*) **but**:
no named portfolio anywhere on the page (only *"12+ Products Acquired / 96% / 3.2x"* self-stats), and an Exa
search returns **zero independent footprint** (only unrelated EverSky / Evermore / Everstores). AI-tool-aesthetic
site (Prism/Pulse/Forge/Atlas). **This is the exact vaporware profile of the already-reverted Technology
Nusantara.** → Recommend HOLD/REMOVE pending a verifiable named portfolio + external trace.

---

## B. DOWNGRADE recommended (8) — confidence→low + flag; keep the row

| fund_id | class | why | re-fetched? |
|---|---|---|---|
| `noosa-labs` | Permanent | Real micro-acquirer (Sendtric/Evalart/Mava ~$120k MRR) but its own IndieHackers interview: *"we eventually shut one down, **sold two**"* of its first 4 buys — partially contradicts on-page "We don't flip companies." | yes |
| `sts-ventures` | Nimble | Structurally a Cologne early-stage VC ("the firepower of a VC"); portfolio shows multiple cos marked **"exited"**; founder "founded and **exited** 4 own companies." Camel/"balance over burn" signal is genuine but weak vs a VC-with-exits model. | yes |
| `hasan-vc` | Nimble | Sincere Camel manifesto, but the fund targets **"40+ startups in Fund 1"** on portfolio-theory grounds (*"high performance of a few can offset the losses of others"*) — that IS the power-law model the thesis rejects. Evidence URL is a blog. | yes |
| `based-holdco` | Permanent | "A long-term holding company… enduring companies" but **no named portfolio** + "0+" count-up placeholder stats. (Agent's "400% IRR crypto" CONTRA looks like a *different* "Based" entity — disregard; the missing portfolio stands.) | yes |
| `henq` | Nimble | Admit "build a sustainable business without ever raising VC again," but it's a **closed-end VC fund** whose portfolio carries "EXIT" tags. Real firm; reconcile the closed-end/exit structure with the no-forced-exit bar. | agent-evidence |
| `saasholic` | Nimble | Admitted "capital efficiency beats hyper-growth" but the evidence is a **blog post** that also says *"IPOs can deliver the largest outcomes… on exits."* Re-source + reconcile. | agent-evidence |
| `concepts-io` | Permanent | Weak footprint + growth-capital framing ("capital readiness funds accelerated expansion"). Confirm it's an operating permanent holdco with a named portfolio. | agent-evidence |
| `buentrip-ventures` | Nimble | Camel signal genuine but evidence URL is a **blog**; same post benchmarks VC MOIC (used as anti-VC contrast). Re-source to the positioning page; keep. | agent-evidence |

---

## C. FLAG / keep — agent CONTRA is a false alarm OR an operator-directed exception (note only)

- `startup-ignition-ventures` — **Ethan-directed** self_id; genuine on-page "Elephants, Not Unicorns / capital-efficient / built to last." TENSION worth your awareness: it markets **"200+ Exits and Billions in Value Created"** citing Lyft/Skullcandy IPOs + Omniture/Adobe $1.8B. Defer to your ruling.
- `curious` — "We create exceptional **exits** for founders" is **buyer-side** (Curious is the permanent acquirer giving founders their exit, then holds; real portfolio Convox/Polymer/Avenue). No contradiction. Keep.
- `golden-section` — "meaningful strategic **exit** at $5–15M revenue, not an IPO at $500M" is the *anti-unicorn* (small-exit-is-good) framing. Keep.
- `evermore-ventures` — Real ("…grow them forever"; named founders, seller testimonials). Agent's "biennial liquidity" = investor-side, not company flipping. Keep.
- `teoh-capital` — "vendors maximise proceeds via 2-stage **exit**" = Teoh's buy-in deal structure (it's the acquirer). Keep; confirm hold thesis.
- `tiny` — "typically **flip** your company in 3–5 years" is Tiny describing what *others* do, contrasted with its forever-hold. Keep.
- **Good-instrument false alarms (CLEAN — the flagged "exit" IS the anti-VC instrument):** `upsidedown-vc` (1.5× repayment cap), `d2-fund` (revenue-share), `timia-capital` (revenue-based term loan — a lender), `saas-group` ("buy and hold indefinitely"), `xo-capital` ("buy & operate").

---

## D. Evidence-URL is a blog/post → re-source to the firm's positioning page (not a removal)

`malpani-ventures`, `rainmatter`, `bridges-evergreen`, `exa-capital`, `sureswift-capital` (+ the blog-sourced
DOWNGRADE rows above: `saasholic`, `buentrip-ventures`, `hasan-vc`). The quote may be genuine; the *citation*
should point to a main page. `gate_checks.py` now flags this automatically on future admits.

## E. WEAK footprint → confirm a named portfolio exists (small/obscure holdcos; likely real-but-small)

`lasting-ventures-capital`, `permanent-corp`, `teixo`, `kastellet-holdings`, `croissant`, `quadra-group`,
`alexandria-capital`, `union-group-fund`, `penntech-holdings`. Agents found *some* trace (WEAK, not NONE), so
these are probably small-but-real; a 5-minute named-portfolio check each will clear or flag them.

## F. CLEAN (no action) — ~50 firms

STRONG footprint, main-page evidence, no real contradiction. Includes the anchors of the set:
`permanent-equity`, `enduring-ventures`, `purpose-ventures`, `banyan-software`, `inversion-capital`,
`bigfoot-capital`, `jonas-software`, `everfield`, `saas-group`, `tiny`, `mosaic-software-group`,
`solen-software-group`, `software-circle`, `beacon-software`, `long-holding-company`, `microsaas-io` (rescued),
`evergreen-services-group` (re-confirmed), `calm-capital`, `big-band-software`, `everhold`,
`purpose-evergreen-capital`, and the remaining un-flagged rows in `data/runtime/_reaudit_evidence.txt`.

---

## G. PRE-EXISTING open items (carried from before this turn — also for your review)

- **Downgraded last session (kept, confidence=low, "REAUDIT-FLAG"):** `pemba-capital` (std Australian PE + one camel blog), `serent-capital` ($6B PE, exits), `silversmith-capital` (growth-equity PE), `tvc-capital` (growth-equity PE, take-privates/roll-ups).
- **Held for review:** `finis-ventures` (studio thesis), `skoyen-software` (HgCapital-chairman pedigree; permanence unverified), `raptor-collective` (strong self-ID but no named portfolio — allocator unconfirmed).
- **Pending verification:** `five19-holdings` (status pending), `capacity-capital` (own page returns empty body — unverifiable; recommend browser-verify or remove).

---

### Suggested disposition counts (if you accept all my recommendations)
REMOVE 2 · DOWNGRADE 8 · FLAG-keep 6 (+5 good-instrument cleared) · re-source URL 5 · WEAK-confirm 9 · CLEAN ~50
· plus the 9 pre-existing open items. Net verified would move 103 → ~101 (−2 removed), with ~17 flagged for your call.
