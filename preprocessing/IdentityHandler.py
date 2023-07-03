import faker as faker
from deduce import Deduce
from docdeid import Annotation, AnnotationSet, Document

from preprocessing.PersonAnnotator import PersonAnnotationConverter


class Deidentifier:
    deidentifier = Deduce()

    def deidentify(self, text: str) -> Document:
        """
            Deidentify the identity of a text.
                :param text: The text to deidentify.
                :return: A deidentified object that can be surrogated.
        """
        self.deidentifier.processors["names"].remove_processor("person_annotation_converter")
        self.deidentifier.processors["names"].add_processor("person_annotation_converter", PersonAnnotationConverter())
        deidentified_object = self.deidentifier.deidentify(text)
        return deidentified_object


class Surrogator:
    faker = faker.Faker()

    def surrogate(self, deidentified_object, identity_cache: dict):
        """
            Surrogate the identity of a text.
                :param identity_cache: A cache of the original text and the faked text.
                :param deidentified_object: The deidentified object to surrogate.
                :return: The surrogated object.
        """
        new_annotation_set = AnnotationSet()
        faker_dict = {
            "initial": self.faker.name,
            "name": self.faker.name,
            "patient": self.faker.name,
            "person": self.faker.name,
            "persoon": self.faker.name,
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
            faked_text = faker_dict.get(tag_lower, lambda: f'REDACTED-{self.faker.random_number(digits=6)}')()

            new_annotation_set.add(Annotation(
                original_text, annotation.start_char, annotation.end_char, faked_text
            ))
            identity_cache[original_text] = faked_text

        for original_text, faked_text in identity_cache:
            deidentified_object.set_deidentified_text(
                deidentified_object.deidentified_text.replace(
                    original_text, faked_text
                )
            )
        deidentified_object.annotations = new_annotation_set
        return deidentified_object, identity_cache


class Reidentifier:

    @staticmethod
    def reidentify(text: str, identity_cache: dict) -> str:
        """
            Reidentify the identity of a text.
                :param identity_cache: A cache of the original text and the faked text.
                :param text: The text to reidentify the identity of.
                :return: The reidentified text.
        """
        for faked_text, original_text in identity_cache.items():
            text = text.replace(faked_text, original_text)
        return text


class IdentityHandler:
    deidentifier: Deidentifier
    surrogator: Surrogator
    reidentifier: Reidentifier
    identity_cache: dict

    def deidentify(self, text: str) -> Document:
        """
            Deidentify the identity of a text.
                :param text: The text to deidentify.
                :return: A deidentified object that can be surrogated.
        """
        deidentified_object = self.deidentifier.deidentify(text)
        return deidentified_object

    def surrogate(self, deidentified_object, identity_cache: dict):
        """
            Surrogate the identity of a text.
                :param identity_cache: A cache of the original text and the faked text.
                :param deidentified_object: The deidentified object to surrogate.
                :return: The surrogated object.
        """
        surrogated_object, identity_cache = self.surrogator.surrogate(deidentified_object, identity_cache)
        self.identity_cache = identity_cache
        return surrogated_object

    def reidentify(self, text: str, identity_cache: dict) -> str:
        """
            Reidentify the identity of a text.
                :param identity_cache: A cache of the original text and the faked text.
                :param text: The text to reidentify the identity of.
                :return: The reidentified text.
        """
        text = self.reidentifier.reidentify(text, identity_cache)
        return text
