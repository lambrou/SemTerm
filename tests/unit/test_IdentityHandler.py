from unittest.mock import MagicMock

from hypothesis import given
from hypothesis.strategies import sampled_from

from preprocessing.IdentityHandler import (
    IdentityHandler,
    Deidentifier,
    Surrogator,
    Reidentifier,
)


class TestIdentityHandler:
    names = ["Alice", "Bob", "Charlie", "Diana"]

    @given(sampled_from(names))
    def test_identity_handler(self, name):
        identity_handler = IdentityHandler()
        original_text = f"My name is {name}."
        deidentified_object = identity_handler.deidentify(original_text)
        surrogated_object = identity_handler.surrogate(
            original_text, deidentified_object
        )
        reidentified_text = identity_handler.reidentifier.reidentify(
            surrogated_object.deidentified_text, identity_handler.identity_cache
        )

        assert (
            reidentified_text == original_text
        ), f"Reidentified text should match the original text. Got {reidentified_text}, expected {original_text}"


class TestDeidentifier:
    names = ["Alex Jones", "Bob Barker", "Charlie", "Diana"]

    @given(sampled_from(names))
    def test_name_deidentification(self, name):
        deidentifier = Deidentifier()

        original_text = f"My name is {name}."
        deidentified_object = deidentifier.deidentify(original_text)
        deidentified_text = deidentified_object.deidentified_text

        assert name not in deidentified_text, f"The name {name} was not deidentified."


class TestSurrogator:
    names = ["Alice", "Bob", "Charlie", "Diana"]

    @given(sampled_from(names))
    def test_surrogation(self, name):
        surrogator = Surrogator()
        identity_cache = {}

        original_object = f"My name is {name}."

        deidentified_object = MagicMock()
        annotation_set = MagicMock()

        mock_annotation = MagicMock()
        mock_annotation.text = name
        mock_annotation.tag = "name"
        mock_annotation.start_char = 11
        mock_annotation.end_char = 11 + len(name)
        annotation_set.__iter__.return_value = iter([mock_annotation])

        deidentified_object.annotations = annotation_set
        deidentified_object.set_deidentified_text = MagicMock()

        surrogated_object, updated_identity_cache = surrogator.surrogate(
            original_object, deidentified_object, identity_cache
        )

        assert name not in surrogated_object.set_deidentified_text.call_args[0][0]
        assert name in updated_identity_cache
        assert updated_identity_cache[name] != name


class TestReidentifier:
    names = ["Alice", "Bob", "Charlie", "Diana"]

    @given(sampled_from(names))
    def test_reidentification(self, name):
        reidentifier = Reidentifier()
        surrogated_name = "FakeName"
        identity_cache = {name: surrogated_name}
        original_text = f"My name is {name}."
        surrogated_text = f"My name is {surrogated_name}."

        reidentified_text = reidentifier.reidentify(surrogated_text, identity_cache)

        assert (
            reidentified_text == original_text
        ), f"Reidentified text should match the original text. Got {reidentified_text}, expected {original_text}"
