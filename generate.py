from package.puzzle_generator import *


def main():
    # print("Good ones")
    # p1 = Puzzle({
    #     'A': IfConnective(IsOfType('B', Knave), IsOfType('A', Knight)),
    #     'B': IfConnective(IsOfType('')),
    #     'C': [],
    #     'D': [],
    # })
    # p1.generate_and_check_scenarios(should_print=True)
    # print(p1.get_solution_count(), p1.get_total_possibilities())
    # print("---------------")

    gen = PuzzleGenerator(['A', 'B', 'C'], [IsSameAs, CountOfType, IsOfType, Honesty])
    gen.generate_puzzles(to_file=False)


if __name__ == '__main__':
    main()

