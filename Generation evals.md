# Qwen answers on the golden set

`qwen3:8b` wrote 15 answers with thinking off. gold-026 asks who is named on the Carbon Reduction Plan sign-off, and the question does not say current. Scoring uses the deterministic checks in `src/eval_generation.py`. No judge is called. Means skip a score when it does not apply. Token F1, phrase coverage, and citation recall skip the 1 abstain question.

Source: `data/generation/answers.json` and `data/generation/evals.json`.

| Score | Value | Questions |
|---|---:|---:|
| Phrase coverage | 0.9821 | 14 |
| Required phrases | 0.9333 | 15 |
| Citation recall | 0.9286 | 14 |
| Cited section | 0.9333 | 15 |
| Distractor citation | 0.1000 | 15 |
| Token F1 | 0.5319 | 14 |
| Abstain contamination | 0.0000 | 1 |
| Hard checks passed | 11 / 15 | 15 |
| Confidence when the hard checks pass | 0.9909 | 11 |
| Confidence when a hard check fails | 0.7500 | 4 |
| Mean generation latency | 6.487 s | 15 |

A hard check fails when a required phrase is missing, a gold section is not cited, phrase coverage or citation recall is below 1, a cited section is a distractor, or the abstain answer adds a figure or a name. Token F1 is reported and is not a gate.

Token F1 is word overlap with `expected_answer`. On the 14 scored questions, word recall is 0.914 and word precision is 0.431. The required phrases are usually present. The extra words in the sentence pull F1 down to 0.5319.

## Questions that fail a hard check

| Question | What happened | Phrases | Section | Distractor citation |
|---|---|---|---|---:|
| gold-018 | The 10% by 2028 and about 50% by 2032 figures are right, and `Carbon_New_2040#6` is cited. `Envi_2040-1#5` is also cited, and that section is a gold distractor. | Pass | Pass | 0.5000 |
| gold-026 | The answer names John Speight, President and Head of Europe (EVP). It cites `Carbon_Old_2050#9`. The gold section is `Carbon_New_2040#8`, so citation recall is 0. The name appears in the answer, so the cited-section check passes. Confidence is 1. | Pass | Pass | 0.0000 |
| gold-029 | The scope is right: rented, leased, and owned. The answer does not contain the word "No". | Fail | Pass | 0.0000 |
| gold-049 | The abstain question. The answer text is empty and adds no figure or name. It still cites `Envi_2040-1#13`, a distractor, so the section check fails. Confidence is 0. | Pass | Fail | 1.0000 |

gold-022 passes the hard checks. It states 10% by 2025 and about 50% by 2030, and it cites `Carbon_New_2040#6` and `Envi_2040-1#5`.
