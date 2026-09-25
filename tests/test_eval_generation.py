import json

import pytest

from src.eval_generation import (
    ATTEMPTS,
    K,
    CitedSection,
    Generation,
    QuestionScore,
    abstain_contamination,
    call_with_retry,
    citation_recall,
    cited_section,
    distractor_citation,
    evaluate,
    GENERATION_K,
    generate_answers,
    generation_prompt,
    prompt_order,
    hard_checks_passed,
    parse_generation,
    phrase_coverage,
    required_phrases,
    score_answers,
    score_item,
    token_f1,
)
from src.retrieve import INITIAL_K, HybridHit


def _hit(
    section_id: str = "Carbon_New_2040#1",
    name: str = "Commitment to Achieving Net Zero",
    body: str = "Net Zero emission by 2040.",
    document_date: str | None = None,
    date_source: str | None = None,
    version: str | None = None,
    superseded: bool = False,
) -> HybridHit:
    return HybridHit(
        chunk_id=f"{section_id}:0",
        filename="Carbon_New_2040.md",
        title="Carbon",
        page_no=None,
        section_name=name,
        parent_id=section_id,
        start_span=0,
        end_span=10,
        document_date=document_date,
        date_source=date_source,
        version=version,
        superseded=superseded,
        body=body,
        score=1.0,
        rrf_score=0.1,
    )


def _item(**overrides: object) -> dict[str, object]:
    item: dict[str, object] = {
        "id": "gold-001",
        "question": "By which year?",
        "abstain": False,
        "expected_answer": "2040",
        "answer_must_include": ["2040"],
        "supporting_sections": [
            {
                "section_id": "Carbon_New_2040#1",
                "section_name": "Commitment to Achieving Net Zero",
            }
        ],
        "distractor_sections": [
            {
                "section_id": "Carbon_Old_2050#2",
                "section_name": "Commitment to Achieving Net Zero",
            }
        ],
    }
    item.update(overrides)
    return item


def _cited(section_id: str, section_name: str = "") -> Generation:
    return Generation(
        answer="2040",
        sections=(CitedSection(section_id, section_name),),
        confidence=0.5,
    )


def test_prompt_asks_for_the_gold_section_fields() -> None:
    prompt = generation_prompt("By which year?", [_hit()])

    assert "section_id: Carbon_New_2040#1" in prompt
    assert "section_name: Commitment to Achieving Net Zero" in prompt
    assert "chunk_id: Carbon_New_2040#1:0" in prompt
    assert '"section_id"' in prompt
    assert '"section_name"' in prompt
    assert "confidence" in prompt
    assert "Question: By which year?" in prompt
    assert "superseded: false" in prompt
    assert "set sections to []" in prompt
    assert "gold supporting" not in prompt
    assert "version:" not in prompt
    assert "document_date:" not in prompt

    labeled = generation_prompt(
        "What does the archived plan say?",
        [
            _hit(
                section_id="Carbon_Old_2050#2",
                document_date="2023-03-12",
                date_source="publication",
                version="1.0",
                superseded=True,
            )
        ],
    )
    assert "superseded: true" in labeled
    assert "version: 1.0" in labeled
    assert "document_date: 2023-03-12" in labeled
    assert "date_source: publication" in labeled


def test_prompt_puts_the_best_chunks_at_the_ends() -> None:
    hits = [_hit(section_id=f"Doc#{rank}", name=f"Rank {rank}", body=f"body {rank}") for rank in range(1, 6)]

    assert [hit.parent_id for hit in prompt_order(hits)] == ["Doc#2", "Doc#4", "Doc#5", "Doc#3", "Doc#1"]
    prompt = generation_prompt("By which year?", hits)
    assert prompt.index("body 2") < prompt.index("body 5") < prompt.index("body 1")
    assert GENERATION_K == 5


def test_parse_generation_reads_sections_and_confidence() -> None:
    text = (
        '```json\n{"answer": "2040", "sections": '
        '[{"section_id": "Carbon_New_2040#1", "section_name": "Commitment"}], '
        '"confidence": "0.8"}\n```'
    )
    parsed = parse_generation(text)

    assert parsed.answer == "2040"
    assert parsed.sections == (
        CitedSection("Carbon_New_2040#1", "Commitment"),
    )
    assert parsed.confidence == pytest.approx(0.8)


def test_parse_generation_accepts_a_chunk_id_and_a_percent() -> None:
    parsed = parse_generation(
        '{"answer": "2050", "sections": [{"chunk_id": "Carbon_Old_2050#2:0"}], "confidence": 80}'
    )

    assert parsed.sections[0].section_id == "Carbon_Old_2050#2:0"
    assert parsed.confidence == pytest.approx(0.8)


def test_non_json_reply_has_no_citation() -> None:
    assert parse_generation("The year is 2040.") == Generation(
        answer="The year is 2040.",
        sections=(),
        confidence=None,
    )


