"""
If running from shell and package is installed, run from 'working directory' so that test/dir_1 works
"""


import unittest
try:
    from src.chksum_cli import chksum # if in repository
except:
    from chksum_cli import chksum # if installed

dir_1_hash_with_dots = "9b50fd1de4a200b09339804dff073dd0"
dir_1_hash_without_dots = "1020906e154bc7243ed1c63ce12edac8"
foo_hash = "7034f113c8a5fefebfb52ff38cd29ed2"

output = False


class TestDirs(unittest.TestCase):
    def test_matching_dirs(self):
        print("matching dirs")
        result = chksum.cli(["./test/dir_1", "./test/dir_1", "md5"])
        assert result == 0
        print("PASS\n----")

    def test_not_matching_dirs(self):
        print("not matching dirs")
        result = chksum.cli(["./test/dir_1", "./test/dir_2", "md5"])
        assert result == 1
        print("PASS\n----")


class TestDots(unittest.TestCase):
    def test_dir_with_dots(self):
        print("dir with dots")
        result = chksum.cli(["./test/dir_1", dir_1_hash_with_dots, "md5"])
        assert result == 0
        print("PASS\n----")
    
    def test_dir_without_dots(self):
        print("dir without dots")
        result = chksum.cli(["./test/dir_1", dir_1_hash_without_dots, "md5", "-d"])
        assert result == 0
        print("PASS\n----")


class TestFiles(unittest.TestCase):
    def test_matching_files(self):
        print("matching files")
        result = chksum.cli(["./test/dir_1/foo.txt", "./test/dir_1/foo.txt", "md5"])
        assert result == 0
        print("PASS\n----")

    def test_not_matching_files(self):
        print("non matching files")
        result = chksum.cli(["./test/dir_1/foo.txt", "./test/dir_2/bar.txt", "md5"])
        assert result == 1
        print("PASS\n----")

    def test_file_hashing(self):
        print("file hashing")
        result = chksum.cli(["./test/dir_1/foo.txt", foo_hash, "md5"])
        assert result == 0
        print("PASS\n----")
        

class TestStrings(unittest.TestCase):
    def test_matching_strings(self):
        print("matching strings")
        result = chksum.cli(["9b50fd1de4a200b09339804dff073dd0", "9b50fd1de4a200b09339804dff073dd0", "md5"])
        assert result == 0
        print("PASS\n----")

    def test_not_matching_strings(self):
        print("non matching strings")
        result = chksum.cli(["9b50fd1de4a200b09339804dff073dd0", "1020906e154bc7243ed1c63ce12edac8"])
        assert result == 1
        print("PASS\n----")

    def test_not_same_size_strings(self):
        print("dif size strings")
        result = chksum.cli(["9b50fd1de4a200b09339804dff073dd0", "102096e154bced1c63ce12edff073"])
        assert result == 1
        print("PASS\n----")


if __name__ == '__main__':
    output = True
    unittest.main()