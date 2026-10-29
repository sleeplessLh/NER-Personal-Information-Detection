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
    result = predictor.predict("Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru.")
    assert {entity["type"] for entity in result["entities"]} == {"PER", "ORG", "LOC"}
    university = next(entity for entity in result["entities"] if entity["type"] == "ORG")
    assert result["text"][university["start"]:university["end"]] == "Universiti Teknologi Malaysia"


def test_no_entity_text():
    assert Predictor().predict("The weather is beautiful today.")["entities"] == []


def test_punctuation_is_not_absorbed_into_entity_span():
    text = "Sarah studies at Oxford University in London!"
    result = Predictor().predict(text)
    assert all(text[entity["start"]:entity["end"]] == entity["text"] for entity in result["entities"])
    assert redact_text(text, result["entities"]).endswith("[LOC]!")


def test_empty_long_repeated_and_multisentence_inputs_do_not_crash():
    predictor = Predictor()
    assert predictor.predict("")["entities"] == []
    repeated = predictor.predict("Sarah and Sarah joined a club at Oxford University in London.")
    assert sum(entity["text"] == "Sarah" for entity in repeated["entities"]) == 2
    long_text = " ".join(["Sarah studies at Oxford University in London."] * 200)
    result = predictor.predict(long_text)
    assert len(result["tokens"]) > 1_000
    assert all(long_text[e["start"]:e["end"]] == e["text"] for e in result["entities"])
