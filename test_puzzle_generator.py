import unittest
import operator

from .puzzle_generator import *


class TestIsOfTypeStatement(unittest.TestCase):
    def setUp(self):
        self.s = Scenario(puzzle=None, character_types={
            'A': Knave,
            'B': Knight,
        })

    def test_1(self):
        statement = IsOfType('A', Knight)
        self.assertFalse(statement.evaluate_truth(self.s))
        self.assertFalse(statement.evaluate_consistency(Knight, self.s))
        self.assertTrue(statement.evaluate_consistency(Knave, self.s))

    def test_2(self):
        statement = IsOfType('B', Knight)
        self.assertTrue(statement.evaluate_truth(scenario=self.s))
        self.assertTrue(statement.evaluate_consistency(Knight, self.s))
        self.assertFalse(statement.evaluate_consistency(Knave, self.s))


class TestConjunctiveStatement(unittest.TestCase):
    def setUp(self):
        self.s = Scenario(puzzle=None, character_types={
            'A': Knave,
            'B': Knight,
        })

    def test_1(self):
        s = Scenario(puzzle=None, character_types={
            'A': Knave,
            'B': Knight,
        })
        statement = IsOfType('A', Knight)


@unittest.skip
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


@unittest.skip
class TestSimplePuzzles(unittest.TestCase):
    def test_lecture_1_puzzle(self):
        p = Puzzle({
            'A': [
                IsOfType('A', Knave),
                IsOfType('B', Knave),
            ],
            'B': [],
        })
        p.generate_and_check_scenarios(should_print=True)
        correct_scenarios = p.get_consistent_scenario_set()
        print(correct_scenarios)
        self.assertSetEqual(correct_scenarios, {Scenario(puzzle=p, character_types={
            'A': Knave,
            'B': Knight,
        })})

    def test_lecture_1_puzzle_variety_2(self):
        p = Puzzle({
            'A': [CountOfType(Knave, 2, operator.eq)],
            'B': [],
        })
        p.generate_and_check_scenarios(should_print=True)
        correct_scenarios = p.get_consistent_scenario_set()
        print(correct_scenarios)
        self.assertSetEqual(correct_scenarios, {Scenario(puzzle=p, character_types={
            'A': Knave,
            'B': Knight,
        })})

    def _test_lecture_3_puzzle(self):
        p = Puzzle({
            'Alfred': [CountOfType(Knight, 1, operator.eq)],
            'Betty': [SamenessCount(3, operator.eq)],
            'Clara': [],
        })
        p.generate_and_check_scenarios(should_print=True)
        correct_scenarios = p.get_consistent_scenario_set()
        print(correct_scenarios)
