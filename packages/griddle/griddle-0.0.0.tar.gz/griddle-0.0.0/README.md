# griddle

Turn tabular data into a printable grid. <br>
Wraps the [tabulate](https://pypi.org/project/tabulate/) to streamline usage as well as
automatically reduce column widths to fit the grid to the current terminal width.

## Installation

Install with:

<pre>
pip install griddle
</pre>



## Usage

<pre>
>>> from griddle import griddy
>>> data = [{"a": i, "b": i+1, "c": i+2} for i in range(10)]
>>> print(griddy(data, "keys"))
╭─────┬─────┬─────╮
│ a   │ b   │ c   │
├─────┼─────┼─────┤
│ 0   │ 1   │ 2   │
├─────┼─────┼─────┤
│ 1   │ 2   │ 3   │
├─────┼─────┼─────┤
│ 2   │ 3   │ 4   │
├─────┼─────┼─────┤
│ 3   │ 4   │ 5   │
├─────┼─────┼─────┤
│ 4   │ 5   │ 6   │
├─────┼─────┼─────┤
│ 5   │ 6   │ 7   │
├─────┼─────┼─────┤
│ 6   │ 7   │ 8   │
├─────┼─────┼─────┤
│ 7   │ 8   │ 9   │
├─────┼─────┼─────┤
│ 8   │ 9   │ 10  │
├─────┼─────┼─────┤
│ 9   │ 10  │ 11  │
╰─────┴─────┴─────╯
</pre>
