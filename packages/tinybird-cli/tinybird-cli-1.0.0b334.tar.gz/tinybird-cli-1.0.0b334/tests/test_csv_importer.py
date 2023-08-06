
import unittest

from tinybird.csv_importer_find_endline_wrapper import find_new_line_index_to_split_the_buffer
from tinybird.csv_importer import BufferedCSVProcessor
from io import StringIO


class ChunkListCSVProcessor(BufferedCSVProcessor):
    def __init__(self, dialect):
        super().__init__(dialect)
        self.chunks = []

    def process_csv_chunk(self, csv_chunk):
        self.chunks.append(csv_chunk.decode())


class TestFindInCImplementation(unittest.TestCase):
    @staticmethod
    def _execute_find_new_line_index_to_split_the_buffer(buffer_text: str, quotechar='"', escapechar='\0'):

        buffer_text_encoded = buffer_text.encode("utf-8")
        idx = find_new_line_index_to_split_the_buffer(buffer_text_encoded, 'utf-8', quotechar, escapechar)
        print("IDX returned:", idx)
        process = buffer_text_encoded[:idx + 1]
        final_text = process.decode("utf-8")

        return final_text

    def test_buffering_logic_splits_the_csv_correctly_as_lines_come_in(self):

        csv = '''a,b,c
1,2,foo
4,5,bar
7,8,"foo

bar"
10,11,foo
13,14,bar
    '''
        csv_stream = StringIO(csv)

        p = ChunkListCSVProcessor(dialect={'new_line': "\n"})
        p.chunk_size = 16

        b = csv_stream.read(8)
        while b:
            p.write(b.encode())
            b = csv_stream.read(8)

        p.flush()

        for c in p.chunks:
            self.assertEqual(c.count('"') % 2, 0, f"{c} has invalid quoting")

    def test_buffering_logic_splits_the_csv_correctly_as_lines_come_in_with_fragment_bigger_than_chunk_size(self):

        csv = '''a,b,c
    1,2,foo
    4,5,bar
    7,8,"foo

    bar"
    10,11,foo
    13,14,bar
    '''
        csv_stream = StringIO(csv)

        p = ChunkListCSVProcessor(dialect={'escapechar': '"', 'new_line': "\n"})
        p.chunk_size = 16

        b = csv_stream.read(8)
        while b:
            p.write(b.encode())
            b = csv_stream.read(8)

        p.flush()

        for c in p.chunks:
            self.assertEqual(c.count('"') % 2, 0, f"{c} has invalid quoting")

    def buffering_fallbacks_to_old_new_line_finding_method_in_case_it_can_not_find_a_correct_new_line_char(self):

        csv = '''a,b,c
    1,2,"foo4,5,b
    ar7,8,foo10,11,foo11231231231233,14,bar
'''
        csv_stream = StringIO(csv)

        p = ChunkListCSVProcessor(dialect={'escapechar': '"', 'new_line': "\n"})
        p.chunk_size = 16

        b = csv_stream.read(8)

        while b:
            p.write(b.encode())
            b = csv_stream.read(8)
        p.flush()
        number_of_quotes_in_chunks = [c.count('"') for c in p.chunks]
        self.assertEqual([0, 1, 0], number_of_quotes_in_chunks)

    def test_split_on_complete_csv_returns_the_text(self):

        buffer_text = '''a,b,c
1,2,foo
4,5,bar
'''
        final_text = self._execute_find_new_line_index_to_split_the_buffer(buffer_text)

        self.assertEqual("""a,b,c
1,2,foo
4,5,bar
""", final_text)

    def test_split_csv_withlast_line_half_done_skips_that_line(self):

        buffer_text = '''a,b,c
1,2,foo
4,5,bar
7,8,"foo
'''
        final_text = self._execute_find_new_line_index_to_split_the_buffer(buffer_text)

        self.assertEqual("""a,b,c
1,2,foo
4,5,bar
""", final_text)

    def test_split_over_complete_csv_even_with_escaped_parts_returns_the_csv(self):

        buffer_text = '''a,b,c
1,2,foo
4,5,bar
7,8,"foo

bar"
10,11,foo
13,14,bar
'''
        final_text = self._execute_find_new_line_index_to_split_the_buffer(buffer_text)

        self.assertEqual('''a,b,c
1,2,foo
4,5,bar
7,8,"foo

bar"
10,11,foo
13,14,bar
''', final_text)

    def test_split_over_a_complete_csv_with_multiple_escaped_parts_returns_the_csv(self):

        buffer_text = '''a,b,c
1,2,"foo
"
4,"5",bar
7,"8","foo

bar"
10,11,foo
13,14,bar
'''
        final_text = self._execute_find_new_line_index_to_split_the_buffer(buffer_text)

        self.assertEqual('''a,b,c
1,2,"foo
"
4,"5",bar
7,"8","foo

bar"
10,11,foo
13,14,bar
''', final_text)

    def test_split_with_escaped_escapechar_and_and_incomplete_line_correctly_splits_the_text(self):

        buffer_text = '''a,b,c
1,2,""foo
4,""5"",bar
7,"""8","""foo


'''
        final_text = self._execute_find_new_line_index_to_split_the_buffer(buffer_text)

        self.assertEqual('''a,b,c
1,2,""foo
4,""5"",bar
''', final_text)

    def test_split_correctly_detects_and_endline_after_closing_a_quote(self):

        buffer_text = 'a,b,"c"\n4,"""5","bar"\n7,"8","foo\n'
        final_text = self._execute_find_new_line_index_to_split_the_buffer(buffer_text)
        self.assertEqual('a,b,"c"\n4,"""5","bar"\n', final_text)

    def test_buffer_using_multichar_new_line(self):

        buffer_text = 'a,b,c\r\n4,"5",bar\r\n7,"8","foo\r\n'
        final_text = self._execute_find_new_line_index_to_split_the_buffer(buffer_text)
        self.assertEqual('a,b,c\r\n4,"5",bar\r\n', final_text)

    def test_using_a_different_quotechar(self):
        buffer_text = "a,b,c\n4,'5',bar\n7,'8','foo\n"
        final_text = self._execute_find_new_line_index_to_split_the_buffer(buffer_text, quotechar="'")
        self.assertEqual("a,b,c\n4,'5',bar\n", final_text)

    def test_adding_a_different_kind_of_escapechar(self):
        buffer_text = 'a,b,c\n4,x"5x",bar\n7,"8x",x"foo\n'
        final_text = self._execute_find_new_line_index_to_split_the_buffer(buffer_text, escapechar='x')
        self.assertEqual('a,b,c\n4,x"5x",bar\n', final_text)

    def test_slow_iteration(self):
        csv = '''"Samsung U600""
    24""
    ","10000003409","1","10000003427"
"Samsung ""U600""
    24""","10000003409","",""
"Samsung U600 24""","10000003409","1","10000003427"
'''

        csv_stream = StringIO(csv)

        p = ChunkListCSVProcessor(dialect={'escapechar': '"', 'new_line': "\n"})
        p.chunk_size = 2

        b = csv_stream.read(1)
        while b:
            p.write(b.encode())
            b = csv_stream.read(1)

        p.flush()
        self.assertEqual(len(p.chunks), 3)
