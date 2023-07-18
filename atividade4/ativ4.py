#%%
from enum import Enum
import math
import pag
from typing import Iterable, cast
import numpy as np


def generate_attribution(m: int, n: int):
    """Given a problem size, generates the matrix of restrictions pertaining to the
    attribution part of the problem."""
    if n < 0 or m < 0:
        raise ValueError("Sizes must be positive.")
    res = np.eye(n)
    for _ in range(m - 1):
        res = np.concatenate((res, np.eye(n)), axis=1)
    return res


class Problem:
    "Just a convenient data structure for the GAP parameters."
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
    
    def __str__(self) -> str:
        problem_str = "Problem:\n"
        problem_str += f"Objective: {self.objective}\n"
        problem_str += f"Attribution:\n{self.attribution}\n"
        problem_str += f"Knapsack:\n{self.knapsack}\n"
        problem_str += f"b: {self.b}\n"
        problem_str += f"m: {self.m}\n"
        problem_str += f"n: {self.n}\n"
        return problem_str
    
    def __repr__(self) -> str:
        return str(self)

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

    # the line below will create a matrix of indices to reshape the `new_obj`
    # array back into a matrix, so we can extract the cost relative to each variable
    restrictions = [np.where(row == 1)[0] for row in attribution]

    obj_reshaped = new_obj[restrictions]
    solution = np.zeros(m * n)

    for row, indices in zip(obj_reshaped, restrictions):
        idx = row.argmin() # we're choosing index of the variable with lowest cost
        solution[indices[idx]] = 1 # now we're using the index to select the variable
    
    # `cast` is used only to satisfy the typechecker
    return solution, cast(float, solution @ new_obj - u @ b) 

class CheckResult(Enum):
    VIOLATES_ATTRIBUTION_RESTRICTIONS = 0
    VIOLATES_KNAPSACK_RESTRICTIONS = 1
    SUBOPTIMAL_SOLUTION = 2
    OPTIMAL_SOLUTION = 3

def check_optimality(
    solution: np.ndarray,
    value: float,
    objective: np.ndarray,
    attribution: np.ndarray,
    knapsack: np.ndarray,
    b: np.ndarray
) -> CheckResult:
    for row in attribution:
        if not math.isclose(solution @ row, 1.):
            return CheckResult.VIOLATES_ATTRIBUTION_RESTRICTIONS
        
    for row, bi in zip(knapsack, b):
        if solution @ row > bi:
            return CheckResult.VIOLATES_KNAPSACK_RESTRICTIONS
        
    if math.isclose(objective @ solution, value):
        return CheckResult.OPTIMAL_SOLUTION

    return CheckResult.SUBOPTIMAL_SOLUTION


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

        if value >= previous_value: # wrong?
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

        if verification == CheckResult.OPTIMAL_SOLUTION:
            viable = True
            break
        if verification == CheckResult.SUBOPTIMAL_SOLUTION:
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


#%%
if __name__ == '__main__':
    m, n, knapsack, b, objective, solver_solution = pag.main(6, 15)

    # our routine works with a flattened objective (costs) vector (i.e. not a matrix)
    objective = np.array(objective).flatten()

    solver_solution = np.array(solver_solution).flatten()
    solver_objective_value = cast(float, solver_solution @ objective)

    # our routine demands a filled out matrix for the knapsack restrictions
    for j in range(m):
        for k in range(m):
            if k < j:
                knapsack[j] = [0]*n + knapsack[j]
            if k > j:
                knapsack[j] = knapsack[j] + [0]*n

    problem = Problem(objective, knapsack, b, m, n)
    solution, value, viable = solve_problem(
        problem = problem,
        initial_u = np.zeros(m),
        lamda = 2,
        z_bar = solver_objective_value * 1.5,
        max_iterations = 200,
        max_iterations_without_improvement = 10
    )
    print(f'{solution=}\n{value=}\n{viable=}')
    print(f'Default solver solution: {solver_solution}\n' \
          f'Default solution value: {solver_objective_value}')
