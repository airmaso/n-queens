import threading
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from utils.solver import NQueens, NQueensSolve, solve


class Benchmarker:
    existential_data: list[NQueensSolve]
    universal_data:   list[NQueensSolve]
    EXISTENTIAL_LIMIT = 60  # max existential n
    UNIVERSAL_LIMIT   = 15  # max universal n

    def __init__(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            existential_future = executor.submit(self._benchmark_existential)
            universal_future = executor.submit(self._benchmark_universal)
            self.existential_data = existential_future.result()
            self.universal_data = universal_future.result()

    def _benchmark(self, limit: int, find_all: bool) -> list[NQueensSolve]:
        data: list[NQueensSolve] = [None] * (limit + 1)

        def run_solver(n: int):
            data[n] = solve(NQueens(n=n), find_all=find_all)

        threads = [
            threading.Thread(target=run_solver, args=(queens,))
            for queens in range(1, limit + 1)
        ]

        for t in threads: t.start()
        for t in threads: t.join()

        return data

    def _benchmark_existential(self):
        """
        Benchmarks the solver on finding a single solution for a given n
        
        NOTE: we can input larger n for this benchmark as the code
        is simulating an existential (i.e., we just need to find one solution)
        as opposed to finding every possible one, which scales massively as
        n increases
        """
        return self._benchmark(limit=self.EXISTENTIAL_LIMIT, find_all=False)

    def _benchmark_universal(self):
        """
        Benchmarks the solver on finding all solutions
        """
        return self._benchmark(limit=self.UNIVERSAL_LIMIT, find_all=True)

    def get_existential_data(self) -> list[NQueensSolve]:
        return self.existential_data[1:]
    
    def get_universal_data(self) -> list[NQueensSolve]:
        return self.universal_data[1:]


@dataclass
class FigureData:
    title:  str
    xdata:  list[int]
    ydata:  list[NQueensSolve]
    color:  str = "#000000"
    xlabel: str = "n"
    ylabel: str = "time (ms)"


if __name__ == "__main__":
    benchmarker = Benchmarker()

    for idx, fdata in enumerate([
        FigureData(
            title="existential benchmark",
            xdata=list(range(1, benchmarker.EXISTENTIAL_LIMIT + 1)),
            ydata=[res.elapsed for res in benchmarker.get_existential_data()],
        ),
        FigureData(
            title="universal benchmark",
            xdata=list(range(1, benchmarker.UNIVERSAL_LIMIT + 1)),
            ydata=[res.elapsed / 1000 for res in benchmarker.get_universal_data()],
            ylabel="time (s)"
        )
    ]):
        subplot = plt.subplots()
        fig: Figure = subplot[0]
        ax:  Axes   = subplot[1]

        # plt.grid(visible=True)
        plt.title(fdata.title)
        ax.set_xlabel(fdata.xlabel)
        ax.set_ylabel(fdata.ylabel)

        ax.plot(fdata.xdata, fdata.ydata, color=fdata.color, marker="o", markersize=3)

        for x, y in zip(fdata.xdata, fdata.ydata):
            if idx == 1 or (x - 1) % 5 == 0:  # annotate every third data point
                ax.annotate(
                    f"({x}, {y:.4f})",
                    xy=(x, y),
                    xytext=(4, 4),
                    textcoords="offset points",
                    fontsize=6,
                    bbox=dict(
                        boxstyle="round,pad=0.3",
                        facecolor="white",
                        edgecolor="#4ECCFA",
                        alpha=0.8
                    )
                )

    plt.show()
