from .puzzle_generator import *


def main():
    gen = PuzzleGenerator(['A', 'B', 'C', 'D'], [IsOfType, SamenessCount])
    gen.generate_puzzles()


if __name__ == '__main__':
    main()

