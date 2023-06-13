#%%
import igraph as ig
import numpy as np
from ortools.linear_solver import pywraplp

#%%
def generate_graph(rng: np.random.Generator, n: int, density: float) -> ig.Graph:
    vertices = np.arange(n)
    adjacency = np.zeros((n, n))
    max_num_of_edges = int( n * (n - 1) / 2 )
    for _ in range(density * max_num_of_edges):
        while True:
            i, j = rng.choice(vertices, size=2, replace=False)
            if adjacency[i, j] == 0:
                adjacency[i, j], adjacency[j, i] = 1, 1
                break
    return ig.Graph.Adjacency(adjacency, mode="undirected")
        
#%%
def generate_vertex_cover_relaxation(g: ig.Graph):
    solver = pywraplp.Solver.CreateSolver('GLOP')
    if not solver:
        return
    
    solver.EnableOutput()

    n = len(g.vs)
    x = [ solver.IntVar(0, 1, f'x_{i}') for i in range(n)]

    adjacency = g.get_adjacency()
    for i in range(n):
        for j in range(n - i - 1, -1, -1):
            if adjacency[i][j] == 1:
                solver.Add(x[i] + x[j] >= 1)
    
    solver.Minimize( sum(x) )


#%%
gg = generate_graph(np.random.default_rng(2023), 7, 0.5)
ig.plot(gg)