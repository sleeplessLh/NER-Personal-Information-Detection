from src.predict import Predictor, extract_entities
from src.redact import redact_text


def test_entity_extraction_handles_malformed_initial_i_tag():
    entities = extract_entities(["John", "London"], ["I-PER", "B-LOC"])
    assert entities == [
        {"text": "John", "type": "PER", "start_token": 0, "end_token": 1},
        {"text": "London", "type": "LOC", "start_token": 1, "end_token": 2},
    ]


def test_saved_model_reloads_and_predicts_required_types():
    predictor = Predictor()
    result = predictor.predict("Sarah works at Microsoft in Kuala Lumpur.")
    assert {entity["type"] for entity in result["entities"]} == {"PER", "ORG", "LOC"}
    microsoft = next(entity for entity in result["entities"] if entity["text"] == "Microsoft")
    assert result["text"][microsoft["start"]:microsoft["end"]] == "Microsoft"


def test_no_entity_text():
    assert Predictor().predict("The weather is beautiful today.")["entities"] == []


def test_punctuation_is_not_absorbed_into_entity_span():
    text = "Sarah works at Microsoft in London!"
    result = Predictor().predict(text)
    assert all(text[entity["start"]:entity["end"]] == entity["text"] for entity in result["entities"])
    assert redact_text(text, result["entities"]).endswith("[LOC]!")


def test_empty_long_repeated_and_multisentence_inputs_do_not_crash():
    predictor = Predictor()
    assert predictor.predict("")["entities"] == []
    repeated = predictor.predict("Sarah met Sarah at Microsoft in London.")
    assert sum(entity["text"] == "Sarah" for entity in repeated["entities"]) == 2
    long_text = " ".join(["Sarah works at Microsoft in London."] * 200)
    result = predictor.predict(long_text)
    assert len(result["tokens"]) > 1_000
    assert all(long_text[e["start"]:e["end"]] == e["text"] for e in result["entities"])
