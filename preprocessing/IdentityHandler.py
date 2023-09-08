import faker as faker
from deduce import Deduce
from docdeid import Annotation, AnnotationSet, Document

from preprocessing.PersonAnnotator import PersonAnnotationConverter


class Deidentifier:
    deidentifier = Deduce()

    def deidentify(self, text: str) -> Document:
        self.deidentifier.processors["names"].remove_processor(
            "person_annotation_converter"
        )
        self.deidentifier.processors["names"].add_processor(
            "person_annotation_converter", PersonAnnotationConverter()
        )
        deidentified_object = self.deidentifier.deidentify(text)
        return deidentified_object


class Surrogator:
    faker = faker.Faker()

    def surrogate(self, original_object, deidentified_object, identity_cache: dict):
        """
        Surrogate the identity of a text.
            :param identity_cache: A cache of the original text and the faked text.
            :param deidentified_object: The deidentified object to surrogate.
            :return: The surrogated object.
        """
        new_annotation_set = AnnotationSet()
        faker_dict = {
            "initial": self.faker.first_name,
            "name": self.faker.first_name,
            "patient": self.faker.first_name,
            "person": self.faker.first_name,
            "persoon": self.faker.first_name,
            "date": self.faker.date,
            "location": self.faker.address,
            "institution": self.faker.company,
            "phone": self.faker.phone_number,
            "url": self.faker.url,
            "email": lambda: f"{self.faker.name()}@{self.faker.domain_name()}",
            "mid": lambda: str(self.faker.random_number(digits=len(annotation.text))),
        }

        for i, annotation in enumerate(deidentified_object.annotations):
            original_text = annotation.text
            tag_lower = annotation.tag.lower()

            if original_text.lower() == "the" or original_text.lower() == "in":
                continue

            faked_text = faker_dict.get(
                tag_lower, lambda: f"REDACTED-{self.faker.random_number(digits=6)}"
            )()

            new_annotation_set.add(
                Annotation(
                    original_text,
                    annotation.start_char,
                    annotation.end_char,
                    faked_text,
                )
            )
            identity_cache[original_text] = faked_text

        for original_text, faked_text in identity_cache.items():
            deidentified_object.set_deidentified_text(
                original_object.replace(original_text, faked_text)
            )
        deidentified_object.annotations.update(new_annotation_set)
        return deidentified_object, identity_cache


class Reidentifier:
    @staticmethod
    def reidentify(text: str, identity_cache: dict) -> str:
        if not text:
            return text
        if not identity_cache.items():
            return text
        for original_text, faked_text in identity_cache.items():
            text = text.replace(faked_text, original_text)
        return text


class IdentityHandler:
    deidentifier = Deidentifier()
    surrogator = Surrogator()
    reidentifier = Reidentifier()
    identity_cache: dict = {}

    def deidentify(self, text: str) -> Document:
        """
        Deidentify the identity of a text.
            :param text: The text to deidentify.
            :return: A deidentified object that can be surrogated.
        """
        deidentified_object = self.deidentifier.deidentify(text)
        return deidentified_object

    def surrogate(self, original_object, deidentified_object):
        """
        Surrogate the identity of a text.
            :param identity_cache: A cache of the original text and the faked text.
            :param deidentified_object: The deidentified object to surrogate.
            :param original_object: The original object to surrogate.
            :return: The surrogated object.
        """
        surrogated_object, self.identity_cache = self.surrogator.surrogate(
            original_object, deidentified_object, self.identity_cache
        )
        return surrogated_object

    def reidentify(self, text: str) -> str:
        """
        Reidentify the identity of a text.
            :param identity_cache: A cache of the original text and the faked text.
            :param text: The text to reidentify the identity of.
            :return: The reidentified text.
        """
        text = self.reidentifier.reidentify(text, self.identity_cache)
        return text