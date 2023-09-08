import docdeid as dd


class PersonAnnotationConverter(dd.process.AnnotationProcessor):
    """
    Responsible for processing the annotations produced by all name annotators (regular and context-based).
    """

    def __init__(self) -> None:
        self._overlap_resolver = dd.process.OverlapResolver(
            sort_by=["tag", "length"],
            sort_by_callbacks={
                "tag": lambda x: "person" not in x,
                "length": lambda x: -x,
            },
        )

    def process_annotations(
        self, annotations: dd.AnnotationSet, text: str
    ) -> dd.AnnotationSet:
        new_annotations = self._overlap_resolver.process_annotations(
            annotations, text=text
        )

        return dd.AnnotationSet(
            dd.Annotation(
                text=annotation.text,
                start_char=annotation.start_char,
                end_char=annotation.end_char,
                tag="person",
            )
            for annotation in new_annotations
        )
