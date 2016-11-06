import abc
import itertools

DEBUG = True


class CharacterIdentifierError(Exception):
    pass


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


POSSIBLE_CHARACTERS = [Knight, Knave, Monk]


class Scenario:
    def __init__(self, puzzle, character_types: {str: type}):
        self.puzzle = puzzle
        self.character_types = character_types

    def check_correctness(self):
        """
        If it makes sense that the character would speak this phrase, returns True; otherwise False.
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

            if statement.evaluate_correctness(speaking_character_type=speaking_character_type, scenario=self) is False:
                return dict(result=False, reason="{} should not have said {}.".format(character_name, statement))
        return True

    def __str__(self):
        names_and_identities = []
        for name, character_type in self.character_types.items():
            names_and_identities.append("{}[{}]".format(name, character_type.short_identifier))
        return " \t ".join(names_and_identities)


class Statement:
    def evaluate_correctness(self, speaking_character_type, scenario: Scenario):
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
        return '"{}"'.format(self.as_sentence())

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
        if DEBUG:
            print("Evaluating truth for", self)
        try:
            return isinstance(scenario.character_types[self.target_name], self.claimed_character_type)
        except KeyError:
            raise CharacterIdentifierError("Cannot find character '{}'.".format(self.target_name))

    def as_sentence(self):
        return "{} is a {}.".format(self.target_name, self.claimed_character_type.title)


class Puzzle:
    def __init__(self, character_names_and_statements: {str: [Statement]}):
        self.scenarios = []
        self.character_names = []
        self.character_statements = {}
        for character_name, statements in character_names_and_statements.items():
            self.character_names.append(character_name)
            self.character_statements[character_name] = statements

        self.max_num_monks = self._calculate_max_num_monks()

    @property
    def num_characters(self):
        return len(self.character_names)

    def _calculate_max_num_monks(self):
        """
        Determines the maximum number of Monks allowed in a puzzle of this size.
        (Less than half the number of characters.)
        """
        max_num_monks = self.num_characters // 2
        if max_num_monks == self.num_characters / 2:
            max_num_monks -= 1
        return max_num_monks

    def _generate_scenario(self, identity_ordering: [type]):
        character_types = {}
        i = 0
        for name in self.character_names:
            character_types[name] = identity_ordering[i]
            i += 1
        return Scenario(puzzle=self, character_types=character_types)

    def _generate_scenarios(self):
        self.scenarios = []  # Clears all scenarios first.
        for identity_ordering in itertools.combinations_with_replacement(POSSIBLE_CHARACTERS, self.num_characters):
            scenario = self._generate_scenario(identity_ordering)
            self.scenarios.append(scenario)

    def generate_and_check_scenarios(self):
        self._generate_scenarios()
        for scenario in self.scenarios:
            if scenario.check_correctness():
                print('+++++ \t' + str(scenario))
            else:
                if DEBUG is True:
                    print('----- \t' + str(scenario))

    def __str__(self):
        return self.character_names

