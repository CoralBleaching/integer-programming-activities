from enum import Enum, auto
from sortedcontainers import SortedSet, SortedKeyList
from typing import List, Set, Tuple, Optional
import numpy as np
import os


def preprocessing_step_1(A: np.ndarray, kept_variables: SortedSet):
    removed_restrictions = SortedSet()
    removed_variables = SortedSet()
    row_index = 0
    for row in A:
        row_sum = row.sum()
        if row_sum == 1:
            column_index = np.where(row == 1)[0][0]
            removed_variables.add(column_index)
        if row_sum == 0:
            removed_restrictions.add(row_index)
        row_index += 1
    for var_index in removed_variables:
        removed_restrictions.update(np.where(A[:, var_index] == 1)[0])

    A = np.delete(A, removed_restrictions, 0)
    A = np.delete(A, removed_variables, 1)

    removed_variables = SortedSet(np.array(kept_variables)[removed_variables])
    kept_variables -= removed_variables

    return A, removed_variables


class LineMode(Enum):
    Column = auto()
    Row = auto()


def order_by_sum_descending(A: np.ndarray, mode: LineMode):
    index_sum_pairs = SortedKeyList(key=lambda x: x[1])
    axis = 1 if mode == LineMode.Column else 0
    sums = A.sum(int(not axis))
    for idx in range(A.shape[axis]):
        index_sum_pairs.add((idx, sums[idx]))
    return list(reversed(index_sum_pairs))


def is_second_subset_of_first(a, b) -> bool:
    for k in range(len(a)):
        if b[k] > a[k]:
            return False
    return True


def preprocessing_subroutine(
        A: np.ndarray, 
        mode: LineMode,
        kept_variables: Optional[SortedSet] = None
        ):
    index_sum_pairs = order_by_sum_descending(A, mode)
    marked_for_removal = SortedSet()
    for i, (k, sum_k) in enumerate(index_sum_pairs, 1):
        for l, sum_l in index_sum_pairs[i:]:
            line_k = A[:, k] if mode == LineMode.Column else A[k, :]
            line_l = A[:, l] if mode == LineMode.Column else A[l, :]
            # print(f'{k}:{line_k} {l}:{line_l}')
            if is_second_subset_of_first(line_k, line_l):
                marked_for_removal.add(l if mode == LineMode.Column else k)
                # print(f'{l} is subset of {k}')

    axis = 1 if mode == LineMode.Column else 0
    print(f'{axis = } {A.shape = }')
    A = np.delete(A, marked_for_removal, axis)
    print(f'{A.shape = }')


    if kept_variables is not None:
        marked_for_removal = SortedSet(np.array(kept_variables)[marked_for_removal])
        kept_variables -= marked_for_removal

    return A, marked_for_removal


def preprocess(A: np.ndarray):
    kept_variables = SortedSet(range(A.shape[1]))
    selected_variables = SortedSet()
    removed_variables = SortedSet()

    processed = True
    while (processed):
        processed = False
        A, selected = preprocessing_step_1(A, kept_variables)
        if len(selected) != 0:
            processed = True
            selected_variables.update(selected)
            removed_variables.update(selected)
        print(f'1)\nr = {selected}\ns = {selected_variables}')

        A, step2 = preprocessing_subroutine(A, LineMode.Row)
        if len(step2) > 0:
            processed = True
        print(f'2)\nr = {step2}')

        A, removed = preprocessing_subroutine(
            A, LineMode.Column, kept_variables)
        if len(removed) > 0:
            processed = True
            removed_variables.update(removed)
        print(f'3)\nr = {removed}')


    return A, kept_variables, removed_variables, selected_variables


def minimum_set_cover_solve_greedy(A: np.ndarray):
    A, kept_variables, removed_variables, selected_variables = preprocess(A)
    B = A.copy()

    while not (A.shape[1] == 0 or A.shape[0] == 0):
        sums = order_by_sum_descending(A, LineMode.Column)
        max_col = sums[0][0]
        selected_variables.add(kept_variables[max_col])

        s_star = A[:, max_col]

        rows_to_remove = SortedSet()
        for i in range(A.shape[0]):
            if s_star[i] == 1:
                rows_to_remove.add(i)

        A = np.delete(A, rows_to_remove, 0)

        columns_to_remove = SortedSet([max_col])
        for j in range(A.shape[1]):
            if A[:, j].sum() == 0:
                columns_to_remove.add(j)

        A = np.delete(A, columns_to_remove, 1)

    return B, selected_variables, kept_variables, removed_variables


def main():
    A = np.genfromtxt(os.getcwd() + '/entrada.txt',
                      delimiter=1, dtype=np.int16)
    B, sol, kept, removed = minimum_set_cover_solve_greedy(A)
    print(f'sol: {sol}\nkept: [{len(kept)}] {kept}\nrows: [{B.shape[0]}]')


if __name__ == '__main__':
    main()
