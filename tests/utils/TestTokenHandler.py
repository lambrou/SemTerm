from textwrap import wrap
from typing import Union, List

import faker
import tiktoken


class TestTokenHandler:
    encoding: str = "cl100k_base"
    fake = faker.Faker()
    encoder = tiktoken.get_encoding(encoding)

    def generate_nonsensical_tokens(self, n: int = 8192) -> Union[List[str], None]:
        if n == 0:
            return None
        nonsense = self.fake.text(max(n * 2, 100))
        encoded_nonsense = self.encoder.encode(nonsense)
        clipped_nonsense = self.encoder.decode(encoded_nonsense[:n])
        return wrap(clipped_nonsense, 10)
