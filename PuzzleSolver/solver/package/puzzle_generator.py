import csv
import statistics
from typing import List, Tuple, Dict

import abc
import itertools
import operator
import logging

import time

import random
from tqdm import tqdm

import functools

import math
import os

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

DEBUG = False
if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.WARNING)

MULTIPLIERS = {
    7: 1,
    6: 1.25,
    5: 1.5,
    4: 2,
    3: 2.5,
}
CHARACTER_COUNT_BOUND = [3, 7]
SOLUTION_COUNT_BOUND = [0, 2]
ALLOWED_REASON_DISTRIBUTION_DELTA = 0.25


class CharacterIdentifierError(Exception):
    pass


class TooManyMonksError(Exception):
    def __init__(self, monk_count):
        self.message = "You asked for {} Monks, which is too many here.".format(monk_count)

    def __repr__(self):
        return self.message


class Character:
    title = '---Not Set---'
    short_identifier = '_'
    truth_quantifier = '_'

    def __str__(self):
        return "{}".format(self.title)

    def tells_truth_more_often_than(self, character):
        return self.truth_quantifier > character.truth_quantifier

    def tells_truth_less_often_than(self, character):
        return self.truth_quantifier < character.truth_quantifier

    def tells_truth_at_least_as_often_as(self, character):
        return self.truth_quantifier >= character.truth_quantifier

    def tells_truth_less_often_or_the_same_as(self, character):
        return self.truth_quantifier <= character.truth_quantifier


class Knight(Character):
    title = 'Knight'
    short_identifier = 'K'
    truth_quantifier = 1


class Monk(Character):
    title = 'Monk'
    short_identifier = 'M'
    truth_quantifier = 0


class Knave(Character):
    title = 'Knave'
    short_identifier = 'V'
    truth_quantifier = -1


POSSIBLE_CHARACTERS = {Knight, Knave, Monk}


class Reason:
    def __init__(self, character_name, statement):
        self.character_name = character_name
        self.statement = statement

    def __str__(self):
        return "{} should not have said {}".format(self.character_name, self.statement)


class Scenario:
    def __init__(self, puzzle, character_types: {str: type}):
        self.puzzle = puzzle  # type: Puzzle
        self.character_types = character_types
        self.result = None  # Will be set after consistency is evaluated.

    def _check_consistency(self) -> Tuple[bool, List[Reason]]:
        """
        If it makes sense that each character would speak their respective phrases, returns True; otherwise False.

        If False, returns a list of Reasons why it could have failed.

        :returns: (is_consistent, reasons)
        """
        reasons = []
        is_consistent = True
        for character_name, statements in self.puzzle.character_statements.items():
            speaking_character_type = self.character_types[character_name]

            # Note: Each of the statements this character says must be consistent independently.
            for statement in statements:
                if statement.evaluate_consistency(speaking_character_type=speaking_character_type, scenario=self) is False:
                    reasons.append(Reason(character_name, statement))
                    is_consistent = False
        return is_consistent, reasons

    def check_consistency(self) -> Tuple[bool, List[Reason]]:
        result = self._check_consistency()
        self.result = result
        return result

    def __eq__(self, other):
        """
        To be equal, two Scenario instances must only have the same character name-type assignments and character count.
        """
        assert(isinstance(other, Scenario))
        if len(self.character_types) != len(other.character_types):
            return False
        for name, t in self.character_types.items():
            if other.character_types[name] != t:
                return False
        return True

    def __hash__(self):
        """
        TODO: This could be more efficient and less stupid.  ;)
        """
        character_string = "|"
        for name in sorted(self.character_types):
            t = self.character_types[name]
            character_string += "{},{}|".format(name, t.short_identifier)
        return hash(character_string)

    def __str__(self, joiner=" \t "):
        names_and_identities = []
        ordered_character_names = sorted(self.character_types.keys())
        for name in ordered_character_names:
            character_type = self.character_types[name]
            names_and_identities.append("{}={}".format(name, character_type.short_identifier))
        return joiner.join(names_and_identities)

    def __repr__(self):
        return "<Scenario: {}>".format(self.__str__(joiner=', '))


