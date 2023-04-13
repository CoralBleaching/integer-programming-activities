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


def order_by_sum_descending(A: np.ndarray, mode: LineMode) -> List[Tuple[int, int]]:
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


def preprocessing_subroutine(A: np.ndarray, mode: LineMode, kept_variables: Optional[SortedSet] = None) -> Tuple[bool, Optional[SortedSet]]:
    index_sum_pairs = order_by_sum_descending(A, mode)
    marked_for_removal = SortedSet()
    for i, (k, sum_k) in enumerate(index_sum_pairs, 1):
        for l, sum_l in index_sum_pairs[i:]:
            line_k = A[:, k] if mode == LineMode.Column else A[k, :]
            line_l = A[:, l] if mode == LineMode.Column else A[l, :]
            if is_second_subset_of_first(line_k, line_l):
                marked_for_removal.add(l if mode == LineMode.Column else k)

    axis = 1 if mode == LineMode.Column else 0
    A = np.delete(A, marked_for_removal, axis)

    if kept_variables is not None:
        kept_variables -= marked_for_removal

    return A, len(marked_for_removal) > 0


def preprocess(A: np.ndarray) -> Tuple[Set[int], SortedSet]:
    kept_variables = SortedSet(range(A.shape[1]))
    selected_variables = SortedSet()

    processed = True
    while (processed):
        processed = False
        A, selected = preprocessing_step_1(A, kept_variables)
        if len(selected) != 0:
            processed = True
        selected_variables.update(selected)
        print(selected_variables)

        A, step2 = preprocessing_subroutine(A, LineMode.Row)
        if step2:
            processed = True

        A, has_processed = preprocessing_subroutine(
            A, LineMode.Column, kept_variables)
        if (has_processed):
            processed = True

    return A, kept_variables, selected_variables


def minimum_set_cover_solve_greedy(A: np.ndarray):
    A, kept_variables, selected_variables = preprocess(A)

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

    return selected_variables


def main():
    A = np.genfromtxt(os.getcwd() + '/entrada.txt',
                      delimiter=1, dtype=np.int16)
    sol = minimum_set_cover_solve_greedy(A)
    print(sol)


if __name__ == '__main__':
    main()
