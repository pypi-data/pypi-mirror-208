from collections import Counter
from count_unique_chars.exceptions import TypeNotStrException


class UniqueCharsCounter:
    def __init__(self) -> None:
        self.cache = {}

    def count_unique_chars(self, text: str) -> int:
        if not isinstance(text, str):
            raise TypeNotStrException
        if text in self.cache:
            return self.cache[text]
        unique_count = sum(1 for count in Counter(text).values() if count == 1)
        self.cache[text] = unique_count
        return unique_count