class Statement:
    def evaluate_consistency(self, speaking_character_type, scenario: Scenario):
        logger.debug('Evaluating consistency of "{}" as {}'.format(self, speaking_character_type.title))
        if speaking_character_type == Monk:
            return True
        truth = self.evaluate_truth(scenario=scenario)
        if speaking_character_type == Knight:
            return truth
        if speaking_character_type == Knave:
            return not truth

    @abc.abstractmethod
    def evaluate_truth(self, scenario: Scenario) -> True | False:
        raise NotImplementedError(type(self).__name__)

    @abc.abstractmethod
    def as_sentence(self):
        raise NotImplementedError(type(self).__name__)

    @abc.abstractclassmethod
    def generate_possibilities(cls, names, kinds):
        raise NotImplementedError(cls.__name__)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.is_equal_to_instance(other)

    @abc.abstractmethod
    def is_equal_to_instance(self, other):
        raise NotImplementedError(type(self).__name__)

    def __str__(self):
        return '{}'.format(self.as_sentence())

    def __repr__(self):
        return "<{}: {}>".format(type(self).__name__, str(self))


class TrueStatement(Statement):
    def evaluate_truth(self, scenario: Scenario):
        return True

    def as_sentence(self):
        return "2+2=4."


class AbstractStatementCombiner(Statement):
    joining_string = " --- "

    def __init__(self, *statements: [Statement]):
        self.statements = statements

    @abc.abstractmethod
    def for_each_statement(self, truth_value):
        """
        If returns None, loop will continue.  If returns other, evaluation is finished with this final value.
        :return: True | False | None
        """
        pass

    @abc.abstractmethod
    def default_value(self):
        """
        :return: True | False
        """
        pass

    def evaluate_truth(self, scenario: Scenario):
        logger.debug("Evaluating truth of [{}] ".format(self))
        for statement in self.statements:
            truth = statement.evaluate_truth(scenario=scenario)
            result = self.for_each_statement(truth_value=truth)
            if result is not None:
                return result
        return self.default_value()

    def __str__(self):
        return self.joining_string.join(map(lambda s: '({})'.format(s), self.statements))


class ConjunctiveStatement(AbstractStatementCombiner):
    """
    Requires every statement to be true.  If no statements, value is true.
    """
    joining_string = ' AND '

    def for_each_statement(self, truth_value):
        if truth_value is False:
            return False
        return None

    def default_value(self):
        return True


class DisjunctiveStatement(AbstractStatementCombiner):
    """
    Requires at least one statement to be true.  If no statements, value is false.
    """
    joining_string = ' OR '

    def for_each_statement(self, truth_value):
        if truth_value is True:
            return True
        return None

    def default_value(self):
        return False


class Not(Statement):
    """
    True if and only if the passed statement is False.
    """
    def __init__(self, statement: Statement):
        self.statement = statement

    def evaluate_truth(self, scenario: Scenario):
        truth = self.statement.evaluate_truth(scenario=scenario)
        return not truth

    def __str__(self):
        return "NOT({})".format(self.statement)


class IsOfType(Statement):
    """
    True if and only if the named target is of the claimed character type.
    """
    def __init__(self, target_name: str, claimed_character_type):
        self.target_name = target_name
        self.claimed_character_type = claimed_character_type

    def evaluate_truth(self, scenario: Scenario):
        try:
            return scenario.character_types[self.target_name] == self.claimed_character_type
        except KeyError:
            raise CharacterIdentifierError("Cannot find character '{}'.".format(self.target_name))

    def as_sentence(self):
        return "{} is a {}.".format(self.target_name, self.claimed_character_type.title)

    @classmethod
    def generate_possibilities(cls, names, kinds):
        possibilities = []
        for name, kind in itertools.product(names, kinds):
            possibilities.append(cls(target_name=name, claimed_character_type=kind))
        return possibilities

    def is_equal_to_instance(self, other):
        assert isinstance(other, IsOfType)
        return self.target_name == other.target_name and self.claimed_character_type == other.claimed_character_type


class IsSameAs(Statement):
    def __init__(self, target_1_name: str, target_2_name: str):
        self.target_1_name = target_1_name
        self.target_2_name = target_2_name

    def evaluate_truth(self, scenario: Scenario):
        try:
            target_1_kind = scenario.character_types[self.target_1_name]
        except KeyError:
            raise CharacterIdentifierError("Cannot find character '{}'.".format(self.target_1_name))

        try:
            target_2_kind = scenario.character_types[self.target_2_name]
        except KeyError:
            raise CharacterIdentifierError("Cannot find character '{}'.".format(self.target_2_name))

        return target_1_kind == target_2_kind

    def as_sentence(self):
        return "{} is the same as {}.".format(self.target_1_name, self.target_2_name)

    @classmethod
    def generate_possibilities(cls, names, kinds):
        ret = []
        for n1, n2 in itertools.combinations(names, 2):
            ret.append(IsSameAs(n1, n2))
        return ret

    def is_equal_to_instance(self, other):
        assert(isinstance(other, IsSameAs))
        return self.target_1_name == other.target_1_name and self.target_2_name == other.target_2_name


