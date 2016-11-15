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

    p=Puzzle({
'A': [
IfConnective(
Not(Biconditional(
IsOfType('D', Monk),
IsOfType('B', Knight)
)),
Biconditional(
IsOfType('D', Knight),
CountOfType(Monk, 2, operator.le)
)
),
],
'B': [
DisjunctiveStatement(
Biconditional(
Honesty('B', 'C', operator.le),
IsOfType('B', Monk)
),
Not(Biconditional(
CountOfType(Knight, 2, operator.le),
IsSameAs('A', 'D')
))
),
],
'C': [
DisjunctiveStatement(
ConjunctiveStatement(
IsOfType('C', Knave),
IsSameAs('A', 'B')
),
ConjunctiveStatement(
IsSameAs('C', 'D'),
IsOfType('A', Knight)
)
),
],
'D': [
ConjunctiveStatement(
DisjunctiveStatement(
IsSameAs('A', 'C'),
Not(Honesty('C', 'D', operator.le))
),
DisjunctiveStatement(
IsOfType('D', Knave),
Not(Honesty('A', 'B', operator.le))
)
),
],
})

    p=Puzzle({
        'A': [
            IfConnective(
                Not(Biconditional(
                    IsOfType('A', Knight),
                    IsOfType('C', Monk)
                )),
                Biconditional(
                    CountOfType(Monk, 2, operator.le),
                    Honesty('A', 'B', operator.le)
                )
            ),
        ],
        'B': [
            DisjunctiveStatement(
                Biconditional(
                    IsOfType('D', Monk),
                    IsOfType('C', Knight)
                ),
                Not(Biconditional(
                    Honesty('C', 'D', operator.le),
                    Honesty('A', 'C', operator.le)
                ))
            ),
        ],
        'C': [
            DisjunctiveStatement(
                ConjunctiveStatement(
                    IsOfType('A', Monk),
                    Honesty('B', 'D', operator.le)
                ),
                ConjunctiveStatement(
                    IsOfType('C', Knave),
                    CountOfType(Knight, 2, operator.le)
                )
            ),
        ],
        'D': [
            ConjunctiveStatement(
                DisjunctiveStatement(
                    IsSameAs('B', 'D'),
                    Not(IsSameAs('A', 'B'))
                ),
                DisjunctiveStatement(
                    IsOfType('D', Knave),
                    Not(IsSameAs('A', 'D'))
                )
            ),
        ],
    })

    p = Puzzle({
        'Betty': [
            IfConnective(
                Not(Biconditional(
                    Honesty('Bob', 'Bill', operator.le),
                    Honesty('Bob', 'Brittany', operator.le)
                )),
                Biconditional(
                    IsSameAs('Bob', 'Brittany'),
                    CountOfType(Knave, 2, operator.le)
                )
            ),
        ],
        'Bob': [
            IfConnective(
                Biconditional(
                    Honesty('Bill', 'Betty', operator.le),
                    IsSameAs('Betty', 'Bill')
                ),
                Not(Biconditional(
                    Honesty('Bob', 'Betty', operator.le),
                    IsSameAs('Bob', 'Bill')
                ))
            ),
        ],
        'Brittany': [
            IfConnective(
                Not(Biconditional(
                    Honesty('Brittany', 'Bill', operator.le),
                    Honesty('Bill', 'Bob', operator.le)
                )),
                Biconditional(
                    IsSameAs('Betty', 'Bob'),
                    Honesty('Brittany', 'Betty', operator.le)
                )
            ),
        ],
        'Bill': [
            IfConnective(
                Biconditional(
                    IsSameAs('Betty', 'Brittany'),
                    Not(Honesty('Brittany', 'Bob', operator.le))
                ),
                Not(Biconditional(
                    CountOfType(Knight, 2, operator.le),
                    Not(Honesty('Bill', 'Brittany', operator.le))
                ))
            ),
        ],
    })

    p = Puzzle({
        'A': IfConnective(IsOfType('B', Knight), IsOfType('A', Knave)),
        'B': IfConnective(IsOfType('C', Knight), IsOfType('B', Knave)),
        'C': IfConnective(IsOfType('D', Knight), IsOfType('C', Knave)),
        'D': IfConnective(IsOfType('E', Knight), IsOfType('D', Knave)),
        'E': IsOfType('E', Knight),
    })

    # p.solve(save_work_to_csv='test.csv')
    p.solve()

    p.print_puzzle_with_solutions()
    # p.print_puzzle_statistics()


if __name__ == '__main__':
    main()
