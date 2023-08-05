from tinybird.csv_importer_find_endline_wrapper import find_new_line_index_to_split_the_buffer
import unittest
import random


class TestCSVFindEndline(unittest.TestCase):
    def test_fuzzy(self):
        self.fuzzy(1)
        self.fuzzy(2)
        self.fuzzy(3)
        self.fuzzy(629574684)
        self.fuzzy(1054762918)
        self.fuzzy(629574684)
        i = 0
        while i < 2000:
            seed = random.randint(0, 2**31)
            self.fuzzy(seed)
            i += 1

    def fuzzy(self, seed):
        prng = random.Random(seed)
        text = ""

        FIELD, NEWLINE, QUOTED_FIELD, ESCAPED_NEWLINE, ESCAPED_QUOTE = 1, 2, 3, 4, 5
        iters = prng.randrange(0, 33)
        i = 0
        last_newline = -1
        last = None
        while i < iters:
            action = prng.sample([FIELD, NEWLINE, QUOTED_FIELD, ESCAPED_NEWLINE, ESCAPED_QUOTE], 1)[0]
            if last in {FIELD, ESCAPED_NEWLINE, ESCAPED_QUOTE, QUOTED_FIELD} and action != NEWLINE:
                text += ","
            if action == FIELD:
                size = prng.randrange(0, 33)
                text += "a" * size
            elif action == ESCAPED_NEWLINE:
                size = prng.randrange(0, 33)
                text += "\\\n" * size
            elif action == ESCAPED_QUOTE:
                size = prng.randrange(0, 33)
                text += '\\"' * size
            elif action == NEWLINE:
                last_newline = len(text)
                text += "\n"
            elif action == QUOTED_FIELD:
                size = prng.randrange(0, 33)
                t = "\n" * size
                text += f'"{t}"'
            last = action
            i += 1
        got = find_new_line_index_to_split_the_buffer(text.encode('utf-8'), 'utf-8', escapechar="\\")
        assert got == last_newline, f"Fuzzy test failed with seed {seed}: {repr(text)}"
