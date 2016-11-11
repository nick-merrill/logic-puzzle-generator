from package.puzzle_generator import *


def main():
    Puzzle({
        'A': [
            DisjunctiveStatement(AllTheSame(), AllDifferent()),
            Honesty('B', 'C', operator.gt),
        ],
        'B': DisjunctiveStatement(AllTheSame(), CountOfType(Monk, 0, operator.eq)),
        'C': DisjunctiveStatement(AllTheSame(), CountOfType(Monk, 1, operator.eq)),
    }).print_puzzle_with_solutions()

    Puzzle({
        'A': [
            DisjunctiveStatement(
                ConjunctiveStatement(IsOfType('B', Monk), IsOfType('C', Knave)),
                ConjunctiveStatement(IsOfType('B', Knave), IsOfType('C', Monk)),
            ),
            Honesty('C', 'D', operator.gt),
        ],
        'B': [
            DisjunctiveStatement(
                ConjunctiveStatement(IsOfType('C', Monk), IsOfType('D', Knave)),
                ConjunctiveStatement(IsOfType('C', Knave), IsOfType('D', Monk)),
            ),
            DisjunctiveStatement(
                AllTheSame(),
                CountOfType(Knight, 1, operator.ge),
            )
        ],
        'C': DisjunctiveStatement(
            ConjunctiveStatement(IsOfType('D', Monk), IsOfType('A', Knave)),
            ConjunctiveStatement(IsOfType('D', Knave), IsOfType('A', Monk)),
        ),
        'D': DisjunctiveStatement(
            ConjunctiveStatement(IsOfType('A', Monk), IsOfType('B', Knave)),
            ConjunctiveStatement(IsOfType('A', Knave), IsOfType('B', Monk)),
        ),
    }).print_puzzle_with_solutions()


if __name__ == '__main__':
    main()
