# %%
from minimalSetCoverGreedy_py_version import *

# %%
A = np.genfromtxt(os.getcwd() + '/entrada.txt',
                  delimiter=1, dtype=np.int16)
print(A)
kept_variables = SortedSet(range(A.shape[1]))
print_matrix = False

# %%
print('preprocess(A)')
B, k, r, s = preprocess(A)
print(f'removed vars = {r}\nkept vars = {k}\nselected vars = {s}')
# %%
print('preprocess1')
k = kept_variables.copy()
B, r = preprocessing_step_1(A, k)
print(f'removed vars = {r}\nkept vars = {k}')

# %%
# print(order_by_sum_descending(A, LineMode.Row))

print('preprocess2')
B, _ = preprocessing_subroutine(A, LineMode.Row)
if print_matrix: print(B)
# %%
print('preprocess2->3')
k = kept_variables.copy()
B, _ = preprocessing_subroutine(A, LineMode.Row)
C, r = preprocessing_subroutine(B, LineMode.Column, k)
if print_matrix: print(C)
print(f'removed vars = {r}\nkept vars = {k}')

# %%
print('preprocess3')
k = kept_variables.copy()
B, r = preprocessing_subroutine(A, LineMode.Column, k)
if print_matrix: print(C)
print(f'removed vars = {r}\nkept vars = {k}')

# %%
B, sol, kept, removed = minimum_set_cover_solve_greedy(A)
print(f'sol: [{len(sol)}] {sol}\nkept: [{len(kept)}] {kept}\nrows: [{B.shape[0]}]')

##########################################################
# %%
k = SortedSet(range(A.shape[1]))
print(f'{k=}')
# %%
B, r = preprocessing_step_1(A, k)
if print_matrix: print(B)
print(f'{r=} {k=}')

# %%
C, r = preprocessing_subroutine(B, LineMode.Row)
if print_matrix: print(C)
print(f'{r=}')

# %%
D, r = preprocessing_subroutine(C, LineMode.Column, k)
if print_matrix: print(D)
print(f'{r=} {k=}')

# %%
B, r = preprocessing_step_1(D, k)
if print_matrix: print(B)
print(f'{r=} {k=}')

# %%
any(A[:, sol].sum(1) == 0)
# %%

####################################################################

#%%
remr = SortedSet()
remv = SortedSet()
kk = k.copy()
row_index = 0
for row in E:
    if row.sum() == 1:
        c_idx = np.where(row == 1)[0][0]
        remv.add(c_idx)
        print(f'{c_idx = }')
    if row.sum() == 0:
        print(f'{row_index = }')
        remr.add(row_index)
    row_index += 1
print('remv', remv)
for c_idx in remv:
    row_idxs = np.where(E[:, c_idx] == 1)[0]
    remr.update(row_idxs)
    print(f'{c_idx = } {row_idxs = }')
print(f'{remr = }')

F = np.delete(E, remr, 0)
G = np.delete(F, remv, 1)

print(f'{F = }')
print(f'{G = }')

kk -= remv
print(f'{kk = } {remv = }')

# %%