def lookup(scenario: Scenario, *keys):
    ret = []
    for key in keys:
        try:
            ret.append(scenario.character_types[key])
        except KeyError:
            raise CharacterIdentifierError("Cannot find character '{}'.".format(key))
    return tuple(ret)


class Honesty(Statement):
    def __init__(self, target_1_name, target_2_name, claimed_relation):
        self.target_1_name = target_1_name
        self.target_2_name = target_2_name
        self.claimed_relation = claimed_relation

    def evaluate_truth(self, scenario: Scenario):
        target_1_kind, target_2_kind = lookup(scenario, self.target_1_name, self.target_2_name)
        return self.claimed_relation(target_1_kind.truth_quantifier, target_2_kind.truth_quantifier)

    def as_sentence(self):
        return "{}'s honesty is {} {}'s honesty.".format(
            self.target_1_name,
            english_operator_helper(self.claimed_relation),
            self.target_2_name,
        )

    @classmethod
    def generate_possibilities(cls, names, kinds):
        name_combinations = itertools.combinations(names, 2)
        ret = []
        for (a, b) in name_combinations:
            ret.append(Honesty(a, b, operator.le))
        return ret

    def is_equal_to_instance(self, other):
        assert(isinstance(other, Honesty))
        return (
            self.target_1_name == other.target_1_name
            and self.target_2_name == other.target_2_name
            and self.claimed_relation == other.claimed_relation
        )


def english_operator_helper(relation):
    if relation == operator.eq:
        return 'exactly'
    elif relation == operator.lt:
        return 'less than'
    elif relation == operator.gt:
        return 'more than'
    elif relation == operator.le:
        return 'less than or exactly'
    elif relation == operator.ge:
        return 'more than or exactly'
    else:
        raise Exception("Cannot handle operator of type {}.".format(relation))


class CountOfType(Statement):
    def __init__(self, character_type, claimed_count: int, claimed_relation):
        self.character_type = character_type
        self.claimed_count = claimed_count
        self.claimed_relation = claimed_relation

    def evaluate_truth(self, scenario: Scenario):
        count = 0
        for t in scenario.character_types.values():
            if t == self.character_type:
                count += 1
        return self.claimed_relation(count, self.claimed_count)

    def as_sentence(self):
        return "There are {op} {count} {kind}s.".format(
            op=english_operator_helper(self.claimed_relation),
            count=self.claimed_count,
            kind=self.character_type.title,
        )

    @classmethod
    def generate_possibilities(cls, names, kinds):
        ret = []
        count = len(names) // 2
        for kind in kinds:
            ret.append(CountOfType(kind, count, operator.le))
        return ret

    def is_equal_to_instance(self, other):
        assert(isinstance(other, CountOfType))
        return (
            self.character_type == other.character_type
            and self.claimed_count == other.claimed_count
            and self.claimed_relation == other.claimed_relation
        )


class AbstractConnective(Statement):
    def __init__(self, a: Statement, b: Statement):
        self.a = a
        self.b = b

    @staticmethod
    @abc.abstractstaticmethod
    def evaluate_connective(a: bool, b: bool):
        raise NotImplementedError

    def evaluate_truth(self, scenario: Scenario):
        return self.evaluate_connective(
            self.a.evaluate_truth(scenario=scenario),
            self.b.evaluate_truth(scenario=scenario)
        )


class IfConnective(AbstractConnective):
    @staticmethod
    def evaluate_connective(a: bool, b: bool):
        return (not a) or b

    def as_sentence(self):
        return "{} only if {}.".format(self.a, self.b)


class Biconditional(AbstractConnective):
    @staticmethod
    def evaluate_connective(a: bool, b: bool):
        return (a and b) or (not a and not b)

    def as_sentence(self):
        return "{} if and only if {}.".format(self.a, self.b)


class ExclusiveOrConnective(AbstractConnective):
    @staticmethod
    def evaluate_connective(a: bool, b: bool):
        return (a or b) and not(a and b)

    def as_sentence(self):
        return "{} OR {}, BUT NOT BOTH.".format(self.a, self.b)


