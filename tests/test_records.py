"""Saved retrieval and generation scores must stay above the CI floors."""

import json
from pathlib import Path

RECORDS_PATH = Path(__file__).resolve().parents[1] / "data" / "generation" / "records.json"

RETRIEVAL_FLOORS = {
    "recall_at_k": 0.90,
    "mrr": 0.80,
    "ndcg": 0.80,
    "precision": 0.10,
    "precision_at_k": 0.10,
}
GENERATION_FLOORS = {
    "phrase_coverage": 0.90,
    "citation_recall": 0.90,
    "required_phrases": 0.90,
    "cited_section": 0.90,
}
DISTRACTOR_CEILING = 0.20
HARD_CHECKS_FLOOR = 11


def test_recorded_evals_meet_thresholds() -> None:
    record = json.loads(RECORDS_PATH.read_text(encoding="utf-8"))
    retrieval = record["retrieval"]
    generation = record["generation"]

    for name, floor in RETRIEVAL_FLOORS.items():
        assert retrieval[name] >= floor
    for name, floor in GENERATION_FLOORS.items():
        assert generation[name] >= floor
    assert generation["distractor_citation"] <= DISTRACTOR_CEILING
    assert generation["hard_checks_passed"] >= HARD_CHECKS_FLOOR
    assert generation["questions"] == 15
