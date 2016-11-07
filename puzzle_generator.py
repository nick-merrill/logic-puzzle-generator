import abc
import itertools
import operator
import logging

import functools

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


class Scenario:
    def __init__(self, puzzle, character_types: {str: type}):
        self.puzzle = puzzle  # type: Puzzle
        self.character_types = character_types
        self.result = None  # Will be set after consistency is evaluated.

    def _check_consistency(self):
        """
        If it makes sense that each character would speak their respective phrases, returns True; otherwise False.

        If False, returns a reason.

        :rtype: (bool, str)
        :returns: (is_consistent, reason)
        """
        for character_name, statements in self.puzzle.character_statements.items():
            speaking_character_type = self.character_types[character_name]

            # In order to simplify the complexity of nested statements for debugging, we try not to over-encapsulate.
            statement_count = len(statements)
            if statement_count == 0:
                continue
            elif statement_count == 1:
                statement = statements[0]
            else:  # statement_count > 1
                # Note: All statements this character says must make sense independently.
                statement = ConjunctiveStatement(*statements)

            if statement.evaluate_consistency(speaking_character_type=speaking_character_type, scenario=self) is False:
                return False, '{} should not have said "{}".'.format(character_name, statement)
        return True, None

    def check_consistency(self):
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
        for name, character_type in self.character_types.items():
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
        pass

    @abc.abstractmethod
    def as_sentence(self):
        pass

    def __str__(self):
        return '{}'.format(self.as_sentence())

    def __repr__(self):
        return "<{}: {}>".format(type(self).__name__, str(self))


class AbstractStatementCombiner(Statement):
    joining_string = " --- "

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

    def __init__(self, *statements: [Statement]):
        self.statements = statements

    def evaluate_truth(self, scenario: Scenario):
        logger.debug("Evaluating truth of [{}] ".format(self))
        for statement in self.statements:
            truth = statement.evaluate_truth(scenario=scenario)
            result = self.for_each_statement(truth_value=truth)
            if result is not None:
                return result
        return self.default_value()

    def __str__(self):
        return " AND ".join(map(lambda s: '({})'.format(s), self.statements))


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
    def __init__(self, statement: Statement):
        self.statement = statement

    def evaluate_truth(self, scenario: Scenario):
        truth = self.statement.evaluate_truth(scenario=scenario)
        return not truth

    def __str__(self):
        return "NOT({})".format(self.statement)


class IsOfType(Statement):
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


def english_operator_helper(relation):
    if relation == operator.eq:
        return 'exactly'
    elif relation == operator.lt:
        return 'fewer than'
    elif relation == operator.gt:
        return 'more than'
    elif relation == operator.le:
        return 'fewer than or exactly'
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


class SamenessCount(Statement):
    def __init__(self, claimed_count: int, claimed_relation):
        self.claimed_count = claimed_count
        self.claimed_relation = claimed_relation

        satisfying_statements = []
        for kind in POSSIBLE_CHARACTERS:
            satisfying_statements.append(
                CountOfType(kind, self.claimed_count, self.claimed_relation)
            )
        self.disjunctive_statement = DisjunctiveStatement(*satisfying_statements)

    def evaluate_truth(self, scenario: Scenario):
        """
        If one of the possible character types satisfies this statement, then it is true.
        """
        return self.disjunctive_statement.evaluate_truth(scenario=scenario)

    def as_sentence(self):
        return "{op} {count} of us are the same.".format(
            op=english_operator_helper(self.claimed_relation),
            count=self.claimed_count,
        )


class Puzzle:
    def __init__(self, character_names_and_statements: {str: [Statement]}, allow_monks=True):
        self.is_solved = False
        self.scenarios = []
        self.character_names = []
        self.character_statements = {}

        for character_name, statements in character_names_and_statements.items():
            if not isinstance(statements, list):
                statements = [statements]
            self.character_names.append(character_name)
            self.character_statements[character_name] = statements

        self.max_num_monks = self._calculate_max_num_monks(allow_monks=allow_monks)

    @property
    def num_characters(self):
        return len(self.character_names)

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
        result, reason = scenario.check_consistency()
        if should_print:
            if result:
                print('+++++ \t{}'.format(scenario))
            else:
                if DEBUG is True:
                    print('----- \t{} \t ---> {}'.format(scenario, reason))

    def generate_and_check_scenarios(self, should_print=DEBUG):
        if len(self.scenarios) == 0:
            self._generate_scenarios()
        for scenario in self.scenarios:
            self.check_scenario(scenario=scenario, should_print=should_print)
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
            self.generate_and_check_scenarios()
        return len(self.get_consistent_scenario_set())

    def is_valid_puzzle(self):
        return (
            (CHARACTER_COUNT_BOUND[0] <= self.num_characters <= CHARACTER_COUNT_BOUND[1])
            and (SOLUTION_COUNT_BOUND[0] <= self.get_solution_count() <= SOLUTION_COUNT_BOUND[1])
        )

    def get_puzzle_score(self):
        multiplier = MULTIPLIERS[self.num_characters]

    def __str__(self):
        return self.character_names

