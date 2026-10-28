from src.redact import redact_text, redact_tokens


def test_redaction_replaces_multitoken_entities_and_repairs_spacing():
    tokens = ["Ali", "studies", "at", "Universiti", "Malaya", "."]
    entities = [
        {"text": "Ali", "type": "PER", "start_token": 0, "end_token": 1},
        {"text": "Universiti Malaya", "type": "ORG", "start_token": 3, "end_token": 5},
    ]
    assert redact_tokens(tokens, entities) == "[PER] studies at [ORG]."


def test_repeated_entities_are_each_redacted():
    tokens = ["Ali", "met", "Ali", "."]
    entities = [
        {"text": "Ali", "type": "PER", "start_token": 0, "end_token": 1},
        {"text": "Ali", "type": "PER", "start_token": 2, "end_token": 3},
    ]
    assert redact_tokens(tokens, entities) == "[PER] met [PER]."


def test_character_redaction_preserves_original_whitespace():
    text = "Alice  works at Microsoft.\n"
    entities = [
        {"type": "PER", "start": 0, "end": 5},
        {"type": "ORG", "start": 16, "end": 25},
    ]
    assert redact_text(text, entities) == "[PER]  works at [ORG].\n"
