# Classification-Method Validation — 2026-06-07

Coarse signal-classifier vs assigned class, over the verified set. **This validates the method and
surfaces probable mislabels — it does not edit any class.** Caveat: SMV/Nimble overlap by design;
the reliable axis is Permanent vs growth (SMV/Nimble) vs Studio. Docket-flagged rows are marked
*pending* and excluded from the agreement rate.

## Summary
- Active rows judged: **87** (excl. 9 Reserved/Excluded, 14 docket-pending)
- Classifier agreement with human class: **70/87 = 80%**
- Probable mislabels (DISAGREE): **17**

## Probable mislabels (review)
| fund_id | assigned | classifier | signal scores |
|---|---|---|---|
| `4d-ventures` | Nimble | **Permanent** | Perm:2 Nimb:1 |
| `d2-fund` | Nimble | **Permanent** | Perm:1 Nimb:1 SMV:1 |
| `golden-section` | Nimble | **SMV** | Nimb:3 SMV:5 |
| `flying-founders` | Permanent | **Nimble** | Nimb:1 SMV:1 |
| `sureswift-capital` | Permanent | **Nimble** | Nimb:1 |
| `tiny` | Permanent | **SMV** | SMV:1 |
| `next-wave-partners` | Studio | **Permanent** | Perm:2 Nimb:1 Stud:2 |
| `mainsail-partners` | SMV | **Nimble** | Nimb:1 SMV:1 |
| `expedition-growth-capital` | SMV | **Nimble** | Nimb:1 |
| `invictus-growth` | SMV | **Nimble** | Nimb:2 SMV:1 |
| `updata-partners` | SMV | **Nimble** | Nimb:1 SMV:1 |
| `apex-point-equity` | SMV | **Nimble** | Nimb:1 SMV:1 |
| `argentum-group` | SMV | **Nimble** | Nimb:1 SMV:1 |
| `acadian-software` | SMV | **Nimble** | Nimb:3 |
| `nyo-capital` | SMV | **Nimble** | Nimb:2 SMV:2 |
| `edited-capital` | SMV | **Permanent** | Perm:1 SMV:1 |
| `gearbox-capital` | SMV | **Nimble** | Nimb:1 |

## Docket-pending rows (resolve first, then re-validate)
| fund_id | assigned | classifier |
|---|---|---|
| `pemba-capital` | SMV | Nimble |
| `buentrip-ventures` | Nimble | Nimble |
| `hasan-vc` | Nimble | Nimble |
| `henq` | Nimble | unclear |
| `saasholic` | Nimble | Studio |
| `sts-ventures` | Nimble | Nimble |
| `based-holdco` | Permanent | Permanent |
| `concepts-io` | Permanent | Permanent |
| `everroost` | Permanent | unclear |
| `noosa-labs` | Permanent | Permanent |
| `serent-capital` | SMV | Nimble |
| `tvc-capital` | SMV | SMV |
| `silversmith-capital` | SMV | Nimble |
| `tangle-ventures` | Permanent | Permanent |

## Method assessment
- A signal proxy reproduces the **Permanent vs growth vs Studio** split well; most DISAGREEs cluster
  on the **SMV-Nimble** boundary, confirming that is where the taxonomy needs the *deep* self-
  description cross-reference (instrument + outcome size), not keyword counts.
- Recommendation: the full classification phase should (1) resolve the docket, (2) then run a
  self-description pass that reads each firm's stated *instrument* (equity vs revenue-based vs
  acquisition) and *outcome size* to settle SMV vs Nimble, rather than vocabulary overlap.
