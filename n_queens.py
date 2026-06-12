import math

from rich import box
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.table import Table

from utils.parser import parser
from utils.solver import NQueens, solve, NQueensSolve


class NQueensTerminal:
    n_queens: NQueens
    find_all: bool

    def __init__(self, n_queens: NQueens, find_all: bool = False):
        self.n_queens = n_queens
        self.find_all = find_all

    def _browse_solutions(self, solutions: list[list[int]]):
        pass

    def _build_stat_table(self, result: NQueensSolve):
        stat_table = Table(box=box.ROUNDED, show_header=True, header_style="dim")

        # init table columns
        for header, style in [
            ("solutions", "cyan"),
            ("explored", "cyan"),
            ("backtracks", "cyan"),
            ("space explored", "cyan"),
            ("time", "cyan")
        ]:
            stat_table.add_column(header, style=style)

        # inject results into table
        stat_table.add_row(
            f"{len(result.solutions):,}",
            f"{result.explored:,}",
            f"{result.backtracks:,}",
            f"~{result.explored / math.factorial(self.n_queens.n) * 100:.2f}%",
            f"{result.elapsed:,.2f} ms"
        )

        return stat_table

    def run(self):
        with Progress(
            SpinnerColumn(spinner_name="bouncingBar", style="cyan", finished_text="thought for:"),
            TimeElapsedColumn(),
            transient=False
        ) as progress:
            task = progress.add_task("solve", total=1)
            result = solve(nq=self.n_queens, find_all=self.find_all)
            progress.update(task, completed=1)

        console = Console(width=88)

        # stat table
        stat_table = self._build_stat_table(result)
        console.print(stat_table)

        # solution browsing
        if len(result.solutions) > 0:
            self._browse_solutions(result.solutions)


if __name__ == "__main__":
    args = parser.parse_args()

    ui = NQueensTerminal(
        n_queens=NQueens(n=args.n),
        find_all=args.all
    )
    ui.run()
