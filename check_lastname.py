import re
from typing import List


class RussianSurnameDetector:
    def __init__(self):
        self.surname_endings = [
            'ov', 'ova', 'ev', 'eva', 'in', 'ina', 'iy', 'oy', 'yy',
            'sky', 'skiy', 'skaya', 'skoy', 'tskiy', 'tsky', 'tskaya',
            'ko', 'enko', 'chuk', 'shin', 'kin', 'ovitch', 'evich',
            'vich', 'uk', 'yuk', 'ak', 'ik', 'yk', 'ovski', 'evski',
            'aya', 'aya', 'na', 'ova', 'eva', 'ina', 'skaya', 'tskaya'
        ]

        self.min_length = 3
        self.max_length = 20

    def is_russian_surname(self, text: str) -> bool:

        text = text.strip().lower()

        has_surname_ending = any(text.endswith(ending) for ending in self.surname_endings)


        has_consonants = len(re.findall(r'[bcdfghjklmnpqrstvwxz]', text)) >= 2
        not_too_many_vowels = len(re.findall(r'[aeiouy]', text)) < len(text) * 0.6
        return (has_surname_ending and has_consonants and not_too_many_vowels)


# surname_detector = RussianSurnameDetector()
# print(surname_detector.is_russian_surname("AMINA"))



