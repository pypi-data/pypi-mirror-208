import os
from typing import Any, Iterable, Mapping, Sequence

from tabulate import tabulate


def griddy(
    data: Mapping[str, Iterable[Any]] | Iterable[Iterable[Any]],
    headers: str | dict[str, str] | Sequence[str] = (),
    shrink_to_terminal: bool = True,
    margin: int = 10,
    table_format: str = "rounded_grid",
    disable_numparse: bool = True,
) -> str:
    """Convert `data` into a formatted string grid representation.

    #### :params:

    * `headers`: Can either be an explicit list of column names, `"keys"`, or `"firstrow"`.
    If not given, the grid will have no headers.

    * `shrink_to_terminal`: When `True`, `griddy` will limit column widths so that the total width of the output will fit within the terminal.

    * `margin`: When shrinking to the terminal, `griddy` will try to maximize the output width such that `terminal_width - margin < output_width < terminal_width`.
    The larger this value, the larger the acceptable output width and, likely, the faster this function will return.
    Note: `griddy` will, internally, increase the margin when necessary to avoid getting stuck in an infinite loop.


    * `table_format`: The grid asthetic. See the `tabulate` package for a full list of options.

    * `disable_numparse`: Turn off treating and aligning numbers differently from non-numbers.

    """
    output = tabulate(
        data,
        headers=headers,
        disable_numparse=disable_numparse,
        tablefmt=table_format,
    )
    if not shrink_to_terminal:
        return output

    grid = lambda w: tabulate(
        data,
        headers=headers,
        disable_numparse=True,
        tablefmt=table_format,
        maxcolwidths=w,
    )

    terminal_width = os.get_terminal_size().columns
    max_col_width = terminal_width
    current_width = output.find("\n")
    if current_width < terminal_width:
        return output

    previous_col_width = max_col_width
    acceptable_width = terminal_width - margin
    while max_col_width > 1:
        if current_width >= terminal_width:
            previous_col_width = max_col_width
            max_col_width = int(max_col_width * 0.5)
        elif current_width < terminal_width:
            # Without lowering acceptable width, this condition will cause an infinite loop
            if max_col_width == previous_col_width - 1:
                acceptable_width -= margin
            max_col_width = int(
                max_col_width + (0.5 * (previous_col_width - max_col_width))
            )
        # Check if output width is in the acceptable range
        output = grid(max_col_width)
        current_width = output.find("\n")
        if acceptable_width < current_width < terminal_width:
            return output
    raise RuntimeError("Could not resize grid to fit within the terminal :/.")