def test_required_phrases_are_case_insensitive() -> None:
    assert required_phrases("Net zero by 2040.", _item())
    assert not required_phrases("Net zero soon.", _item())


def test_abstain_rejects_distractor_evidence() -> None:
    item = _item(
        abstain=True,
        expected_answer=None,
        answer_must_include=[],
        supporting_sections=[],
        distractor_sections=[
            {
                "section_id": "Envi_2040-1#13",
                "section_name": "John Speight",
                "evidence": [{"text": "information@coforge.com"}],
            }
        ],
    )

    assert required_phrases("The documents do not say.", item)
    assert not required_phrases("Write to information@coforge.com.", item)


def test_cited_section_matches_the_gold_id() -> None:
    assert cited_section(_cited("Carbon_New_2040#1"), _item())
    assert cited_section(_cited("Carbon_New_2040#1:0"), _item())
    assert not cited_section(_cited("Carbon_New_2040#10"), _item())
    assert not cited_section(_cited("Carbon_Old_2050#2"), _item())


def test_shared_section_name_needs_the_section_id() -> None:
    named = Generation(
        answer="2040",
        sections=(CitedSection("", "Commitment to Achieving Net Zero"),),
        confidence=None,
    )

    assert not cited_section(named, _item())


def test_a_unique_section_name_matches() -> None:
    item = _item(distractor_sections=[])
    named = Generation(
        answer="See the preamble.",
        sections=(CitedSection("", "Commitment to Achieving Net Zero"),),
        confidence=None,
    )

    assert cited_section(named, item)


def test_abstain_matches_only_when_nothing_is_cited() -> None:
    item = _item(abstain=True, supporting_sections=[], answer_must_include=[])

    assert cited_section(Generation("The documents do not say.", (), None), item)
    assert not cited_section(_cited("Envi_2040-1#13", "John Speight"), item)


def test_token_f1_is_word_overlap() -> None:
    assert token_f1("Version 1.0", "1.0") == pytest.approx(0.8)
    assert token_f1("about 50% by 2030", "about 25% by 2030") == pytest.approx(0.75)
    assert token_f1("2040", "2040") == pytest.approx(1.0)
    assert token_f1("2040", "") == pytest.approx(0.0)
    assert token_f1("", "") == pytest.approx(1.0)


def test_phrase_coverage_is_the_share_of_gold_phrases() -> None:
    item = _item(answer_must_include=["half", "quarterly"])

    assert phrase_coverage("A quarterly report.", item) == pytest.approx(0.5)
    assert phrase_coverage("A half-year quarterly report.", item) == pytest.approx(1.0)
    assert phrase_coverage("The documents do not say.", _item(abstain=True)) is None


def test_citation_recall_counts_each_supporting_section() -> None:
    item = _item(
        supporting_sections=[
            {"section_id": "Carbon_New_2040#6", "section_name": "Carbon Reduction Initiatives"},
            {"section_id": "Envi_2040-1#5", "section_name": "Energy Optimization"},
        ]
    )
    parsed = Generation(
        answer="10% by 2025.",
        sections=(CitedSection("Carbon_New_2040#6:0", "Carbon Reduction Initiatives"),),
        confidence=0.9,
    )

    assert citation_recall(parsed, item) == pytest.approx(0.5)
    assert citation_recall(parsed, _item(abstain=True, supporting_sections=[])) is None


def test_distractor_citation_is_the_share_of_cited_sections() -> None:
    parsed = Generation(
        answer="10% and 25%.",
        sections=(
            CitedSection("Carbon_New_2040#6", "Carbon Reduction Initiatives"),
            CitedSection("Carbon_Old_2050#8:0", "Carbon Reduction Initiatives"),
        ),
        confidence=0.9,
    )
    item = _item(
        distractor_sections=[
            {"section_id": "Carbon_Old_2050#8", "section_name": "Carbon Reduction Initiatives"}
        ]
    )

    assert distractor_citation(parsed, item) == pytest.approx(0.5)
    assert distractor_citation(Generation("2040", (), None), item) == pytest.approx(0.0)


def test_abstain_contamination_flags_an_added_figure_or_name() -> None:
    item = _item(
        question="What were Coforge's FY25 Scope 2 emissions in the United States?",
        abstain=True,
        expected_answer=None,
        answer_must_include=[],
        supporting_sections=[],
    )

    assert abstain_contamination("The documents do not say.", item) is False
    assert abstain_contamination("The documents do not say. The UK figure is 2.90.", item) is True
    assert abstain_contamination("The ESG Committee may amend the policy.", item) is True
    assert abstain_contamination("2040", _item()) is None


