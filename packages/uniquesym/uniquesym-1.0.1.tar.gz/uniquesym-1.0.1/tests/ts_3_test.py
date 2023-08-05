import unittest
from unittest.mock import mock_open, patch
from scr import unique
class MyTestCase(unittest.TestCase):
    def test_answer3(self):
        m = mock_open(read_data='qwerty\ngghhue')
        with patch('builtins.open', m):
            with open('foo') as mock_file:
                file = mock_file.readlines()
                print(file)
                self.assertEqual([unique(string.strip()) for string in file], [6, 2])
if __name__ == '__main__':
    unittest.main()