import random
import string
from typing import overload

class Msgs:
    n: int
    salt: int

    def __init__(self, n: int, salt: int) -> None:
        self.n = n
        self.salt = salt

    @overload
    def __getitem__(self, key: int) -> str:
        ...

    @overload
    def __getitem__(self, key: slice) -> list[str]:
        ...

    def __getitem__(self, key: int | slice) -> str | list[str]:
        if isinstance(key, slice):
            indices = range(*key.indices(len(self)))
            return [self[i] for i in indices]

        if isinstance(key, int):
            if key >= len(self):
                raise IndexError
            rng = random.Random()
            rng.seed(key + self.salt)
            num_words = int(rng.gauss(5, 3))
            if num_words < 1:
                num_words = 1

            generated_words = []
            for _ in range(num_words):
                word_length = rng.randint(3, 10)
                word = ''.join(rng.choice(string.ascii_lowercase) for _ in
                               range(word_length))
                generated_words.append(word)
            return ' '.join(generated_words)

        raise TypeError(f"Invalid key type: {type(key).__name__}")
        

    def __len__(self):
        return self.n

