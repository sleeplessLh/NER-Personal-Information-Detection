from src.predict import Predictor, extract_entities


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
