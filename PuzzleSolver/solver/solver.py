from package.puzzle_generator import *


def main():
    # p = Puzzle({
    #     'A': IfConnective(
    #         Biconditional(IsSameAs('C', 'D'), IsOfType('B', Monk)),
    #         Biconditional(Honesty('C', 'D', operator.gt), CountOfType(Knave, 2, operator.lt)),
    #     ),
    #     'B': IfConnective(
    #         Biconditional(IsSameAs('A', 'C'), IsSameAs('A', 'D')),
    #         Not(Biconditional(IsSameAs('A', 'D'), IsSameAs('A', 'B'))),
    #     ),
    #     'C': Biconditional(IsOfType('A', Knave), Honesty('C', 'D', operator.gt)),
    #     'D': DisjunctiveStatement(
    #         CountOfType(Knight, 2, operator.eq),
    #         CountOfType(Knight, 4, operator.eq)
    #     ),
    # })

    p = Puzzle({
        'D': DisjunctiveStatement(
            CountOfType(Knight, 2, operator.eq),
            CountOfType(Knight, 4, operator.eq)
        ),
    })

    p.solve(save_work_to_csv='test.csv')

    p.print_puzzle_with_solutions()


















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
