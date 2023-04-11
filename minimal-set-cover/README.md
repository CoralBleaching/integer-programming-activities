# Activity 1:  Set Cover Problem

>Renato Marques de Oliveira

## Table of contents

- [Introduction](#introduction)
    - [Problem formulation](#problem-formulation)
    - [Greedy algorithm](#greedy-algorithm)
- [How to Use](#how-to-use)
    - [Run](#run)
    - [Download](#download)
    - [Build](#build)
- [Code documentation](#code-documentation)
    - [`matrix.hpp`](#matrixhpp)
    - [`main.cpp` (minimalSetCoverGreedy)](#maincpp-minimalsetcovergreedy)


## Introduction

This is a standalone CLI application that solves the specific minimal set cover problem. Executables for Windows and Ubuntu Linux can be found in the Releases page, or it can be built with any C++ compiler (with at least C++17) directly, or through Cmake. Detailed instructions further below.

### Problem formulation

This is how ChatGPT describes the problem (slightly edited):

The set cover problem is a classical problem in computer science and optimization theory that seeks to find the smallest set of sets that covers a given universe of elements.

More specifically, given a universe $U$ of n elements and a collection of $m$ subsets of $U$, each called a set, the goal is to find the smallest subset of the $m$ sets that contains all $n$ elements of $U$. Each set can be thought of as a candidate solution, and the set cover problem asks for the minimum number of such sets needed to cover all elements.

More mathematically:
$$
\begin{align*}
\text{minimize}\quad &\sum_{j=1}^{n} c_j x_j \\
\text{subject to}\quad &\sum_{j: i \in S_j} x_j \geq 1 \quad \forall i \in \{1,2,\ldots,m\}\\
&x_j \in \{0,1\} \quad \forall j \in \{1,2,\ldots,n\}
\end{align*}
$$

In this formulation, we introduce a binary variable $x_j$ for each set $S_j$, where $x_j = 1$ if we select set $S_j$ and $x_j = 0$ otherwise. We aim to minimize the total cost of the selected sets, given by $\sum_{j=1}^{n} c_j x_j$. The constraints ensure that every element $i$ in the universe is covered by at least one selected set: $\sum_{j: i \in S_j} x_j \geq 1$. Here, the summation is over all sets that contain element $i$. 

This problem has important applications in many areas, including scheduling, logistics, telecommunications, and database query optimization. It is also a well-known NP-hard problem, meaning that it is believed to be difficult to solve in the worst case for large instances. However, many practical instances can be solved efficiently using heuristic algorithms or approximation algorithms that provide near-optimal solutions.

> In case you're wondering, yes, this is a precise and correct definition.

### Greedy Algorithm

We will approach the problem with a greedy algorithm: just look for the biggest set and add it to the solution, remove the subsets of the chosen set, then repeat until your solution covers all elements. The precise definition can be found in the file `A1-PI.pdf` (in Portuguese, but intelligible).

## How to use

### Run

The application `minimalSetCoverGreedy` must be run on the terminal, with no arguments. The problem must be formulated as a binary matrix in a file called `entrada.txt`. It outputs the number of variables remaining after preprocessing, the number of restrictions remaining after preprocessing and the final number of selected variables.  For example:
>Contents of `entrada.txt`
```
0001001
0001001
1010001
0011010
0001010
1111110
0000010
0000001
0010001
0001100
```
Output of execution:
```bash
$ ./minimal_set_cover_greedy.exe
No. of variables remaining after preprocessing: 1
No. of restrictions remaining after preprocessing: 1
Final No. of selected variables: 3
```

### Download

You can find executables in the releases page. 
[Download latest release](https://github.com/CoralBleaching/integer-programming-activities/releases/latest). 

Untar the releases with a compatible application (WinRar on Windows, for instance). The app is ready for use.

### Build

The app can be build directly with a C++17 or greater capable compiler. For example, using clang on Windows:
```
clang -std=c++20 -Wall -Wextra -pedantic main.cpp -o minimalSetCoverGreedy.exe
```

It can also be built with CMake. One can build the entire Integer Programming Activities project or piecemeal build any desired subprojects. To build the entire parent project, navigate to the parent directory and run CMake:
```
cmake -B <build-directory> -DCMAKE_INSTALL_PREFIX=<install-directory>

cmake --build <build-directory> --config <desired-configuration (Release, Debug etc)>

cmake --install <build-directory> --strip
```
The executable will be found in the chosen installation directory.

## Code documentation

### `main.cpp` (minimalSetCoverGreedy)

The code includes a few general utility functions:
|Function|Description|
|---|---|
|`parseToIntVector(std::string line)`|Takes a string as input and returns a vector of integers.|
|`readFile(std::string filepath)`|Takes a file path as input, reads in the matrix from the file, and returns it.|
|`fillRange(Container &c, valueType n, valueType start, valueType increment)`|Fills a container `c` with `n` elements, starting at `start`, with an increment of `increment`.|
|`operator<<(std::ostream &os, const Container<valueType> &vector)`|Overloads the `<<` operator to allow printing of vectors. |

The code also has several functions related to pre-processing. Below are utility functions related to pre-processing:

| Function | Description |
| --- | --- |
|`Step1Output`| Enum that represents the output of a function that determines whether a given row in a matrix is a unit vector, a non-unit vector, or a zero vector. `IsUnit` represents the output when the row is a unit vector, i.e., a vector of magnitude `1`. `IsNotUnit` represents the output when the row is not a unit vector, i.e., a vector with magnitude not equal to `1`. `IsZero` represents the output when the row is a zero vector, i.e., a vector with all entries equal to zero.|
| `isUnitVector(Matrix::Row row)` | Takes a matrix row as input and checks if it is a unit vector, i.e., a vector with only one non-zero element. Returns a pair consisting of a `Step1Output` and the index of the non-zero element. If `IsNotUnit` or `IsZero`, the index returned is `-1`. |
| `removeRestrictions(Matrix &A, std::set<size_t> restrictions)` | Removes rows from the matrix `A` with indices in `restrictions`. |
| `removeVariables(Matrix &A, std::set<size_t> variablesToRemove, std::set<size_t> &variablesToKeep)` | Removes columns from the matrix `A` with indices in `variablesToRemove`. The remaining column indices are returned in `variablesToKeep`. |
|`valueGreater`| A functor that compares pairs based on their second element. Used for sorting the rows or columns of a matrix by sum.|
|`isSecondSubsetOfFirst(Container a, Container b)`| Takes two containers and checks if the second one is a subset of the first one.|
|`LINETYPE`| Enum that represents two different options for processing data, either column-wise or row-wise. `COLUMN_WISE` Represents a line type where data is arranged by columns. `ROW_WISE` Represents a line type where data is arranged by rows.|
|`orderBySumDescending<LineWise>(Matrix &A)`| Takes a matrix `A` and returns a `multiset` of pairs where the first element is the index of a row or column in `A` and the second element is the sum of that row or column. If `LineWise` is `COLUMN_WISE`, the multiset is ordered by column sums in descending order, otherwise it's ordered by row sums in descending order.|

And following are the proper pre-processing functions and main algorithm:
|Function|Description|
|---|---|
| `preprocessingStep1(Matrix &A, std::set<size_t> &keptVariables)` | The first step of pre-processing. This function calls `isUnitVector` to identify unit vector rows and removes them as restrictions. It then looks for variables associated with those rows (elements) and removes them. The indices of remaining variables are stored in `keptVariables`. |
|`preprocessingSubRoutine<COLUMN_WISE>(Matrix& A, std::set<size_t>)` `preprocessingSubRoutine<ROW_WISE>(Matrix& A)`| Preprocessing routine that takes a matrix and performs one step of the preprocessing algorithm by removing some rows or columns based on a criterion, which is that if one row or column is a subset of another row or column, then the former (`ROW_WISE` mode) or the latter (`COLUMN_WISE` mode) can be removed. The `LineWise` is used to specialize the function to either remove columns or rows. In `COLUMN_WISE` mode, the `keptVariables` parameter is a reference to a set that keeps track of which variables have not been removed. The function returns a set of indices for columns that are removed. In `ROW_WISE` mode, the function returns `bool` representing whether any rows were removed (`true` if yes).|
|`preprocessingStep2(Matrix &A)`| Calls `preprocessingSubRoutine` with `LineWise` set to `ROW_WISE` to remove unnecessary rows.|
|`preprocessingStep3(Matrix &A, std::set<size_t> &keptVariables)`| Calls `preprocessingSubRoutine` with `LineWise` set to `COLUMN_WISE` to remove unnecessary columns. The `keptVariables` parameter is passed to `preprocessingSubRoutine` to keep track of which columns have not been removed.|
|`preprocess(Matrix &A)`| The main preprocessing routine that repeatedly calls `preprocessingStep1`, `preprocessingStep2`, and `preprocessingStep3` until no more rows or columns can be removed. Returns a tuple containing three sets: `keptVariables` is a set of indices for columns that have not been removed, `removedVariables` is a set of indices for columns that have been removed, and `selectedVariables` is a set of indices for columns that will be included in the final solution.|
|`minimumSetCoverSolveGreedy`| The main algorithm for the minimum set cover problem. Takes a matrix `A` and repeatedly selects the column with the highest number of non-covered elements until all elements are covered. Returns a set of indices for the selected columns. Calls `preprocess` as a preprocessing step. |

### `matrix.hpp`

This is a microscopic version of a larger project of mine, [Cpp-Linear-Algebra](https://github.com/CoralBleaching/Cpp-Linear-Algebra). This Matrix abstraction was implemented here for performance purposes and also easy of use and readability. (Yes, readability and performance not cancelling each other) It was mainly created to avoid use of `std::vector<std::vector<int>>` or tedious manipulation of indices. It also exposes convenient methods that make the code more succint and expressive while still keeping performance cost minimal. I **adopted the phylosophy of in-place operations** and taking inputs as reference arguments in this implementation for this reason. 

This class also provides some basic error checking for out-of-bound access and for adding rows or columns whose size does not match the matrix's dimensions. Furthermore, it has an overloaded operator<< that allows for easy output of the matrix to an output stream.

However, as this small implementation is here to fit a very specific purpose, it lacks any functionality of linear algebra and more sophisticated iterator features.

| Class | Description |
| --- | --- |
| `Matrix` | A data structure for optimized storage and access of matrices. |
| **Members** |  |
| `nrows` | The number of rows in the matrix. |
| `ncols` | The number of columns in the matrix. |
| `data` | A `std::vector<int>` that stores the matrix elements in row-major order. |
| `Row` | A nested class that represents a row in the matrix. Crucially, it provides iterators that allow easy traversal of a row. |
| `Column` | A nested class that represents a column in the matrix. Crucially, it provides iterators that allow easy traversal of a column. |
| `appendRow(InputIterator begin, InputIterator end)` | A member function that appends a row to the matrix. |
| `appendColumn(InputIterator begin, InputIterator end)` | A member function that appends a column to the matrix. |
| `empty()` | A member function that returns true if the matrix is empty, i.e., has zero elements. |
| `removeRow(size_t index)` | A member function that removes a row from the matrix. |
| `removeRows(std::set<size_t> rows)` | A member function that removes a set of rows from the matrix. |
| `removeColumn(size_t index)` | A member function that removes a column from the matrix. |
| `removeColumns(std::set<size_t> columns)` | A member function that removes a set of columns from the matrix. |
| `at(size_t k)` | A member function that returns a reference to the element at the given index in the matrix. |
| `operator[](size_t i)` | An overloaded operator that returns a `Row` object representing the row at the given index in the matrix. |
| `row(size_t i)` | A member function that returns a `Row` object representing the row at the given index in the matrix. |
| `col(size_t i)` | A member function that returns a `Column` object representing the column at the given index in the matrix. |
| `operator<<` | A friend function that overloads the output stream operator to allow printing of the matrix. |