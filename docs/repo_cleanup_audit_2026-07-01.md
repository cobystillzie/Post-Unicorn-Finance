# Repo Cleanup Audit — 2026-07-01

Working-tree state vs last commit. Buckets are *recommendations* for our line-by-line review — nothing is acted on yet.

**Also pending: 9 unpushed commits** (`origin/main..HEAD`) — see chat.

## KEEP — CORE (10)

- `M` .gitignore
- `??` AGENTS.md
- `??` CLAUDE.md
- `M` data/evidence/ecosystem_entities.csv
- `M` data/evidence/entity_claims.csv
- `M` data/evidence/entity_intake_queue.csv
- `M` data/evidence/industry_entities.csv
- `??` data/evidence/liquidity_horizons.csv
- `M` data/evidence/schema.json
- `M` data/evidence/source_registry.csv

## KEEP — docs/site/tests (27)

- `M` docs/01_taxonomy.md
- `??` docs/atlas_blueprint.md
- `??` docs/post_unicorn_permanent_capital_atlas.md
- `??` docs/research/camel_philosophy_rubric.md
- `??` docs/research/classification_theory_2026-06-06.md
- `??` docs/research/classification_validation_2026-06-07.md
- `??` docs/research/emergent_post_unicorn_taxonomy_2026-06-01.md
- `??` docs/research/emergent_self_description_classification_2026-05-30.md
- `??` docs/research/ethan_guidance_2026-06-07.md
- `??` docs/research/ethan_reconciliation_questions_2026-06-08.md
- `??` docs/research/exit_framing_outliers_2026-06-19.md
- `??` docs/research/exit_framing_plan_and_codex_handoff_2026-06-19.md
- `??` docs/research/expansion_round1_studio_2026-06-08.md
- `??` docs/research/fast_exit_liquidity_lens_2026-06-27.md
- `??` docs/research/fast_exit_liquidity_lens_codex_reverification_2026-06-27.md
- `M` docs/research/post_unicorn_finance_research_dossier.md
- `??` docs/research/validation_smv_nimble_studio_2026-06-08.md
- `??` docs/research/venture_studio_definition_2026-06-01.md
- `??` docs/research/web_discovery_handoff_prompt.md
- `??` docs/superpowers/
- `??` site/Post-Unicorn-Finance-Atlas.pdf
- `??` site/post_unicorn_atlas_packet.html
- `??` site/post_unicorn_atlas_packet.pdf
- `M` site/post_unicorn_industry_atlas_cover_note.md
- `M` site/post_unicorn_industry_atlas_entities_claims.csv
- `M` site/post_unicorn_industry_atlas_packet.html
- `??` site/post_unicorn_permanent_capital_atlas.html

## REVIEW — script (17)

- `??` scripts/aplus_finalize_from_profiles.py
- `??` scripts/archive/
- `??` scripts/boundary_appendix_render.py
- `??` scripts/build_boundary_appendix.py
- `??` scripts/classification_synthesis_workflow.js
- `??` scripts/discovery_workflow.js
- `M` scripts/export_atlas_pdf.py
- `M` scripts/export_research_dossier.py
- `M` scripts/export_shareable_atlas.py
- `??` scripts/inject_and_promote.py
- `??` scripts/phase1_make_batches.py
- `M` scripts/publish_atlas_packet.py
- `??` scripts/render_asset_class_packet.py
- `M` scripts/research_agents.py
- `??` scripts/reverify_workflow.js
- `??` scripts/tier3_synthesize_taxonomy.py
- `??` scripts/verify_workflow.js

## REVIEW — artifact/snapshot (39)

- `??` data/evidence/atlas_asset_class_audit.csv
- `??` data/evidence/atlas_by_asset_class.csv
- `??` data/evidence/atlas_core_entities.csv
- `??` data/evidence/atlas_layer_2026-06-01.csv
- `??` data/evidence/audit_removed_2026-05-29.csv
- `??` data/evidence/case_studies.csv
- `??` data/evidence/classification_review_2026-05-28.csv
- `??` data/evidence/ecosystem_candidates_2026-05-29.csv
- `??` data/evidence/ecosystem_claims.csv
- `??` data/evidence/full_audit_2026-05-29.csv
- `??` data/evidence/funds_anchors.csv
- `??` data/evidence/funds_traditional_excluded.csv
- `??` data/evidence/funds_verified.csv
- `??` data/evidence/instruments.csv
- `??` data/evidence/junk_purge_log_2026-05-28.csv
- `??` data/evidence/manual_changes_2026-05-28.log
- `M` data/evidence/manual_changes_2026-06-01.log
- `??` data/evidence/manual_changes_2026-06-03.log
- `??` data/evidence/manual_changes_2026-06-06.log
- `??` data/evidence/manual_changes_2026-06-08.log
- `??` data/evidence/manual_changes_2026-06-17.log
- `??` data/evidence/manual_changes_2026-06-18.log
- `??` data/evidence/manual_changes_2026-06-19.log
- `??` data/evidence/movements.csv
- `??` data/evidence/orphan_claims_aplus_2026-06-01.csv
- `??` data/evidence/orphan_claims_purged_2026-05-28.csv
- `??` data/evidence/queue_audit_2026-05-29.csv
- `??` data/evidence/queue_audit_junk_purged_2026-05-29.csv
- `??` data/evidence/queue_duplicates_removed_2026-05-29.csv
- `??` data/evidence/removed_uvc_2026-06-01.csv
- `??` data/evidence/sample_audit_2026-05-28.csv
- `??` data/evidence/target_economy_2026-06-01.csv
- `??` docs/research/credibility_audit_2026-06-06.md
- `??` docs/research/liquidity_reaudit_2026-06-09.md
- `??` docs/research/reaudit_docket_2026-06-07.md
- `??` docs/research/tech_enabled_lens_reaudit_2026-06-01.md
- `??` scripts/audit_workflow.js
- `??` scripts/purge_atlas_junk.py
- `??` scripts/queue_audit_workflow.js

## REVIEW — other (3)

- `??` data/evidence/atlas_permanent_capital.csv
- `??` economic-impact-study/
- `??` liquidity/

## DELETE (removes file) (13)

- `D` scripts/inject_round2_firms.py
- `D` scripts/inject_round3_firms.py
- `D` scripts/inject_round4_firms.py
- `D` scripts/inject_round5_firms.py
- `D` scripts/inject_round6_firms.py
- `D` scripts/inject_round7_firms.py
- `D` scripts/queue_audit_2026-06-01.py
- `D` scripts/run-daily-publisher.ps1
- `D` scripts/run-hourly-research.ps1
- `D` scripts/run-intake-promotion.ps1
- `D` scripts/run-learning-loop.ps1
- `D` scripts/run-repo-hygiene.ps1
- `D` site/post_unicorn_industry_atlas_packet.pdf
