from enum import Enum, auto
from sortedcontainers import SortedSet, SortedKeyList
from typing import Set, Tuple, Optional
import numpy as np
import os


class Step1Output(Enum):
    IsUnit = auto()
    IsNotUnit = auto()
    IsZero = auto()


def is_unit_vector(arr: np.ndarray) -> Tuple[Step1Output, int]:
    sum = arr.sum()
    if sum > 1:
        return Step1Output.IsNotUnit, -1
    elif sum == 0:
        return Step1Output.IsZero, -1

    variable_index = 0
    for j in arr:
        if j != 0 and j != 1:
            raise ValueError(
                'Defective entries (not in {0, 1}) detected in data.')
        if j == 1:
            return Step1Output.IsUnit, variable_index
        variable_index += 1


def preprocessing_step_1(A: np.ndarray, kept_variables: SortedSet) -> Set:
    removed_restrictions = SortedSet()
    removed_variables = SortedSet()

    for row in A:
        is_unit_vector_result, j = is_unit_vector(row)
        if is_unit_vector_result == Step1Output.IsUnit:
            removed_variables.add(j)
        if is_unit_vector_result != Step1Output.IsNotUnit:
            removed_restrictions.add(j)

    for j in removed_variables:
        for i in range(A.shape[0]):
            if A[i, j] == 1:
                removed_restrictions.add(i)

    A = np.delete(A, removed_restrictions, 0)
    A = np.delete(A, removed_variables, 1)

    kept_variables -= removed_variables

    return A, removed_variables, kept_variables


class LineMode(Enum):
    Column = auto()
    Row = auto()


def order_by_sum_descending(A: np.ndarray, mode: LineMode) -> SortedKeyList[int, int]:
    index_sum_pairs = SortedKeyList(key=lambda x: x[1])
    axis = 1 if mode == LineMode.Column else 0
    sums = A.sum(int(not axis))
    for idx in range(A.shape[axis]):
        index_sum_pairs.add((idx, sums[idx]))
    return index_sum_pairs


def is_second_subset_of_first(a, b) -> bool:
    for k in range(len(a)):
        if b[k] > a[k]:
            return False
    return True


def preprocessing_subroutine(A: np.ndarray, mode: LineMode, kept_variables: Optional[SortedSet] = None) -> Tuple[bool, Optional[SortedSet]]:
    index_sum_pairs = order_by_sum_descending(A, mode)
    removed_variables = SortedSet()
    for k, sum_k in index_sum_pairs:
        for l, sum_l in index_sum_pairs[k + 1:]:
            line_k = A[:, k] if mode == LineMode.Column else A[k, :]
            line_l = A[:, l] if mode == LineMode.Column else A[l, :]
            if is_second_subset_of_first(line_k, line_l):
                removed_variables.add(l if mode == LineMode.Column else k)

    axis = 1 if mode == LineMode.Column else 0
    A = np.delete(A, removed_variables, axis)

    if kept_variables is not None:
        kept_variables -= removed_variables

    return A, len(removed_variables) > 0, kept_variables


def preprocess(A: np.ndarray) -> Tuple[Set[int], SortedSet]:
    kept_variables = SortedSet(range(A.shape[1]))
    selected_variables = SortedSet()

    processed = True
    while (processed):
        processed = False
        A, selected, kept_variables = preprocessing_step_1(A, kept_variables)
        if len(selected) != 0:
            processed = True
        selected_variables.update(selected)

        A, step2, _ = preprocessing_subroutine(A, LineMode.Row)
        if step2:
            processed = True

        A, has_processed, kept_variables = preprocessing_subroutine(
            A, LineMode.Column, kept_variables)
        if (has_processed):
            processed = True

    return A, kept_variables, selected_variables


def minimum_set_cover_solve_greedy(A: np.ndarray):
    A, kept_variables, selected_variables = preprocess(A)

    while not A.shape[1] == 0:
        sums = order_by_sum_descending(A, LineMode.Column)
        max_col = sums[-1][0]
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
