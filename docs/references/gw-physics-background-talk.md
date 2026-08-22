# Gravitational Waves from an Introductory Physics Perspective (background talk)

> Extracted/summarized text, not the original PDF. Source: "Talk_draft.pdf", shared in conversation 2026-08-22. Slide deck by Naresh Adhikari, PhD (Fayetteville Technical Community College), 20 November 2025. General GW-physics background — candidate source material for `thesis/latex/chapters/02_literature_review.tex` Section "GW Fundamentals".

## What it covers

A from-first-principles derivation of the inspiral "chirp" signal shape using only Newtonian gravity, conservation of energy, and basic calculus (no general relativity), using GW150914 (two ~30 M☉ black holes, 1.3 billion light-years away, detected 14 September 2015) as the motivating example.

**Outline:** the chirp physics challenge → Newtonian setup → derivation (dimensional analysis, work-energy theorem, solving for frequency evolution) → comparing the derived formula to real LIGO data → astrophysics applications (probing neutron stars/exotic matter) → current research frontiers.

## Derivation summary

1. **Adiabatic approximation:** the orbit shrinks far more slowly than one orbital period (T_shrink ≫ T_orbit), so at any instant the system can be treated as a stable Newtonian orbit ("snapshot").
2. **Newtonian snapshot** (equal masses M, separation 2r): force balance gives v² = GM/(4r); total energy E_tot = −GM²/(4r) ∝ −r⁻¹.
3. **Why quadrupole radiation:** monopole (mass) and dipole (momentum) radiation both vanish by conservation laws, so gravitational radiation must come from the (mass) quadrupole moment — i.e., the system's asymmetry.
4. **Power radiated** (dimensional analysis): using the "Planck luminosity" L₀ = c⁵/G ≈ 3.6×10⁵² W and the compactness ratio (R_schwarzschild/r), P_GW ≈ (c⁵/G)(R_sch/r)⁵ ∝ r⁻⁵.
5. **Setting up the ODE:** dE/dt = −P_GW. Using dE/dr ∝ r⁻² and P_GW ∝ r⁻⁵ gives dr/dt = −A r⁻³.
6. **Solving:** separates and integrates to r(t) ∝ (t_c − t)^(1/4). Using Kepler's third law (f ∝ r^(−3/2), i.e. r ∝ f^(−2/3)) converts this to the frequency evolution: **f(t) ∝ (t_c − t)^(−3/8)** — the characteristic "chirp."
7. **Strain estimate:** h ≈ (R_s/D)(v/c)². For GW150914 (M≈30 M☉ → R_s≈90 km, D≈1.3 Gly≈10²⁵ m, v/c≈0.5): h ≈ 10⁻²¹, giving a LIGO arm-length change ΔL = h×4000 m ≈ 4×10⁻¹⁸ m (about 1/1000th the width of a proton).
8. **Validation against data:** the derived f ∝ (t_c−t)^(−3/8) Newtonian-inspiral prediction matches real LIGO strain data closely, until the final few milliseconds (merger, where the Newtonian/adiabatic approximation breaks down).

## Astrophysics applications noted

- **BH vs NS discrimination:** black holes are point masses with no surface to tidally deform, so they follow the derived chirp curve exactly; neutron stars (physical objects, ~12 km radius) undergo tidal deformation, which costs orbital energy and produces a measurable deviation from the pure point-mass chirp curve late in the inspiral.
- **Exotic objects (boson stars):** hypothetical horizonless, "fluffier" compact objects made of ultralight dark-matter-like particles would have lower compactness and much larger tidal effects, draining orbital energy faster and producing a large deviation from the f^(−3/8) curve — a possible observational signature.

## Current research frontiers mentioned (directly relevant to this project)

- **Multi-messenger astronomy** — detecting GW and high-energy gamma-ray bursts from the same event; since gravity and light travel at the same speed, they should arrive near-simultaneously, enabling precise localization and fundamental-physics tests.
- **AI/LLMs in GW astronomy** — explicitly named application: "rapid analysis of circulars (GCNs) during observing runs," directly validating this thesis's general research direction as a recognized emerging use case, independent of this project.

## Use in this thesis

Candidate source for Chapter 2's "GW Fundamentals" background section (compact binary coalescence, chirp physics, why the inspiral signal has the shape it does) — the derivation above gives a from-first-principles grounding for why chirp mass is the parameter that governs the inspiral's frequency evolution, complementing the SNR-scaling relation this project's estimator is built on (`docs/references/chirp-mass-methodology-note.md`).
