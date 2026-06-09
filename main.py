"""
Trying to recall information from CSC384H1: AI @ University of Toronto.
06-08-2026 @ 1:36 PM CT
"""

import threading
import time
from dataclasses import dataclass, field
import matplotlib.pyplot as plot


@dataclass
class NQueens:
    """
    N-Queens state wrapper
    """
    n:           int                                            # number of queens (and the board dimension)
    assignments: list[int]       = field(default_factory=list)  # assignment[col]: the current row chosen for col
    domains:     list[set[int]]  = field(default_factory=list)  # domains[col]: possible rows to choose from
    explored:    int             = 0                            # number of (col, row) pairs checked
    backtracks:  int             = 0                            # number of recursive calls

    def __post_init__(self):
        self.assignments = [-1] * self.n                            # each col is unassigned initially
        self.domains = [set(range(self.n)) for _ in range(self.n)]  # each row is a possible choice initially

    def complete(self) -> bool:
        return all(self.assignments[c] != -1 for c in range(self.n))  # all cols are assigned


def consistent(assignments: list[int], col: int, row: int) -> bool:
    for placed_col, placed_row in enumerate(assignments):
        if placed_row == -1:                                 continue      # not placed; okay
        elif placed_row == row:                              return False  # on same row
        elif abs(placed_row - row) == abs(placed_col - col): return False  # on same diagonal
    
    return True


def mrv(nq: NQueens) -> int | None:
    """
    MRV heuristic (chooses a column)
    
    Chooses the variable (i.e., column) with the minimum remaining
    values (i.e., the least rows)

    Breaks ties by choosing the leftmost column
    """
    return min([(len(nq.domains[c]), c) for c in range(nq.n) if nq.assignments[c] == -1])[1]


def lcv(nq: NQueens, col: int) -> list[int]:
    """
    LCV heuristic (chooses a row for a column)
    
    Chooses the row for col that constrains other columns the least.
    (i.e., maximizes the number of rows to choose from across all unassigned columns)
    """
    def constraint_impacts(row: int) -> int:
        impacts = 0
        for other_col in range(nq.n):
            if nq.assignments[other_col] != -1 or other_col == col:
                continue

            for other_row in nq.domains[other_col]:
                if (
                    other_row == row or
                    abs(other_row - row) == abs(other_col - col)
                ):
                    impacts += 1

        return impacts
    
    # orders by lowest impacts
    return sorted(nq.domains[col], key=constraint_impacts)


def fc(nq: NQueens, col: int, row: int):
    removed: dict[int, set[int]] = dict()

    for other_col in range(nq.n):
        if nq.assignments[other_col] != -1 or other_col == col:
            continue

        to_remove: set[int] = {
            other_row
            for other_row in nq.domains[other_col]
            if other_row == row or abs(other_row - row) == abs(other_col - col)
        }

        if to_remove:
            nq.domains[other_col] -= to_remove
            removed[other_col] = to_remove

    return removed


def restore(nq: NQueens, diff: dict[int, set[int]]):
    """
    Undos a forward check by unioning back the lost rows from
    the current assignment being undone
    """
    for other_col, rows in diff.items():
        nq.domains[other_col] |= rows


def backtrack(nq: NQueens) -> list[int]:
    if nq.complete():
        return nq.assignments.copy()
    
    solution: list[int] = []

    col = mrv(nq)
    if col is None:
        return solution
    
    for row in lcv(nq, col):
        nq.explored += 1

        if consistent(nq.assignments, col, row):
            nq.assignments[col] = row  # choose this row for col
            diff = fc(nq, col, row)    # forward check on the selected row

            # recurse only if no other domain went empty
            if all(
                len(nq.domains[c]) > 0 or nq.assignments[c] != -1
                for c in range(nq.n)
            ):
                result = backtrack(nq)
                solution.extend(result)

                if solution:
                    return solution


            # assignment didn't reach success case, choose different row
            nq.assignments[col] = -1
            restore(nq, diff)
        else:
            nq.backtracks += 1

    return solution    


@dataclass
class SolveResult:
    n: int
    elapsed: float
    solution: list[int]
    explored: int
    backtracks: int


data: list[SolveResult] = []  # thread-safe
def solve(nq: NQueens):
    start = time.perf_counter()
    soln = backtrack(nq)
    end = time.perf_counter()

    data.append(SolveResult(
        n=nq.n,
        elapsed=(end - start),
        solution=soln,
        explored=nq.explored,
        backtracks=nq.backtracks
    ))

    # print(nq.n, soln)


@dataclass
class FigureData:
    title:  str
    xlabel: str
    ylabel: str
    xdata:  list[int]
    ydata:  list[int | float]
    color:  str
    marker: str
    label:  str


if __name__ == "__main__":
    n = 88
    threads = [
        threading.Thread(target=solve, args=(NQueens(n),))
        for n in range(1, n + 1)
    ]

    for t in threads: t.start()
    for t in threads: t.join()

    data.sort(key=lambda sr: sr.n)
    ns = [sr.n for sr in data]

    figures: list[FigureData] = [
        FigureData(
            title="n vs. time",
            xlabel="n",
            ylabel="time (s)",
            xdata=ns,
            ydata=[sr.elapsed for sr in data],
            color="#7F956A",
            marker="o",
            label="n_elapsed"
        ),
        FigureData(
            title="n vs. explored",
            xlabel="n",
            ylabel="explored",
            xdata=ns,
            ydata=[sr.explored for sr in data],
            color="#495940",
            marker="o",
            label="n_explored"
        ),
        FigureData(
            title="n vs. backtracks",
            xlabel="n",
            ylabel="backtracks",
            xdata=ns,
            ydata=[sr.backtracks for sr in data],
            color="#000000",
            marker="o",
            label="n_backtracks"
        ),
    ]
    
    for idx, figure in enumerate(figures, start=1):
        plot.figure(idx)
        plot.grid(visible=True)

        plot.title(figure.title)
        plot.xlabel(figure.xlabel)
        plot.ylabel(figure.ylabel)

        plt = plot.plot(
            figure.xdata, figure.ydata,
            color=figure.color,
            # marker=figure.marker
        )

    plot.show()
