#%%
import igraph as ig
import numpy as np
from ortools.linear_solver import pywraplp

SOLVER = 'GLOP'
#%%
def generate_graph(rng: np.random.Generator, n: int, density: float) -> ig.Graph:
    vertices = np.arange(n)
    adjacency = np.zeros((n, n))
    max_num_of_edges = n * (n - 1) / 2 
    for _ in range(round(density * max_num_of_edges)):
        while True:
            i, j = rng.choice(vertices, size=2, replace=False)
            if adjacency[i, j] == 0:
                adjacency[i, j], adjacency[j, i] = 1, 1
                break
    g = ig.Graph.Adjacency(adjacency, mode="undirected")
    g.vs['label'] = list(range(n))
    return g
        
#%%
def generate_vertex_cover_problem(
        graph: ig.Graph, 
        fixed_vars: list[tuple[int, int]] | None = None,
        solver_version: str = SOLVER
        ) -> pywraplp.Solver | None:
    solver: pywraplp.Solver = pywraplp.Solver.CreateSolver(solver_version)
    if not solver:
        return
    
    # solver.EnableOutput()

    n = len(graph.vs)
    x = [ solver.IntVar(0, 1, f'x_{i}') for i in range(n)]

    solver.Minimize(sum(x))

    adjacency = graph.get_adjacency()
    for i in range(1, n):
        for j in range(0, i):
            if adjacency[i][j] == 1:
                if i < j: 
                    continue
                solver.Add(x[i] + x[j] >= 1,
                           f'x_{i} + x_{j} >= 1')
    
    if fixed_vars is not None:
        for index, value in fixed_vars:
            solver.Add(x[index] == value, f'x_{index} == {value}')
    
    return solver

#%%
def get_objective_value(vars: list[pywraplp.Variable]) -> float:
    return sum(var.solution_value() for var in vars)    

#%%
def solve_bab_vertex_cover(graph: ig.Graph) -> tuple[float, tuple[float, ...]] | None:
    solver = generate_vertex_cover_problem(graph)
    if solver is None: 
        return
    solver.Solve()
    
    objective: float = len(graph.vs)
    vars: list[pywraplp.Variable] = []

    stack: list[tuple[pywraplp.Solver, list[tuple[int, int]]]] = \
        [(solver, [])]
    
    optimum = objective

    while len(stack) > 0:
        solved_problem, fixed_vars = stack.pop()

        objective = get_objective_value(solved_problem.variables())
        vars = solved_problem.variables()
        
        branching_index: int | None = None
        for i, var in enumerate(vars):
            if 0 < var.solution_value() < 1:
                branching_index = i
                break
        
        if branching_index is None:
            if objective < optimum:
                optimum = objective
            continue
        
        fixed_vars_ceil = fixed_vars + [(branching_index, 1)]
        fixed_vars_floor = fixed_vars + [(branching_index, 0)]

        solver_ceil = generate_vertex_cover_problem(graph, fixed_vars_ceil)
        solver_floor = generate_vertex_cover_problem(graph, fixed_vars_floor)

        if (solver_ceil is None or solver_floor is None):
            return

        solver_ceil.Solve()
        solver_floor.Solve()
        stack.append(
            (solver_ceil, fixed_vars_ceil)
        )
        stack.append(
            (solver_floor, fixed_vars_floor)
        )

    return optimum, tuple(var.solution_value() for var in vars)    

#%%
def print_solution(solution: tuple[float, tuple[float, ...]] | None):
    if solution is None: 
        return
    objective, vars = solution
    print(f'{objective = }')
    for i, var in enumerate(vars):
        print(f'x_{i} = {var}')

#%%
def run_example(gg: ig.Graph, solver_version = SOLVER):
    solver = generate_vertex_cover_problem(gg, solver_version=solver_version)
    if not solver: 
        return
    # for constraint in solverr.constraints():
    #     print(constraint.name())
    solver.Solve()
    print(f'objective = {get_objective_value(solver.variables())}')
    for var in solver.variables():
        print(f'{var.name()} = {var.solution_value()}')

#%%
gg = generate_graph(np.random.default_rng(2023), 7, 0.5)
run_example(gg)
ig.plot(gg)

# %%
gg2 = generate_graph(np.random.default_rng(2023), 8, 0.5)
run_example(gg2)
ig.plot(gg2)
#%%
print_solution(solve_bab_vertex_cover(gg2))
# %%
gg3 = generate_graph(np.random.default_rng(2023), 9, 0.5)
run_example(gg3)
ig.plot(gg3)

#%%
run_example(gg3, 'SCIP')
print_solution(solve_bab_vertex_cover(gg3))
# %%
gg4 = generate_graph(np.random.default_rng(2023), 14, 0.3)
run_example(gg4)
ig.plot(gg4)

#%%
run_example(gg4, 'SCIP')
print_solution(solve_bab_vertex_cover(gg4))

