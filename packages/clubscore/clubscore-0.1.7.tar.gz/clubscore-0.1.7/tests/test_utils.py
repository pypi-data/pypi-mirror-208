import unittest
from PIL import Image
import os
from clubscore.utils import coloraPNG, diagonal_resize, matchWord, getTeams


class TestUtils(unittest.TestCase):


    def test_matchWord(self):
        s = "Juventus"
        arr = ["Milan", "Inter", "Roma", "Juve"]
        matched_word = matchWord(s, arr)
        self.assertEqual(matched_word, "juve")

    def test_match_not_found(self):
        # Test when a match is not found in the array
        s = "Napoli"
        arr = ["Juventus", "Inter", "Milan", "Roma"]
        with self.assertRaises(Exception):
            matchWord(s, arr)

    def test_match_closest_found(self):
        # Test when a match is not found, but a close match is found
        s = "Napli"
        arr = ["Juventus", "Inter", "Milan", "napoli"]
        self.assertEqual(matchWord(s, arr), "napoli")



if __name__ == '__main__':
    unittest.main()
