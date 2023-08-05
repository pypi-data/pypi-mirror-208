"""Various indexer test cases"""
import unittest
import tempfile

from metaindex import index_files


SIMPLE = """%abc-2.1
X:1
T:Title
K:C
CDEF
"""

ADVANCED = """%abc-2.1
X:1
T:Commented % out
+title
 % K:C
K:D
CDEF
"""


class TestABCIndexing(unittest.TestCase):
    def test_simple(self):
        with tempfile.NamedTemporaryFile('w+t', suffix='.abc') as tmpfile:
            tmpfile.write(SIMPLE)
            tmpfile.seek(0)

            results = index_files([tmpfile.name])

            self.assertEqual(len(results), 1)
            self.assertIn('abc.title', results[0].info.keys())
            self.assertEqual('Title', results[0].info['abc.title'][0])

    def test_advanced(self):
        with tempfile.NamedTemporaryFile('w+t', suffix='.abc') as tmpfile:
            tmpfile.write(ADVANCED)
            tmpfile.seek(0)

            results = index_files([tmpfile.name])

            self.assertEqual(len(results), 1)
            self.assertIn('abc.title', results[0].info.keys())
            self.assertEqual('Commented title', results[0].info['abc.title'][0])
