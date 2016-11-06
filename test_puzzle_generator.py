import unittest

from .puzzle_generator import *


class TestBasicPuzzleElements(unittest.TestCase):
    character_names = ['Alice', 'Bob', 'Charlie', 'Doug', 'Ellie', 'Frank', 'Gillian']

    def make_basic_puzzle(self, num_characters=3):
        css = {}
        for i in range(num_characters):
            name = self.character_names[i]
            statements = []
            css[name] = statements
        return Puzzle(character_names_and_statements=css)

    def test_puzzle_num_characters(self):
        p3 = self.make_basic_puzzle(3)
        self.assertEqual(p3.num_characters, 3)
        p4 = self.make_basic_puzzle(4)
        self.assertEqual(p4.num_characters, 4)

    def test_max_monks_odd(self):
        p3 = self.make_basic_puzzle(3)
        self.assertEqual(p3.max_num_monks, 1)

        p5 = self.make_basic_puzzle(5)
        self.assertEqual(p5.max_num_monks, 2)

    def test_max_monks_even(self):
        p4 = self.make_basic_puzzle(4)
        self.assertEqual(p4.max_num_monks, 1)

        p6 = self.make_basic_puzzle(6)
        self.assertEqual(p6.max_num_monks, 2)


class TestSimplePuzzles(unittest.TestCase):
    def test_day_1_puzzle(self):
        p = Puzzle({
            'Alice': [
                ConjunctiveStatement(
                    IsOfType('Alice', Knave),
                    IsOfType('Bob', Knave),
                )],
            'Bob': []
        })
        p.generate_and_check_scenarios()