class SamenessCount(Statement):
    def __init__(self, claimed_count: int, claimed_relation):
        raise NotImplementedError("SamenessCount isn't working properly yet.")

        self.claimed_count = claimed_count
        self.claimed_relation = claimed_relation

        # FIXME: This allow a single character type to satisfy the condition. All character types must satisfy the condition.
        required_statements_to_satisfy = []
        for kind in POSSIBLE_CHARACTERS:
            required_statements_to_satisfy.append(
                CountOfType(kind, self.claimed_count, self.claimed_relation)
            )
        self.conjunctive_statement = ConjunctiveStatement(*required_statements_to_satisfy)

    def evaluate_truth(self, scenario: Scenario):
        """
        If one of the possible character types satisfies this statement, then it is true.
        """
        return self.conjunctive_statement.evaluate_truth(scenario=scenario)

    def as_sentence(self):
        return "{op} {count} of us are the same.".format(
            op=english_operator_helper(self.claimed_relation),
            count=self.claimed_count,
        )

    @classmethod
    def generate_possibilities(cls, names, kinds):
        ret = []
        total = len(names)
        ret.append(SamenessCount(total // 2, operator.le))
        return ret


class AllTheSame(Statement):
    def evaluate_truth(self, scenario: Scenario):
        kind = None
        for cur in scenario.character_types.values():
            if kind is not None:
                if cur != kind:
                    return False
            kind = cur
        return True

    def as_sentence(self):
        return "All of us are the same."


class AllDifferent(Statement):
    def evaluate_truth(self, scenario: Scenario):
        """
        If any distinct two are the same, returns False.
        """
        for n1, k1 in scenario.character_types.items():
            for n2, k2 in scenario.character_types.items():
                if n1 == n2:
                    continue
                if k1 == k2:
                    return False
        return True

    def as_sentence(self):
        return "All of us are different."


class Puzzle:
    def __init__(self, character_names_and_statements: {str: [Statement]}, allow_monks=True):
        self.is_solved = False
        self.scenarios = []
        self.character_names = []
        self.character_statements = {}
        self._rejection_reasons = []  # type: List[Reason]
        self._reason_count_per_scenario = -1  # type: List[int]

        for character_name, statements in character_names_and_statements.items():
            if statements is None:
                statements = []
            if not isinstance(statements, list):
                statements = [statements]
            self.character_names.append(character_name)
            self.character_statements[character_name] = statements

        self.max_num_monks = self._calculate_max_num_monks(allow_monks=allow_monks)

    @property
    def num_characters(self):
        return len(self.character_names)

    def get_character_statements_as_string(self):
        ret = ""
        for name in sorted(self.character_names):
            ret += "\n{}".format(name)
            for statement in self.character_statements[name]:
                ret += "\n\t {}".format(statement)
        return ret

    def print_puzzle_with_solutions(self):
        print(self.get_character_statements_as_string())
        print(self.get_solution_count(), 'possible solutions exist')
        self.solve(should_print=True)

    def _calculate_max_num_monks(self, allow_monks):
        """
        Determines the maximum number of Monks allowed in a puzzle of this size.
        (Less than half the number of characters.)
        """
        if allow_monks is False:
            return 0
        max_num_monks = self.num_characters // 2
        if max_num_monks == self.num_characters / 2:
            max_num_monks -= 1
        return max_num_monks

    def _generate_scenario(self, identity_ordering: [type]):
        """
        Generates a scenario, rejecting a scenario with too many Monks.
        """
        character_types = {}
        i = 0
        monk_count = 0
        for name in self.character_names:
            if identity_ordering[i] == Monk:
                monk_count += 1
            character_types[name] = identity_ordering[i]
            if monk_count > self.max_num_monks:
                raise TooManyMonksError(monk_count)
            i += 1
        return Scenario(puzzle=self, character_types=character_types)

    def _generate_scenarios(self):
        self.scenarios = []  # Clears all scenarios first.
        possible_characters = set(POSSIBLE_CHARACTERS)
        if self.max_num_monks == 0:
            # Optimizes product if no monks are allowed.
            possible_characters.remove(Monk)
        for identity_ordering in itertools.product(possible_characters, repeat=self.num_characters):
            try:
                scenario = self._generate_scenario(identity_ordering)
            except TooManyMonksError:
                continue
            self.scenarios.append(scenario)

    @functools.lru_cache()
    def check_scenario(self, scenario, should_print=DEBUG):
        result, reasons = scenario.check_consistency()
        if should_print:
            if result:
                print('+++++ \t{}'.format(scenario))
            else:
                if DEBUG is True:
                    print('----- \t{} \t ---> {}'.format(scenario, reasons[0]))
        return result, reasons

    def solve(self, should_print=DEBUG, save_work_to_csv=None):
        if len(self.scenarios) == 0:
            self._generate_scenarios()
        self._rejection_reasons = []
        scenarios, results, reasons = [], [], []
        reason_counts = []
        for scenario in self.scenarios:
            is_scenario_consistent, scenario_reasons = self.check_scenario(scenario=scenario, should_print=should_print)
            if save_work_to_csv:
                scenarios.append(scenario)
                results.append(is_scenario_consistent)
            reason_counts.append(len(scenario_reasons))
            reasons.append(scenario_reasons)  # We'll use the reasons even if not saving to CSV.
        if save_work_to_csv:
            with open(save_work_to_csv, 'w') as f:
                writer = csv.writer(f)
                i = 0
                for scenario, is_scenario_consistent, scenario_reasons in itertools.zip_longest(scenarios, results, reasons):
                    assert(isinstance(scenario, Scenario))
                    assert(isinstance(is_scenario_consistent, bool))
                    assert(isinstance(scenario_reasons, List[Reason]) or scenario_reasons is None)
                    if i == 0:
                        header_row = []
                        for name in sorted(scenario.character_types.keys()):
                            header_row.append(name)
                        header_row += [
                            'Result',
                            'Explanation',
                        ]
                        writer.writerow(header_row)
                    row = []
                    for name in sorted(scenario.character_types):
                        kind = scenario.character_types[name]
                        assert(issubclass(kind, Character))
                        row.append(kind.short_identifier)
                    row.append('Consistent' if is_scenario_consistent else 'Inconsistent')
                    if scenario_reasons:
                        row.append(scenario_reasons)
                    writer.writerow(row)
                    i += 1
        self._rejection_reasons = reasons
        self._reason_count_per_scenario = reason_counts
        self.is_solved = True

    @functools.lru_cache()
    def get_consistent_scenario_set(self):
        ret = set()
        for scenario in self.scenarios:
            if scenario.result[0] is True:
                ret.add(scenario)
        return ret

    @functools.lru_cache()
    def get_solution_count(self):
        if not self.is_solved:
            self.solve()
        return len(self.get_consistent_scenario_set())

    @functools.lru_cache()
    def get_rejection_reason_count(self) -> int:
        if not self.is_solved:
            self.solve()
        return len(self._rejection_reasons)

    def get_reason_counts_per_scenario(self):
        if not self.is_solved:
            self.solve()
        return self._reason_count_per_scenario

    @functools.lru_cache()
    def get_rejection_reasons_distribution(self) -> Dict[str, float]:
        if not self.is_solved:
            self.solve()
        hist = dict()
        for reason in self._rejection_reasons:
            if reason not in hist:
                hist[reason] = 0
            hist[reason] += 1
        dist = dict()
        for reason, count in hist.items():
            dist[reason] = count / len(self._rejection_reasons)
        return dist

    @functools.lru_cache()
    def has_optimal_reason_distribution(self) -> bool:
        reason_dist = self.get_rejection_reasons_distribution()
        reason_dist_count = len(reason_dist)
        min_allowed_percent = 1 / reason_dist_count - ALLOWED_REASON_DISTRIBUTION_DELTA
        max_allowed_percent = 1 / reason_dist_count + ALLOWED_REASON_DISTRIBUTION_DELTA
        for reason, percent in reason_dist.items():
            if not(min_allowed_percent <= percent <= max_allowed_percent):
                return False
        return True

    @functools.lru_cache()
    def get_total_possibilities(self):
        return len(self.scenarios)

    def is_valid_puzzle(self):
        return (
            (CHARACTER_COUNT_BOUND[0] <= self.num_characters <= CHARACTER_COUNT_BOUND[1])
            and (SOLUTION_COUNT_BOUND[0] <= self.get_solution_count() <= SOLUTION_COUNT_BOUND[1])
        )

    def get_puzzle_score(self):
        multiplier = MULTIPLIERS[self.num_characters]

    def has_maximum_monks(self):
        if not self.is_solved:
            self.solve()
        for consistent_scenario in self.get_consistent_scenario_set():
            assert(isinstance(consistent_scenario, Scenario))
            monks = 0
            for name, kind in consistent_scenario.character_types.items():
                if kind == Monk:
                    monks += 1
            if monks == self.max_num_monks:
                return True
        return False

    def __str__(self):
        return self.character_names


class PuzzleGenerator:
    def __init__(self, character_names, possible_statement_kinds):
        self.possible_names = character_names
        self.possible_statement_kinds = possible_statement_kinds

    def generate_possible_statements(self):
        statements = []
        for statement_kind in self.possible_statement_kinds:
            statements += statement_kind.generate_possibilities(self.possible_names, POSSIBLE_CHARACTERS)

        # Bonus Statements
        # statements.append(IsOfType('B', Knave))
        # statements.append(IsOfType('B', Monk))
        # statements.append(IsOfType('C', Monk))
        # statements.append(IsOfType('C', Knight))

        return statements

    def generate_puzzles(self, to_file=True):
        statements = self.generate_possible_statements()
        statements_needed = 6  # Generates the combination of this many statements for `s`.
        total_count = math.factorial(len(statements)) / math.factorial(len(statements) - statements_needed)
        print(len(statements), 'statements to choose from')
        print(total_count, 'total possible permutations')

        good_puzzles = []
        valid_puzzle_count = 0  # A valid puzzle has 0, 1, or 2 solutions.

        possible_statement_combinations = list(itertools.permutations(statements, statements_needed))
        random.shuffle(possible_statement_combinations)
        i = 0
        mean_reason_counts = []
        EARLY_BREAK = 0.5
        progress = tqdm(total=total_count * EARLY_BREAK, smoothing=0.15)

        def update_progress():
            progress.update()
            progress.set_description("{good:0.1f}% good ({good_count}) // avg reason count: {reason_count:0.2f} // {valid:0.1f}% valid".format(
                good=len(good_puzzles) / i * 100,
                good_count=len(good_puzzles),
                reason_count=statistics.mean(mean_reason_counts) if len(mean_reason_counts) > 0 else -1,
                valid=valid_puzzle_count / i * 100,
            ))

        for s in possible_statement_combinations:
            i += 1

            if i/total_count > EARLY_BREAK:
                break

            update_progress()

            puzzle = Puzzle({
                self.possible_names[0]: IfConnective(
                    Biconditional(s[3], IsOfType('B', Monk)),
                    Biconditional(Honesty('C', 'D', operator.gt), CountOfType(Knave, 2, operator.lt)),
                ),
                self.possible_names[1]: [
                    Biconditional(s[1], IsSameAs('A', 'D')),
                    Not(Biconditional(s[2], s[0])),
                ],
                self.possible_names[2]: Biconditional(s[4], s[5]),
                self.possible_names[3]: DisjunctiveStatement(
                    CountOfType(Knight, 2, operator.eq),
                    CountOfType(Knight, 4, operator.eq)
                ),
            })

            if not puzzle.is_valid_puzzle():
                continue
            valid_puzzle_count += 1

            #################################################
            # Restrictions to hopefully make puzzle harder. #
            #################################################

            if not (puzzle.get_solution_count() == 2
                    and puzzle.has_maximum_monks()):
                continue

            # Make sure each character says something fairly significant.
            # if not puzzle.has_optimal_reason_distribution():
            #     continue
            mean_reason_count = statistics.mean(puzzle.get_reason_counts_per_scenario())
            mean_reason_counts.append(mean_reason_count)
            if mean_reason_count > 1.8:
                continue

            scenarios = tuple(puzzle.get_consistent_scenario_set())
            # type: [Scenario]
            sol_a = scenarios[0].character_types
            sol_b = scenarios[1].character_types
            difference = 0
            for name in sol_a.keys():
                if sol_a[name] != sol_b[name]:
                    difference += 1
            # Make sure all characters differ in both solutions.  (To hopefully result in more difficult puzzles.)
            allowed_character_variance = 0
            if difference < len(puzzle.character_names) - allowed_character_variance:
                continue
            good_puzzles.append(puzzle)
            with open(os.path.join(os.path.curdir, 'good_puzzles_auto.txt'), 'a') as file:
                if to_file is False:
                    file = None
                print(puzzle.get_character_statements_as_string(), file=file)
                print('Solutions:', puzzle.get_consistent_scenario_set(), file=file)
                reason_counts = puzzle.get_reason_counts_per_scenario()
                print('Reasons to reject:', 'Avg. {:0.2f}'.format(statistics.mean(reason_counts)), reason_counts, file=file)
                print('', file=file)

        update_progress()
        time.sleep(0.5)  # Give progress bar time to update.
        progress.disable = True
        print('\n', len(good_puzzles), 'good puzzles found of', i)
        print('valid count', valid_puzzle_count)
