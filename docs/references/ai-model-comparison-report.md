# List of Info on GW Events Using Various AI Models (Leg 2 working notes)

> Extracted text, not the original PDF. Source: "Comparison Report.pdf", shared in conversation 2026-08-22. This is the working document for Leg 2 (AI-Model Comparison Study) — see `legs/leg2_ai_comparison/` and `thesis/latex/chapters/04_results_and_discussion.tex` Section "AI-Model Comparison Study".

## Models evaluated (free tier)

- **ChatGPT** — reliable, general-purpose, strong reasoning.
- **Gemini** — fast, web-oriented, multimodal.
- **Claude** — accurate, safe, long-context.
- **DeepSeek** — efficient, analytical, technical.
- **Grok** — rapid, conversational, real-time.

## Prompting framework: RTCROS

- **R**ole — assign the role
- **T**ask — give the task
- **C**ontext — explain the context
- **R**easoning — state what's being checked and why
- **O**utput — specify the format
- **S**topping — tell the model when to stop

## Prompt check 1 (initial ~50-event batch)

Prompt asked each model to evaluate a list of GW events (GW150914 through GW200322_091133, ~50 events) and report: whether it could identify all as BBH mergers, whether it could provide catalog references, whether it could access/cite papers, whether it could provide a clean m₁/m₂/chirp-mass comparison, and any other reliable parameters.

### Results (as recorded, free-tier access, no browsing tools)

| Model | Identified all as BBH? | Reference? | Access papers? | Clean m1/m2/chirp-mass comparison? | Other parameters |
|---|---|---|---|---|---|
| ChatGPT | No (partial — some ambiguous, need catalog verification) | Partial (can name GWTC releases/key papers from memory, not exact DOIs without browsing) | No | Partial (formatted tables, approximate remembered values, no accuracy guarantee) | Can report spins, mass ratio, detector-/source-frame masses, distance, redshift, SNR, sky localization format — reliability varies, needs source verification |
| Gemini | No (correctly identifies non-BBH events like BNS/NSBH) | Yes (GWTC catalogs) | Yes | Yes (constructs comparison table from catalog data) | Yes |
| Claude | Partial (identified most as BBH, can't confirm all individually) | Yes | Partial | Partial (found parameters for specific notable events, e.g. GW190412: 30/8 M☉, GW190521: 85/66 M☉) | Limited (distance, spin, mass ratio for some events, incomplete coverage) |
| DeepSeek | Partially | No, but can mention catalogs | No | Partially (for well-known events) | Limited (e.g. distance, SNR) |
| Grok | Yes | Yes (e.g. GWTC-1/2/3) | Yes | Yes | Yes (e.g. effective spin, distance) |

**Note (project observation, not in the original document):** this table is exactly the kind of evidence used in the thesis to argue that unaided LLM recall of GW parameters is inconsistent across models and should not be trusted without retrieval grounding — see the GW Pathfinder design rationale in `legs/leg3_pathfinder/docs/pathfinder_design_draft.md`.

## Next step (as planned in the original document)

Expand to the full list of ~300 known GW events (BBH, BNS, NSBH), including events reported by groups outside official LVK publications (e.g. Institute for Advanced Study, Alex Nitz's group). Planned columns: discovering organisation/institute, event time and coordinates, classification, observing run, catalog membership, detection pipeline, confidence (FAR), resources/references, one-paragraph description, remark.

**Project decision (2026-08-19):** this expanded ~300-event batch is not being reused for chirp-mass estimator validation — see `legs/leg1_estimation/docs/feasibility_draft.md` limitations. A fresh, independently-run comparison batch (~50-80 events) is planned for Leg 2 instead (sprint Days 6-7), per explicit user decision to keep the two legs' data separate.
