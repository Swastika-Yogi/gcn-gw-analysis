# Note: Accelerating Posterior Inference (Pulsar Light Curves)

> Extracted/summarized text, not the original PDF. Source: "Note-Posterior Inference.pdf", shared in conversation 2026-08-22. Reading notes on: "Accelerating Posterior Inference from Pulsar Light Curves via Learned Latent Representations and Local Simulator-Guided Optimization" (Taiyebah, Siddik, Bhattacharjee, Oyen, De, Olmschenk, Kalapotharakos; 16 Feb 2026; Astrophysics + ML).

**Project status: evaluated and explicitly judged out of scope for this thesis's timeline** — see `legs/leg3_pathfinder/docs/pathfinder_design_draft.md`. Kept here for the literature review and to document why it wasn't adopted.

## Problem, idea, result

- **Problem:** posterior inference from pulsar light curves via MCMC is slow (can take ~24 hours).
- **Main idea:** use a pretrained encoder to retrieve similar past simulations and start optimization near good parameters, instead of random MCMC exploration.
- **Main result:** ~120x speedup vs MCMC (24 hours → 12 minutes) on PSR J0030+0451, with mean NLL after refinement (-42,124.30) very close to the MCMC result (-42,125.14).

## Method

- **Input:** simulated light curves (64 numbers); **parameters:** 11 physical pulsar parameters; **target:** posterior p(θ|x*) given a real observed light curve x*.
- **Pretrain a masked U-Net:** mask parts of simulated light curves, train the network to reconstruct the missing parts. Keep only the encoder afterward (frozen) — turns a light curve into an embedding vector believed to capture meaningful structure.
- **Parameter degeneracy:** different parameter values can produce near-identical light curves, so the true posterior is multimodal, disconnected, high-dimensional, and geometrically messy — the reason plain MCMC is slow (random exploration, discovers each mode slowly).
- **Two-stage approach instead of pure MCMC sampling:**
  1. **Global retrieval** — embed the observation, retrieve k nearest-neighbor simulations in the learned latent space, use their parameters as an empirical posterior approximation (preserves multimodality, unlike direct regression which collapses to a single point).
  2. **Local refinement** — hill-climb from the retrieved candidates using Poisson negative log-likelihood, block hill climbing, 2^P perturbations per step, to sharpen the posterior without collapsing modes.

## Why not adopted for this project's GW work

Mapped onto GW: light curve → gravitational waveform, pulsar parameters → masses/spins, simulation bank → waveform bank, retrieval-based posterior approximation instead of direct parameter prediction. Judged impractical for this thesis given: much higher dimensionality than the pulsar case; GW likelihood evaluation is still expensive, and hill-climbing needs many such evaluations; a GW waveform simulation bank of the scale this method assumes (millions of examples) isn't available at this project's scope; and this project's GW Pathfinder concept is explicitly a catalog-level retrieval/chatbot system, not a parameter-estimation pipeline — adopting this method would mean substantially expanding scope beyond what a two-week thesis sprint can support. Flagged as a possible direction for the longer-term research-paper extension (Master Plan M15) if GW Pathfinder is later expanded toward actual parameter estimation.
