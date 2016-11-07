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

    def test_2(self):
        statement = IsOfType('B', Knight)
        self.assertTrue(statement.evaluate_truth(scenario=self.s))


class TestCharacterConsistency(unittest.TestCase):
    def setUp(self):
        self.s = Scenario(puzzle=None, character_types={
            'A': Knave,
        })
        self.true_statement = IsOfType('A', Knave)
        self.false_statement = IsOfType('A', Monk)

    # Consistent
    def test_knight_tells_truth(self):
        self.assertTrue(self.true_statement.evaluate_consistency(Knight, self.s))

    # Inconsistent
    def test_knight_does_not_lie(self):
        self.assertFalse(self.false_statement.evaluate_consistency(Knight, self.s))

    # Inconsistent
    def test_knave_does_not_tell_truth(self):
        self.assertFalse(self.true_statement.evaluate_consistency(Knave, self.s))

    # Consistent
    def test_knave_lies(self):
        self.assertTrue(self.false_statement.evaluate_consistency(Knave, self.s))

    # Consistent
    def test_monk_tells_truth(self):
        self.assertTrue(self.true_statement.evaluate_consistency(Monk, self.s))

    # Consistent
    def test_monk_lies(self):
        self.assertTrue(self.false_statement.evaluate_consistency(Monk, self.s))


class TestConjunctiveStatement(unittest.TestCase):
    def setUp(self):
        self.s = Scenario(puzzle=None, character_types={
            'A': Knave,
            'B': Knight,
            'C': Monk,
        })

    def test_1(self):
        self.assertTrue(ConjunctiveStatement(
            IsOfType('A', Knave),
            IsOfType('C', Monk),
        ).evaluate_truth(self.s))

    def test_2(self):
        self.assertTrue(ConjunctiveStatement(
            IsOfType('A', Knave),
            IsOfType('B', Knight),
            IsOfType('C', Monk),
        ).evaluate_truth(self.s))

    def test_3(self):
        self.assertFalse(ConjunctiveStatement(
            IsOfType('A', Knave),
            IsOfType('B', Knight),
            IsOfType('C', Knight),
        ).evaluate_truth(self.s))

    def test_4(self):
        self.assertFalse(ConjunctiveStatement(
            IsOfType('A', Monk),
        ).evaluate_truth(self.s))

    def test_5(self):
        self.assertTrue(ConjunctiveStatement().evaluate_truth(self.s))


class TestBasicPuzzleElements(unittest.TestCase):
    character_names = ['Alice', 'Bob', 'Charlie', 'Doug', 'Ellie', 'Frank', 'Gillian']

    def make_basic_puzzle(self, num_characters=3, allow_monks=True):
        css = {}
        for i in range(num_characters):
            name = self.character_names[i]
            statements = []
            css[name] = statements
        return Puzzle(character_names_and_statements=css, allow_monks=allow_monks)

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

    def test_max_monks_disallow_monks_puzzle(self):
        p = self.make_basic_puzzle(4, allow_monks=False)
        self.assertEqual(p.max_num_monks, 0)


