#%%
from enum import Enum
import json
import math
import pag
import warnings
from typing import Iterable, cast
import numpy as np


def generate_attribution(m: int, n: int):
    if n < 0 or m < 0:
        raise ValueError("Sizes must be positive.")
    res = np.eye(n)
    for _ in range(m - 1):
        res = np.concatenate((res, np.eye(n)), axis=1)
    return res


class Problem:
    def __init__(self, 
                 objective: Iterable, 
                 knapsack: Iterable, 
                 b: Iterable, 
                 m: int, 
                 n: int) -> None:
        self.objective = np.array(objective)
        self.knapsack = np.array(knapsack)
        self.b = np.array(b)
        self.m = m 
        self.n = n
        self.attribution = generate_attribution(self.m, self.n)

    def get_all_problem_parameters(self):
        return self.objective, self.attribution, self.knapsack, self.b, self.m, self.n


def load_problem_from_json(filename: str = 'problem.json'):
    "Deprecated."
    warnings.warn("The code has been refactored to "\
                  "comply with another input standard.", DeprecationWarning)
    with open(filename, 'r') as file:
        problem = json.loads(file.read())
        objective = np.array(problem['objective'])
        attribution = np.array(problem['attribution'])[:, :-1]
        knapsack = np.array(problem['knapsack'])
        b = knapsack[:, -1]
        knapsack = knapsack[:, :-1]
        n = attribution.shape[0]
        m = knapsack.shape[0]

        return Problem(objective, knapsack, b, m, n)


def solve_relaxation(
    u: np.ndarray,
    objective: np.ndarray,
    attribution: np.ndarray,
    knapsack: np.ndarray,
    b: np.ndarray,
    m: int,
    n: int
) -> tuple[np.ndarray, float]:
    new_obj = u @ knapsack + objective

    restrictions = [np.where(row == 1)[0] for row in attribution]

    obj_reshaped = new_obj[restrictions]
    solution = np.zeros(m * n)

    for row, indices in zip(obj_reshaped, restrictions):
        idx = row.argmin()
        solution[indices[idx]] = 1
    
    return solution, cast(float, solution @ new_obj - u @ b)

class CheckResult(Enum):
    ViolatesAttribution = 0
    ViolatesKnapsack = 1
    SubOptimal = 2
    Optimal = 3

def check_optimality(
    solution: np.ndarray,
    value: float,
    objective: np.ndarray,
    attribution: np.ndarray,
    knapsack: np.ndarray,
    b: np.ndarray
) -> CheckResult:
    for row in attribution:
        if solution @ row != 1:
            return CheckResult.ViolatesAttribution
        
    for row, bi in zip(knapsack, b):
        if solution @ row > bi:
            return CheckResult.ViolatesKnapsack
        
    if math.isclose(objective @ solution, value):
        return CheckResult.Optimal

    return CheckResult.SubOptimal


def get_next_u(
    u: np.ndarray,
    solution: np.ndarray,
    lamda: float,
    z_bar: float,
    value: float,
    knapsack: np.ndarray,
    b: np.ndarray,
    verbose: bool = False
):
    subgradient = []
    for row, bi in zip(knapsack, b):
        subgradient.append(solution @ row - bi)
    subgradient = np.array(subgradient)
    if verbose: print(subgradient)

    step = lamda * (z_bar - value) / np.linalg.norm(subgradient)**2

    next_u = u + step * subgradient
    next_u = np.array([
        ui if ui > 0 else 0 for ui in next_u
    ])

    return next_u    


def solve_problem(
    problem: Problem,
    initial_u: np.ndarray,
    lamda: float,
    z_bar: float,
    max_iterations: int = 1000,
    max_iterations_without_improvement: int = 50,
    verbose: bool = False
):
    objective, attribution, knapsack, b, m, n = problem.get_all_problem_parameters()

    if verbose: print(m, n,'\n\n', objective, '\n\n', attribution, '\n\n', knapsack,'\n\n', b)

    u = initial_u
    solution = np.array([]) 
    value = math.nan
    previous_value = math.nan
    iterations_without_improvement = 0
    viable = False
    for _ in range(max_iterations):
        viable = False
        solution, value = solve_relaxation(
            u,
            objective,
            attribution,
            knapsack,
            b,
            m, n
        )

        if verbose: print(f'{solution=}\n{value=}')

        if value >= previous_value:
            iterations_without_improvement += 1

        if iterations_without_improvement > max_iterations_without_improvement:
            lamda /= 2
            iterations_without_improvement = 0

        verification = check_optimality(
            solution,
            value,
            objective,
            attribution,
            knapsack,
            b
        )

        if verification == CheckResult.Optimal:
            viable = True
            break
        if verification == CheckResult.SubOptimal:
            viable = True
            if value < previous_value:
                z_bar = value

        u = get_next_u(
            u,
            solution,
            lamda,
            z_bar,
            value,
            knapsack,
            b,
            verbose
        )
        if verbose: print(f'{u=}')

        previous_value = value

    return solution, value, viable

def generate_and_solve_solver_problem(problem: Problem):
    objective, attribution, knapsack, b, m, n = problem.get_all_problem_parameters()
    objective = objective.reshape((m, n))
    pag.atribuicao_generalizado(m, n, knapsack, objective, b)

#%%
if __name__ == '__main__':
    # problem = load_problem_from_json('atividade4/problem.json')
    m, n, knapsack, objective, b, solver_solution = pag.main()

    solver_solution = np.array(solver_solution)

    # our routine works with a flattened objective (costs) vector (i.e. not a matrix)
    objective = np.array(objective).flatten()

    # our routine demands a filled out matrix for the knapsack restrictions
    for j in range(m):
        for k in range(m):
            if k < j:
                knapsack[j] = [0]*n + knapsack[j]
            if k > j:
                knapsack[j] = knapsack[j] + [0]*n

    problem = Problem(objective, knapsack, b, m, n)
    solution, value, viable = solve_problem(
        problem,
        np.zeros(m),
        2,
        15,
        20,
        5
    )
    print(f'{solution=} {value=} {viable=}')
    print(f'Default solver solution: {solver_solution}\n' \
          f'Default solution value: {solver_solution @ objective}')
    # generate_and_solve_solver_problem(problem)
