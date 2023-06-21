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
def generate_vertex_cover_problem(graph: ig.Graph) -> pywraplp.Solver | None:
    solver: pywraplp.Solver = pywraplp.Solver.CreateSolver(SOLVER)
    if not solver:
        return
    
    # solver.EnableOutput()

    n = len(graph.vs)
    x = [ solver.NumVar(0, 1, f'x_{i}') for i in range(n)]

    adjacency = graph.get_adjacency()
    for i in range(1, n):
        for j in range(0, i):
            if adjacency[i][j] == 1:
                if i < j: 
                    continue
                solver.Add(x[i] + x[j] >= 1,
                           f'x_{i} + x_{j} >= 1')
    
    solver.Minimize(sum(x))

    return solver
    

#%%

def solve_bab_vertex_cover(
        graph: ig.Graph, 
        precision: float = 1e-10
) -> tuple[float, tuple[float, ...]] | None:
    solver = generate_vertex_cover_problem(graph)
    if solver is None: 
        return
    solver.Solve()
    vars: list[pywraplp.Variable] = solver.variables()
    
    objective: float = solver.Objective().Value()

    stack: list[tuple[float, tuple[int, ...]]] = \
        [(objective, ())]
    
    optimum = objective

    while len(stack) > 0:
        objective, fixed_vars = stack.pop()
        branching_index: int | None = None
        for i, var in enumerate(vars):
            if 0 < var.solution_value() < 1:
                branching_index = i
                break
        
        if branching_index is None:
            if objective < optimum:
                optimum = objective
            return optimum, tuple(var.solution_value() for var in vars)
        
        solver_ceil = generate_vertex_cover_problem(graph)
        solver_floor = generate_vertex_cover_problem(graph)
        if (solver_ceil is None or solver_floor is None):
            return None
        for fixed_var in fixed_vars:
            solver_ceil.Add(vars[fixed_var] == 1)
            solver_floor.Add(vars[fixed_var] == 0)

        fixed_vars += (branching_index,)
        stack.append(
            (solver_ceil.Objective().Value(), fixed_vars)
        )
        stack.append(
            (solver_floor.Objective().Value(), fixed_vars)
        )
        

    # solver.a
    

#%%
def run_example(gg: ig.Graph):
    solverr = generate_vertex_cover_problem(gg)
    if not solverr: 
        return
    for constraint in solverr.constraints():
        print(constraint.name())
    solverr.Solve()
    for var in solverr.variables():
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