class TestPuzzles(unittest.TestCase):
    def assertPuzzleSolution(self, setup, solution_set, allow_monks=True):
        p = Puzzle(setup, allow_monks=allow_monks)
        p.generate_and_check_scenarios()
        correct_scenarios = set()
        for solution in solution_set:
            correct_scenarios.add(Scenario(puzzle=p, character_types=solution))
        self.assertSetEqual(p.get_consistent_scenario_set(), correct_scenarios)
        self.assertEqual(p.get_solution_count(), len(correct_scenarios))

    def test_lecture_1_puzzle(self):
        p = Puzzle({
            'A': [
                IsOfType('A', Knave),
                IsOfType('B', Knave),
            ],
            'B': [],
        })
        p.generate_and_check_scenarios()
        correct_scenarios = p.get_consistent_scenario_set()
        self.assertSetEqual(correct_scenarios, {Scenario(puzzle=p, character_types={
            'A': Knave,
            'B': Knight,
        })})

    def test_lecture_1_puzzle_variety_2(self):
        p = Puzzle({
            'A': [CountOfType(Knave, 2, operator.eq)],
            'B': [],
        })
        p.generate_and_check_scenarios()
        correct_scenarios = p.get_consistent_scenario_set()
        self.assertSetEqual(correct_scenarios, {
            Scenario(puzzle=p, character_types={
                'A': Knave,
                'B': Knight,
            }),
        })

    def test_lecture_3_puzzle(self):
        p = Puzzle({
            'Alfred': CountOfType(Knight, 1, operator.eq),
            'Betty': SamenessCount(3, operator.eq),
            'Clara': [],
        }, allow_monks=False)
        p.generate_and_check_scenarios()
        correct_scenarios = p.get_consistent_scenario_set()
        self.assertSetEqual(correct_scenarios, {
            Scenario(puzzle=p, character_types={
                'Alfred': Knight,
                'Betty': Knave,
                'Clara': Knave,
            }),
        })

    def test_lecture_4_puzzle(self):
        p = Puzzle({
            'Alfred': IsSameAs('Betty', 'Clara'),
            'Betty': Not(SamenessCount(3, operator.eq)),
            'Clara': [],
        }, allow_monks=False)
        p.generate_and_check_scenarios()
        correct_scenarios = p.get_consistent_scenario_set()
        self.assertSetEqual(correct_scenarios, {
            Scenario(puzzle=p, character_types={
                'Alfred': Knave,
                'Betty': Knight,
                'Clara': Knave,
            }),
        })

    def test_posted_solution_14(self):
        self.assertPuzzleSolution({
            'A': CountOfType(Knave, 3, operator.eq),
            'B': CountOfType(Knave, 2, operator.eq),
            'C': [],
        }, [{
            'A': Knave,
            'B': Knight,
            'C': Knave,
        }], allow_monks=False)

    def test_posted_solution_15(self):
        self.assertPuzzleSolution({
            'A': Honesty('B', 'C', operator.ge),
            'B': Honesty('C', 'A', operator.ge),
            'C': Honesty('A', 'B', operator.ge),
        }, [{
            'A': Knight,
            'B': Knight,
            'C': Knight,
        }], allow_monks=False)

    def test_posted_solution_17(self):
        self.assertPuzzleSolution({
            'A': DisjunctiveStatement(
                CountOfType(Knave, 1, operator.eq),
                CountOfType(Knave, 3, operator.eq),
            ),
            'B': IsSameAs('A', 'C'),
            'C': Not(IsSameAs('A', 'D')),
            'D': CountOfType(Knight, 1, operator.eq),
        }, [{
            'A': Knight,
            'B': Knight,
            'C': Knight,
            'D': Knave,
        }], allow_monks=False)

    def test_posted_solution_18(self):
        self.assertPuzzleSolution({
            'A': DisjunctiveStatement(
                ConjunctiveStatement(
                    IsOfType('A', Knight),
                    CountOfType(Knight, 2, operator.ge),
                ),
                ConjunctiveStatement(
                    IsOfType('A', Knave),
                    CountOfType(Knave, 2, operator.ge)
                )
            ),
            'B': CountOfType(Knight, 2, operator.eq),
            'C': DisjunctiveStatement(
                IsOfType('A', Knight),
                IsOfType('D', Knight),
            ),
            'D': [],
        }, [{
            'A': Knight,
            'B': Knave,
            'C': Knight,
            'D': Knight,
        }], allow_monks=False)

    def test_posted_solution_19(self):
        self.assertPuzzleSolution({
            'A': CountOfType(Knight, 2, operator.gt),
            'B': CountOfType(Knave, 2, operator.gt),
            'C': Honesty('B', 'A', operator.ge),
            'D': [],
        }, [{
            'A': Knave,
            'B': Knave,
            'C': Knight,
            'D': Knight,
        }], allow_monks=False)

    def test_random_1(self):
        self.assertPuzzleSolution({
            'A': IsOfType('C', Knight),
            'B': Honesty('A', 'B', operator.gt),
            'C': SamenessCount(1, operator.le),
        }, [{
        }])


