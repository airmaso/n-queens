import argparse

parser = argparse.ArgumentParser(
    prog="n_queens",
    description="optimized n-queens solver using mrv+lcv heuristics"
)

# board dimension and the number of queens
parser.add_argument(
    "-n",
    "--n",
    type=int,
    required=True,
    help="the number of queens"
)

# all flag (i.e., find all possible solutions)
parser.add_argument(
    "-a",
    "--all",
    help="whether to find all possible solutions",
    action="store_true"
)
