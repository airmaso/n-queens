import time
from dataclasses import dataclass, field


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


def backtrack(nq: NQueens, find_all: bool = False) -> list[int]:
    if nq.complete():
        return [nq.assignments.copy()]
    
    solutions: list[int] = []

    col = mrv(nq)
    if col is None:
        return solutions
    
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
                result = backtrack(nq, find_all=find_all)
                solutions.extend(result)

                if solutions and not find_all:
                    nq.assignments[col] = -1
                    restore(nq, diff)
                    return solutions

            # assignment didn't reach success case or finding all solution, choose different row
            nq.assignments[col] = -1
            restore(nq, diff)
        else:
            nq.backtracks += 1

    return solutions


@dataclass
class NQueensSolve:
    n:          int
    elapsed:    float  # units=ms
    solutions:  list[list[int]]
    explored:   int
    backtracks: int


def solve(nq: NQueens, find_all: bool = False) -> NQueensSolve:
    start = time.perf_counter()
    solns = backtrack(nq, find_all=find_all)
    end = time.perf_counter()

    return NQueensSolve(
        n=nq.n,
        elapsed=(end - start) * 1000,
        solutions=solns,
        explored=nq.explored,
        backtracks=nq.backtracks
    )