def test_evaluate_averages_scores_and_reported_confidence() -> None:
    assert K == INITIAL_K == 10
    first = QuestionScore("gold-001", 0.25, 1.0, True, True)
    second = QuestionScore("gold-002", None, 3.0, False, False)
    result = evaluate([first, second])

    assert result.confidence == pytest.approx(0.25)
    assert result.confidence_questions == 1
    assert result.latency_seconds == pytest.approx(2.0)
    assert result.required_phrases == pytest.approx(0.5)
    assert result.cited_section == pytest.approx(0.5)
    assert result.questions == 2


def test_evaluate_splits_confidence_by_the_hard_checks() -> None:
    passed = QuestionScore(
        "gold-001",
        0.4,
        1.0,
        True,
        True,
        token_f1=1.0,
        phrase_coverage=1.0,
        citation_recall=1.0,
        distractor_citation=0.0,
        abstain_contamination=None,
    )
    failed = QuestionScore(
        "gold-022",
        0.9,
        2.0,
        True,
        True,
        token_f1=0.5,
        phrase_coverage=1.0,
        citation_recall=1.0,
        distractor_citation=0.5,
        abstain_contamination=None,
    )

    assert hard_checks_passed(passed)
    assert not hard_checks_passed(failed)
    result = evaluate([passed, failed])

    assert result.token_f1 == pytest.approx(0.75)
    assert result.phrase_coverage == pytest.approx(1.0)
    assert result.citation_recall == pytest.approx(1.0)
    assert result.distractor_citation == pytest.approx(0.25)
    assert result.abstain_contamination == pytest.approx(0.0)
    assert result.abstain_questions == 0
    assert result.confidence_when_passed == pytest.approx(0.4)
    assert result.confidence_when_failed == pytest.approx(0.9)


def test_empty_eval_raises() -> None:
    with pytest.raises(ValueError):
        evaluate([])


def test_score_item_records_the_checks() -> None:
    text = (
        '{"answer": "2040", "sections": '
        '[{"section_id": "Carbon_New_2040#1", "section_name": "Commitment to Achieving Net Zero"}], '
        '"confidence": 0.7}'
    )
    row = score_item(_item(), text, 1.5)

    assert row.confidence == pytest.approx(0.7)
    assert row.latency_seconds == pytest.approx(1.5)
    assert row.required_phrases
    assert row.cited_section
    assert row.token_f1 == pytest.approx(1.0)
    assert row.phrase_coverage == pytest.approx(1.0)
    assert row.citation_recall == pytest.approx(1.0)
    assert row.distractor_citation == pytest.approx(0.0)
    assert row.abstain_contamination is None


def test_retry_runs_three_times_then_raises() -> None:
    calls = {"n": 0}

    def fail() -> None:
        calls["n"] += 1
        raise RuntimeError("down")

    with pytest.raises(RuntimeError, match="down"):
        call_with_retry(fail)

    assert ATTEMPTS == 3
    assert calls["n"] == 3


def test_retry_returns_the_first_success() -> None:
    calls = {"n": 0}

    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("empty")
        return "ok"

    assert call_with_retry(flaky) == "ok"
    assert calls["n"] == 2


def test_answers_are_written_before_evals(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    gold = tmp_path / "gold.json"
    gold.write_text(json.dumps({"items": [_item()]}), encoding="utf-8")
    monkeypatch.setattr("src.eval_generation.GOLD_PATH", gold)
    calls = {"n": 0}

    def flaky(prompt: str) -> str:
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("empty")
        return (
            '{"answer": "2040", "sections": [{"section_id": "Carbon_New_2040#1", '
            '"section_name": "Commitment to Achieving Net Zero"}], "confidence": 0.4}'
        )

    class _Client:
        def close(self) -> None:
            return None

    monkeypatch.setattr("src.eval_generation.generate", flaky)
    monkeypatch.setattr("src.eval_generation.connect", lambda: _Client())
    monkeypatch.setattr("src.eval_generation.hybrid_search", lambda client, question, k: [_hit()])
    answers = tmp_path / "answers.json"
    generate_answers(answers)

    stored = json.loads(answers.read_text(encoding="utf-8"))
    assert calls["n"] == 2
    assert stored["items"][0]["answer"] == "2040"
    assert stored["items"][0]["error"] is None
    assert stored["items"][0]["retrieved"][0]["section_id"] == "Carbon_New_2040#1"

    def fail_generate(prompt: str) -> str:
        raise AssertionError("evals must not generate")

    monkeypatch.setattr("src.eval_generation.generate", fail_generate)
    evals = tmp_path / "evals.json"
    result = score_answers(answers, evals)
    saved = json.loads(evals.read_text(encoding="utf-8"))

    assert result is not None
    assert "judge" not in saved
    assert saved["items"][0]["required_phrases"] is True
    assert saved["items"][0]["cited_section"] is True
    assert saved["items"][0]["token_f1"] == pytest.approx(1.0)
