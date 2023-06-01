from ortools.linear_solver import pywraplp

def puzzle(solver: pywraplp.Solver | None = None, 
           new_restrictions: dict[str, int] | None = None):
    if solver is None:
        solver = pywraplp.Solver.CreateSolver('SCIP')
        
        x,y,z = [],[],[]
        for i in range(1,10):
            x.append(solver.IntVar(0,1, f'x_{i}'))
            y.append(solver.IntVar(0,1, f'y_{i}'))
            z.append(solver.IntVar(0,1, f'z_{i}'))
        
        solver.Add(sum(x) == 1)
        solver.Add(sum(y) == 1)
        solver.Add(sum(z) == 1)

        for i in range(9):
            solver.Add(sum([x[i], y[i], z[i]]) <= 1)

        solver.Add(x[1] + y[7] + z[8] == 1)
        solver.Add(x[6] + y[2] + z[7] == 0)
        solver.Add(x[0] + x[4] + y[1] + y[4] + z[1] + z[0] == 1)
        solver.Add(x[7] + x[3] + y[6] + y[3] + z[6] + z[7] == 1)
        solver.Add(x[3] + x[1] + y[8] + y[1] + z[8] + z[3] == 2)

        solver.Maximize(sum(list(map(sum, (x,y,z)))))

    print(f'{solver.NumConstraints()=}')

    if new_restrictions is not None and len(new_restrictions) > 0:
        while(len(new_restrictions) > 0):
            variables = solver.variables()
            x = variables[0::3]
            y = variables[1::3]
            z = variables[2::3]
            var, digit = new_restrictions.popitem()
            if var == 'x':
                print(f'x_{digit} = 0')
                solver.Add(x[digit - 1] == 0)
                solver.Add
            if var == 'y':
                print(f'y_{digit} = 0')
                solver.Add(y[digit - 1] == 0)
            if var == 'z':
                print(f'z_{digit} = 0')
                solver.Add(z[digit - 1] == 0)


    status = solver.Solve()
    solutions: set[str] = set()
    while True:
        solution = str('XYZ')
        if status == pywraplp.Solver.OPTIMAL:
                for i in range(9):
                    if x[i].solution_value() > 0:
                        print(f'x_{i + 1}={x[i].solution_value()}')
                        solution = solution.replace('X', str(i + 1))
                    if y[i].solution_value() > 0:
                        solution = solution.replace('Y', str(i + 1))
                        print(f'y_{i + 1}={y[i].solution_value()}')
                    if z[i].solution_value() > 0:
                        solution = solution.replace('Z', str(i + 1))
                        print(f'z_{i + 1}={z[i].solution_value()}')
                print(f'{solution = }')
                print('Objective function value =', solver.Objective().Value())
                solutions.add(solution)
        if (not solver.NextSolution()):
            break

    return solver, status, solutions

def main():
    solver, status, previous_solutions = puzzle()
    new_restrictions: dict[str, int] | None = {'x': int(sol[0]) for sol in previous_solutions}
    counter = 0
    while True:
        solver, status, solutions = puzzle(new_restrictions=new_restrictions)
        # if status != pywraplp.Solver.OPTIMAL:
        #     print(status)
        #     break
        
        for previous_solution, solution in zip(previous_solutions, solutions):
            for i, (prev_digit, curr_digit) in enumerate(zip(previous_solution, solution)):
             if prev_digit == curr_digit:
                new_restrictions.update({'xyz'[i]: int(curr_digit)})
                # if status == pywraplp.Solver.OPTIMAL: 
                #     break

        if solutions.issubset(previous_solutions):
            counter += 10
            if counter >= len(previous_solutions):
                break
        else:
            counter = 0
            previous_solutions.update(solutions)
        
                  
    
if __name__ == '__main__':
    main()