from hypothesis import settings, given
import hypothesis.strategies as strategy

from preprocessing.TokenHandler import TokenHandler


class TestTokenHandler:
    llm_name = "gpt-3.5-turbo"  # Replace with the model name you're using
    token_handler = TokenHandler(llm_name=llm_name)

    @settings(max_examples=100, deadline=None)
    @given(
        strategy.text(min_size=10, max_size=5000),
        strategy.integers(min_value=500, max_value=2000),
    )
    def test_split_by_token(self, text, chunk_size):
        split_documents = self.token_handler.split_by_token(text, chunk_size)
        for document in split_documents:
            assert (
                len(document.page_content.split()) <= chunk_size
            ), "Each split should respect the token size"
        combined_text = " ".join(
            [document.page_content for document in split_documents]
        )
        assert (
            combined_text == text
        ), "Combined splits should reconstruct the original text"
