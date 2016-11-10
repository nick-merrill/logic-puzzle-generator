from package.puzzle_generator import *


def main():
    p1 = Puzzle({
        'A': [DisjunctiveStatement(AllTheSame(), AllDifferent()), Honesty('B', 'C', operator.gt)],
        'B': DisjunctiveStatement(AllTheSame(), CountOfType(Monk, 0, operator.eq)),
        'C': DisjunctiveStatement(AllTheSame(), CountOfType(Monk, 1, operator.eq)),
    })
    print(p1.get_character_statements_as_string())
    print(p1.get_solution_count(), 'possible solutions exist')
    p1.generate_and_check_scenarios(should_print=True)
    print("---------------")


if __name__ == '__main__':
    main()
