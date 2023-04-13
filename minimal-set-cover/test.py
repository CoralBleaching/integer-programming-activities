# %%
from minimalSetCoverGreedy_py_version import *

# %%
A = np.genfromtxt(os.getcwd() + '/entrada.txt',
                  delimiter=1, dtype=np.int16)
print(A)

# %%
preprocess(A)

# %%
print('preprocess1')
kept_variables = SortedSet(range(A.shape[1]))
print('kept_variables =', kept_variables)
preprocessing_step_1(A, kept_variables)

# %%
print(order_by_sum_descending(A, LineMode.Row))

print('preprocess2')
preprocessing_subroutine(A, LineMode.Row)

# %%
print('preprocess2->3')
B, _, _ = preprocessing_subroutine(A, LineMode.Row)
C, _, k = preprocessing_subroutine(B, LineMode.Column, kept_variables)
print(C, k)

# %%
print('preprocess3')
preprocessing_subroutine(A, LineMode.Column)

# %%
B, _, k = preprocessing_subroutine(A, LineMode.Column, kept_variables)
print(B)
sol = minimum_set_cover_solve_greedy(B)
print(k, sol)

# %%
sol = minimum_set_cover_solve_greedy(A)
print(sol)

##########################################################
# %%
k = SortedSet(range(A.shape[1]))
print(k)
# %%
B, s = preprocessing_step_1(A, k)
print(B, s, k)

# %%
C, pr = preprocessing_subroutine(B, LineMode.Row)
print(C, pr)

# %%
D, pr = preprocessing_subroutine(C, LineMode.Column, k)
print(D, pr, k)

# %%
B, s = preprocessing_step_1(D, k)
print(B, s, k)

# %%
any(A[:, sol].sum(1) == 0)
# %%
