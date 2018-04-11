# Logic Puzzle Generator

## Usage

### Solving

If we wanted to solve the following puzzle...

1. Alice says, "There are exactly 3 knaves."
2. Bob says, "There are exactly 2 knaves."
3. Carolina doesn't say anything.

...we would solve like so:

```python
p = Puzzle({
    'Alice': CountOfType(Knave, 3, operator.eq),
    'Barack': CountOfType(Knave, 2, operator.eq),
    'Carolina': [],
}, allow_monks=False)
p.solve()
solutions = p.get_consistent_scenario_set()
```

The `solutions` would then be:

```python
[
    {
        'Alice': Knave,
        'Barack': Knight,
        'Carolina': Knave,
    },
]
```

### Generating

Generate a puzzle like so:

```python
gen = PuzzleGenerator(['A', 'B', 'C', 'D'], [IsSameAs, CountOfType, Honesty])
gen.generate_puzzles(to_file=True)
```

