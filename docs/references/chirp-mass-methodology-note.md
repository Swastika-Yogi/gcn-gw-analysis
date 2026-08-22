# Chirp Mass Estimation from GCN Circular Data (methodology note)

> Extracted text, not the original PDF/DOCX. Source: "Chirp mass estimation-example.pdf" / "Chirp mass estimation-example.txt", shared in conversation 2026-08-22. This is the internal methodology note whose SNR-scaling formula is implemented in `legs/leg1_estimation/modeling/chirp_mass_estimator.py` — see the literature-review gap noted in `thesis/latex/chapters/02_literature_review.tex` (this note is not a peer-reviewed citable source).

Example circular: https://gcn.nasa.gov/circulars/42708

## 1. The goal

The goal is to explore whether chirp mass (ℳ) can be approximately estimated using only GCN circular-level information, combined with basic gravitational-wave scaling relations. Instead of using full waveform data, we start from the standard inspiral signal-to-noise ratio (SNR) expression and rewrite it into a form that depends only on quantities that are either available in circulars or can be reasonably approximated.

## 2. Starting Point: Equation (1)

ρ² = (A²/D_L²) [F₊²(θ,φ,ψ)(1+cos²ι)² + 4F×²(θ,φ,ψ)cos²ι] I₇

where:
- ρ = signal-to-noise ratio (SNR)
- D = luminosity distance
- ι = inclination angle
- F₊, F× = detector antenna pattern functions
- I₇ = detector noise integral
- A contains the chirp mass

## 3. Chirp Mass Dependence (from A)

A = √(5/96) π^(-2/3) (Gℳ_z/c³)^(5/6) c

So the dependence is: A ∝ ℳ_z^(5/6)

Substituting into Equation (1): ρ² ∝ (ℳ_z^(5/3)/D_L²) × [F₊²(1+cos²ι)² + 4F×²cos²ι] × I₇

## 4. Simplifying the Orientation Term

Combined orientation factor: F(ι) = [F₊²(1+cos²ι)² + 4F×²cos²ι]^(1/2)

So: ρ ∝ (ℳ_z^(5/6)/D_L) F(ι) I₇^(1/2)

## 5. Rearranging for Chirp Mass

ℳ_z^(5/6) ∝ ρD_L / (F(ι) I₇^(1/2))

Raising both sides to power 6/5: ℳ_z ∝ (ρD_L / (F(ι) I₇^(1/2)))^(6/5)

## 6. Why the Noise Term I7 Removed

I₇ = ∫ f^(-7/3)/S_n(f) df

Depends on detector sensitivity, noise curve S_n(f), frequency band. However: it depends on the detector, not the source; it varies only within a limited range for a given observing run; it is not available in GCN circulars. Therefore, absorbed into a constant: I₇^(1/2) → included in constant C.

## 7. Final Working Equation

**ℳ = C (ρD_L / F(ι))^(6/5)**

## 8. Key Quantities Used

### (i) Signal-to-Noise Ratio ρ
Not directly given in circulars. Detection threshold: ρ ≳ 8. From the circular (example, S251116en): very low false alarm rate (~10⁻¹²), BBH classification (>99%). This indicates a high-confidence detection, typically ρ ~ 10–25. We choose ρ = 15. This is not arbitrary — consistent with detection significance.

### (ii) Luminosity Distance D_L
From the circular: D_L = 1741 ± 490 Mpc. Directly used in the equation.

### (iii) Orientation Factor F(ι)
The inclination satisfies cos ι ∈ [−1, 1]. For astrophysical sources, orientations are randomly distributed. We choose cos ι = 0.5 — a typical (non-extreme) orientation. Using F(ι) = (1 + cos²ι)/2: F(ι) = 0.625.

## 9. Numerical Example

Step 1: ρD_L/F(ι) = (15 × 1741)/0.625 = 26115/0.625 = 41784
Step 2 (repeat of above): 41784
Step 3: (41784)^(6/5) ≈ 3.5 × 10⁵
Step 4: ℳ = C × 3.5 × 10⁵

## 10. Meaning of Constant C

C includes: physical constants G, c, π; detector noise properties; frequency integration; unit conversion. It converts the scaling relation into a physical mass (in M_☉).

### Calibration

From known GW events: D_L ~ 1000 Mpc, ρ ~ 10–20, ℳ ~ 20–40 M_☉. This gives C ≈ 10⁻⁴.

## 11. Final Result

ℳ ≈ 35 M_☉

## 12. Comparison with Circular

ℳ_circular ∈ (22, 44) M_☉
ℳ_estimate ≈ 35 M_☉

## 13. Interpretation

This shows that (SNR + distance + orientation) ⇒ reasonable chirp mass estimate, for this one worked example.

## 14. Conclusion

Starting from Equation (1), we rewrite the SNR relation into a usable form and estimate chirp mass using circular-level information and physically motivated assumptions. This method does not replace full parameter estimation, but provides a fast, physically grounded approximation that can be extended to multiple events.

---

**Project note (2026-08-20):** the worked example above (S251116en, November 2025) is not from O4a — the O4a run (2023-05-24 to 2024-01-16) predates the "chirp mass falls in bin (X,Y)" reporting sentence entirely (see `legs/leg1_estimation/docs/feasibility_draft.md` Section 3). Applying this method's fixed ρ=15, cos ι=0.5, C≈1e-4 assumptions across the full O4a distance range (3–6,653 Mpc, three orders of magnitude) produces estimates spanning 0.02–175 M_☉, because holding SNR constant while distance varies this much makes the formula track distance rather than mass. See the calibration and validation work in that same file for the full quantitative analysis.
