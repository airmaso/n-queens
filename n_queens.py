import math

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.measure import Measurement
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

from utils.parser import parser
from utils.solver import NQueens, solve, NQueensSolve
from utils.terminal import read_key, KEYS, render


class NQueensTerminal:
    n_queens: NQueens
    find_all: bool

    def __init__(self, n_queens: NQueens, find_all: bool = False):
        self.n_queens = n_queens
        self.find_all = find_all

    def _browse_solutions(self, solutions: list[list[int]]):
        index = 0
        total = len(solutions)
        n = len(solutions[0])

        dummy_table = Table(box=box.ROUNDED, show_lines=True, show_header=False)
        for _ in range(n): dummy_table.add_column(justify="center")
        dummy_table.add_row(*["Q"] * n)  # one row is enough to measure

        console = Console()
        optimal_width = Measurement.get(console, console.options, dummy_table).maximum
        # console = Console(width=max(22, n * 4 + 6))
        console = Console(width=optimal_width + 4)

        def create_panel(i: int) -> Panel:
            soln = solutions[i]
            n = len(soln)

            matrix = Table(box=box.ROUNDED, show_lines=True, show_header=False)
            for _ in range(n): matrix.add_column(justify="center")
            for r in range(n): matrix.add_row(*["Q" if soln[c] == r else "" for c in range(n)], style="magenta")

            footer = Text(justify="center")
            footer.append(f"[{KEYS.QUIT_KEYS[0]}] quit", style="cyan")

            return Panel(
                Align.center(Group(matrix, footer)),
                title=f"[cyan]solution {index + 1:,} / {total:,}[/cyan]",
                subtitle=f"queens: {soln}",
                box=box.MINIMAL
            )
        
        def create_render(i: int) -> int:
            panel = create_panel(i)

            with console.capture() as capture:
                console.print(panel)
            
            return capture.get()

        last_render = create_render(index)
        render(last_render)

        while True:
            key = read_key()

            if   key in KEYS.QUIT_KEYS:  break
            elif key in KEYS.LEFT_KEYS and total >= 2:  index = (index + 1) % total
            elif key in KEYS.RIGHT_KEYS and total >= 2: index = (index - 1) % total
            else:                        continue

            new_render = create_render(index)
            render(new_render, erase_lines=last_render.count("\n"))
            last_render = new_render

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
