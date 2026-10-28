import pytest

from src.preprocessing import build_vocabulary, casing_features, tokenize, tokens_to_ids, validate_bio


def test_tokenization_preserves_punctuation_and_names():
    assert tokenize("Ali works at UTM, Johor.") == ["Ali", "works", "at", "UTM", ",", "Johor", "."]


def test_vocabulary_and_unknown_word():
    vocabulary = build_vocabulary([["Ali", "works"]])
    assert tokens_to_ids(["ALI", "unseen"], vocabulary) == [vocabulary["ali"], vocabulary["<UNK>"]]


def test_casing_feature_shape():
    features = casing_features(["Ali", "UTM", "works", "2026"])
    assert len(features) == 4
    assert all(len(row) == 4 for row in features)


def test_invalid_bio_is_rejected():
    with pytest.raises(ValueError, match="Illegal I-tag"):
        validate_bio(["Ali"], ["I-PER"])
