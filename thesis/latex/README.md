# Thesis LaTeX

Structure follows the [Tribhuwan University Project Work Template](https://www.overleaf.com/latex/templates/tribhuwan-university-project-work-template/kgqnczfcbjrr): formal front matter, then a 5-chapter body (Introduction, Literature Review, Materials and Methods, Results and Discussion, Conclusion and Recommendation).

**Not test-compiled.** No LaTeX toolchain was available in the environment this was written in. Before relying on it, open `main.tex` on Overleaf (where the reference template lives) or compile locally with **XeLaTeX** (required for `polyglossia`/the Devanagari abstract) and fix whatever the first compile turns up.

## Structure

```
main.tex                          - assembles everything below
frontmatter/
  titlepage.tex                   - TODO: institutional details
  recommendation.tex              - TODO: supervisor signs off
  declaration.tex                 - TODO: your details
  letter_of_forward.tex           - TODO: department-specific
  board_certificate.tex           - TODO: filled in post-defense
  acknowledgement.tex             - TODO: personal, write yourself
  abstract.tex                    - drafted (English)
  abstract_devanagari.tex         - TODO: Nepali translation (not machine-translated - see file comment)
  acronyms.tex                    - drafted, add more as needed
chapters/
  01_introduction.tex             - drafted
  02_literature_review.tex        - placeholder skeleton, fill during M2 (sprint Days 4-5)
  03_materials_and_methods.tex    - drafted from docs/feasibility_draft.md + legs/leg3_pathfinder/docs/pathfinder_design_draft.md
  04_results_and_discussion.tex   - drafted; two TODO sections pending the AI-comparison and Pathfinder work
  05_conclusion.tex               - drafted
figures/                          - M7.4 validation plots referenced by Chapter 4, copied in from
                                     legs/leg1_estimation/figures/ (regenerate both via
                                     legs/leg1_estimation/generate_plots.py, then re-copy here -
                                     kept local so this folder stays self-contained if zipped for Overleaf)
references.bib                    - empty (see file comment - no fabricated citations)
```

## What's real vs placeholder

Chapters 3 and 4 (methods, results) contain real content pulled from the actual pipeline and validation results — update them as the underlying work in `legs/leg1_estimation/docs/feasibility_draft.md` changes, since that markdown draft is the source of truth and this LaTeX version can drift out of sync if edited independently.

Everything marked `% TODO` needs either your personal/institutional details or work not yet done (literature review, AI-comparison results, Pathfinder evaluation).
