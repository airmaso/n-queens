from utils.solver import NQueens, solve


if __name__ == "__main__":
    n_queens = NQueens(n=4)
    solve_result = solve(n_queens, find_all=False)

    print(solve_result)
