from package.puzzle_generator import *


def main():
    p1 = Puzzle({
        'A': [
            Biconditional(
                DisjunctiveStatement(  # uncertain
                    IsOfType('B', Knight),
                    IsOfType('C', Knight),
                    IsOfType('B', Monk),
                    IsOfType('C', Monk),
                ),
                IsOfType('E', Knave),
            ),
            IsOfType('A', Monk),
        ],
        'B': [
            CountOfTypes(Knight, Knave, operator.eq),
            IsSameAs('A', 'B'),
        ],
        'C': [
            Biconditional(
                IsOfType('C', Monk),
                IsSameAs('B', 'D'),
            ),
            ConjunctiveStatement(
                IsOfType('A', Knight),
                IsOfType('E', Knight),
            )
        ],
        'D': [
            IsOfType('D', Monk),
            IfConnective(
                Not(IsOfType('A', Monk)),
                IsOfType('B', Knight),
            ),
        ],
        'E': IfConnective(
            IsOfType('D', Knave),
            CountOfType(Monk, 2, operator.eq),
        ),
    })

    a = AllTheSame()
    b = Honesty('A', 'E', operator.gt)
    c = IsSameAs('C', 'A')
    p2 = Puzzle({
        'A': a,
        'B': b,
        'C': c,
        'D': DisjunctiveStatement(
            ConjunctiveStatement(a, b),
            ConjunctiveStatement(a, c),
            ConjunctiveStatement(b, c),
        ),
        'E': IsOfType('E', Knave),
    })

    p4 = Puzzle({
        'A': [
            CountOfType(Knight, 2, operator.le),
            CountOfType(Knave, 2, operator.lt),
        ],
        'B': [
            Honesty('B', 'A', operator.eq),
            CountOfType(Knave, 1, operator.ge),
        ],
        'C': [
            IsOfType('B', Monk),
            DisjunctiveStatement(
                IsOfType('D', Monk),
                IsOfType('E', Monk),
            ),
        ],
        'D': Biconditional(
            IsOfType('D', Monk),
            IsOfType('E', Knave),
        ),
        'E': Biconditional(
            IsOfType('E', Monk),
            IsOfType('A', Knight),
        ),
    })

    p5 = Puzzle({
        'A': [
            CountOfType(Knight, 3, operator.eq),
            IsOfType('B', Knight),
        ],
        'B': [
            CountOfType(Monk, 1, operator.ge),
            Not(IsOfType('A', Knight)),
        ],
        'C': [
            CountOfType(Knave, 0, operator.eq),
            CountOfType(Monk, 2, operator.ge),
        ],
        'D': [
            ExclusiveOrConnective(
                IsOfType('D', Knight),
                IsOfType('B', Monk),
            ),
            Honesty('B', 'D', operator.lt),
        ],
        'E': CountOfType(Knave, 1, operator.eq),
        'F': CountOfType(Knight, 2, operator.le),  # uncertain
    })


    def remainder_by_2_equals(a, b):
        return operator.mod(a, 2) == b


    p6 = Puzzle({
        'A': ConjunctiveStatement(
            IsOfType('B', Knight),
            IsOfType('C', Knight),
        ),
        'B': [
            CountOfType(Knight, 0, remainder_by_2_equals),
            IsOfType('A', Knave),
        ],
        'C': [
            Honesty('C', 'A', operator.gt),
            Honesty('B', 'A', operator.gt),
        ],
    })

    p8 = Puzzle({
        'Karen': [
            IfConnective(
                IsOfType('Thomas', Knave),
                Honesty('Karen', 'Perry', operator.gt),
            ),
            Not(IsSameAs('Perry', 'Thomas')),
        ],
        'Perry': [
            IfConnective(
                CountOfType(Monk, 1, operator.ge),
                CountOfType(Knight, 1, remainder_by_2_equals),
            ),
            CountOfTypes(Knave, Knight, operator.gt),
        ],
        'Thomas': IfConnective(
            CountOfType(Knave, 0, remainder_by_2_equals),
            Not(IsOfType('Thomas', Knave)),
        ),
    })

    c1 = IsSameAs('A', 'E')
    p9 = Puzzle({
        'A': [
            Biconditional(
                IsOfType('A', Monk),
                CountOfType(Monk, 0, remainder_by_2_equals),
            ),
        ],
        'B': [
            Biconditional(
                IsOfType('A', Knight),
                CountOfType(Knight, 0, remainder_by_2_equals),
            ),
            Honesty('C', 'A', operator.gt),
        ],
        'C': [
            c1,
            Honesty('A', 'B', operator.gt),
        ],
        'D': [
            c1,
            IfConnective(
                IsOfType('E', Knave),
                IsOfType('A', Knave),
            ),
        ],
        'E': [
            Biconditional(
                IsOfType('B', Knave),
                CountOfType(Knave, 0, remainder_by_2_equals),
            ),
            IfConnective(
                IsOfType('A', Knight),
                IsOfType('D', Monk),
            ),
        ],
    })

    p13 = Puzzle({
        'A': Biconditional(
            Honesty('A', 'D', operator.gt),
            Honesty('D', 'C', operator.gt),
        ),
        'B': IsOfType('D', Knight),
        'C': IfConnective(
            Honesty('A', 'C', operator.gt),
            CountOfType(Knave, 1, remainder_by_2_equals)
        ),
        'D': ConjunctiveStatement(
            Not(IsSameAs('D', 'B')),
            Not(IsOfType('B', Monk)),
        ),
    })

    p14 = Puzzle({
        'Ned': CountOfType(Knight, 0, remainder_by_2_equals),
        'Chandler': Honesty('Zoe', 'Chandler', operator.ge),
        'Zoe': CountOfType(Knight, 1, remainder_by_2_equals),
        'Ewa': Honesty('Ewa', 'Zoe', operator.gt),
    })

    p18 = Puzzle({
        'A': CountOfType(Monk, 0, operator.eq),
        'B': [
            ConjunctiveStatement(
                IfConnective(
                    IsOfType('B', Knight),
                    CountOfType(Knight, 1, operator.eq),
                ),
                IfConnective(
                    IsOfType('B', Monk),
                    CountOfType(Monk, 1, operator.eq),
                ),
                IfConnective(
                    IsOfType('B', Knave),
                    CountOfType(Knave, 1, operator.eq),
                ),
            ),
            Not(IsOfType('D', Monk)),
        ],
        'C': CountOfType(Knight, 0, operator.eq),
        'D': DisjunctiveStatement(
            IsOfType('A', Monk),
            IsOfType('D', Knave),
        )
    })

    p19 = Puzzle({
        'A': [
            Honesty('C', 'B', operator.gt),
            IfConnective(
                Honesty('B', 'A', operator.gt),
                IsOfType('B', Monk),
            ),
            Honesty('A', 'C', operator.gt),
        ],
        'B': [
            Honesty('B', 'A', operator.gt),
            Honesty('A', 'C', operator.gt),
            Not(IsOfType('C', Knave)),
        ],
        'C': [
            Honesty('A', 'B', operator.gt),
            Not(Honesty('B', 'A', operator.gt)),
        ],
    })

    p20 = Puzzle({
        'A': [
            CountOfType(Knave, 2, operator.eq),
            Not(IsOfType('B', Knave)),
        ],
        'B': [
            CountOfType(Knight, 2, operator.eq),
        ],
        'C': [
            Honesty('B', 'A', operator.gt),
            IsOfType('A', Knight),
        ]
    })

    p22 = Puzzle({
        'Deb': IfConnective(
            IsOfType('Deb', Knight),
            CountOfType(Knave, 1, operator.eq),  # uncertain "exactly"?
        ),
        'Jeb': IfConnective(
            Not(IsOfType('Jeb', Monk)),
            IsOfType('Bob', Monk)
        ),
        'Rob': IfConnective(
            IsOfType('Rob', Monk),
            CountOfType(Knave, 3, operator.eq)
        ),
        'Bob': [
            IfConnective(
                IsOfType('Bob', Knave),
                IsSameAs('Deb', 'Rob')
            ),
            CountOfType(Knave, 3, operator.eq),  # uncertain "exactly"?
        ],
    })

    p23 = Puzzle({
        'A': [
            Biconditional(
                IsOfType('B', Knight),
                IsOfType('C', Knight)
            ),
            IsOfType('C', Knave),
        ],
        'B': [
            Biconditional(
                IsOfType('A', Knight),
                IsOfType('C', Monk)
            ),
        ],
        'C': [
            Biconditional(
                IsOfType('A', Knave),
                IsOfType('D', Knight),
            ),
            IsOfType('B', Monk),
        ],
        'D': [
            Biconditional(
                IsOfType('A', Knave),
                IsOfType('B', Knave),
            ),
        ],
    })

    p24 = Puzzle({
        'A': [
            Honesty('B', 'C', operator.gt),
            IsOfType('C', Knave),
        ],
        'B': [
            Honesty('C', 'A', operator.gt),
            SumOfTypes((Knave, Knight), 2, operator.eq),
        ],
        'C': [
            IsSameAs('C', 'B'),
        ],
    })

    p25 = Puzzle({
        'A': [
            IsOfType('A', Knight),
            CountOfType(Knave, 0, remainder_by_2_equals),
        ],
        'B': [
            IsOfType('C', Knight),
            CountOfType(Monk, 0, operator.eq),
        ],
        'C': [
            CountOfType(Knight, 1, operator.eq),
            Biconditional(
                IsOfType('C', Knight),
                IsOfType('A', Knave)
            ),
        ],
    })

    p26 = Puzzle({
        'Antoine': [
            Biconditional(
                IsOfType('Bernardo', Knight),
                IsOfType('Antoine', Knave),
            ),
            CountOfType(Monk, 1, operator.ge),
        ],
        'Bernardo': CountOfType(Knight, 1, remainder_by_2_equals),
        'Campbell': ConjunctiveStatement(
            Not(IsOfType('Campbell', Monk)),
            IsOfType('Antoine', Monk),
        )
    })

    b1 = Not(IsSameAs('E', 'B'))
    e = IsOfType('A', Knight)
    p27 = Puzzle({
        'A': [
            Biconditional(
                Not(b1),
                Honesty('D', 'A', operator.eq),
            ),
            CountOfType(Monk, 0, operator.eq),
        ],
        'B': [
            b1,
            CountOfType(Knave, 2, operator.ge),
        ],
        'C': [
            DisjunctiveStatement(
                IsOfType('D', Knight),
                CountOfType(Monk, 0, operator.eq),
            ),
            Not(e),
        ],
        'D': [
            IfConnective(
                Not(IsSameAs('D', 'B')),
                IsOfType('E', Knave)
            ),
        ],
        'E': [
            e,
        ],
    })

    p27.print_puzzle_with_solutions()

    # p.print_puzzle_statistics()


if __name__ == '__main__':
    main()
