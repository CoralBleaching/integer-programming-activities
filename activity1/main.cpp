#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
#include <set>
#include <string>

#include "matrix.hpp"

// TO DO: remove the "remove variables" tracking variable? Superfluous?

// Utility functions

std::vector<int> parseToIntVector(std::string line)
{
    std::vector<int> res;
    std::transform(line.begin(), line.end(), std::back_inserter(res), [](auto c)
                   { return c - '0'; });
    return res;
}

Matrix readFile(std::string filepath)
{
    Matrix A;
    auto file = std::ifstream(filepath);

    if (!file.is_open())
    {
        throw std::runtime_error("File not found.");
    }

    try
    {
        std::string line;
        std::getline(file, line);
        A.ncols = line.size();
        A.appendRow(parseToIntVector(line));
        while (std::getline(file, line))
        {
            A.appendRow(parseToIntVector(line));
        }
    }
    catch (const std::invalid_argument &err)
    {
        std::cerr << err.what() << '\n';
    }

    file.close();
    return A;
}

template <template <typename...> typename Container, typename valueType>
std::ostream &operator<<(std::ostream &os, const Container<valueType> &vector)
{
    os << "{ ";
    for (auto &elem : vector)
        os << elem << " ";
    os << "}";
    return os;
}

template <typename Container, typename valueType = size_t>
void fillRange(Container &c, valueType n, valueType start = static_cast<valueType>(0), valueType increment = static_cast<valueType>(1))
{
    valueType i = start;
    std::generate_n(std::inserter(c, c.begin()), n, [increment, &i]() mutable
                    { auto prev = i; i += increment; return prev; });
}

// Pre-processing steps

/// Step 1

enum class Step1Output
{
    IsUnitary,
    IsNonUnitary,
    IsZero
};

std::pair<Step1Output, size_t> isUnitVector(Matrix::Row row)
{
    int sum = std::accumulate(row.begin(), row.end(), 0);
    if (sum > 1)
        return std::make_pair(Step1Output::IsNonUnitary, static_cast<size_t>(-1));
    if (sum == 0)
        return std::make_pair(Step1Output::IsZero, static_cast<size_t>(-1));
    size_t variableIndex = 0;
    for (auto &j : row)
    {
        if (j != 0 && j != 1)
            throw std::runtime_error("Defective entries (not in {0, 1}) detected in data.");
        if (j)
            return std::make_pair(Step1Output::IsUnitary, variableIndex);
        variableIndex++;
    }
    throw std::runtime_error("Unkown error: this step is unreachable.");
}

void removeRestrictions(Matrix &A, std::set<size_t> restrictions)
{
    size_t restrictionIndexOffset = 0;
    for (const auto &restrictionIndex : restrictions)
        A.removeRow(restrictionIndex - restrictionIndexOffset++);
}

void removeVariables(Matrix &A, std::set<size_t> variablesToRemove, std::set<size_t> &variablesToKeep)
{
    size_t variableIndexOffset = 0;
    for (const auto &variableIndex : variablesToRemove)
    {
        A.removeColumn(variableIndex - variableIndexOffset);
        variablesToKeep.erase(std::next(variablesToKeep.begin(), variableIndex - variableIndexOffset));
        variableIndexOffset++;
    }
}

std::set<size_t> preprocessingStep1(Matrix &A, std::set<size_t> &keptVariables)
{
    std::set<size_t> restrictions, variables;

    for (size_t i = 0; i < A.nrows; i++)
    {
        try
        {
            auto [isUnitVectorResult, j] = isUnitVector(A.row(i));
            switch (isUnitVectorResult)
            {
            case Step1Output::IsUnitary:
                variables.emplace(j);
            case Step1Output::IsZero:
                restrictions.emplace(i);
                break;
            default:
                break;
            }
        }
        catch (std::runtime_error &err)
        {
            throw err;
        }
    }

    removeRestrictions(A, restrictions);
    restrictions.clear();

    for (size_t j : variables)
        for (size_t i = 0; i < A.nrows; i++)
            if (A[i][j] == 1)
                restrictions.emplace(i);

    removeRestrictions(A, restrictions);

    removeVariables(A, variables, keptVariables);

    return variables;
}

/// Steps 2 and 3

template <typename Pair>
struct valueGreater
{
    bool operator()(const Pair &a, const Pair &b) const
    {
        return a.second > b.second;
    }
};

template <typename Container>
bool isSecondSubsetOfFirst(Container a, Container b)
{
    for (auto itA = std::begin(a), itB = std::begin(b); itA != std::end(a); itA++, itB++)
        if (*itB > *itA) // should be false everytime if b c A
            return false;
    return true;
}

enum LINETYPE
{
    COLUMN_WISE,
    ROW_WISE
};

template <LINETYPE LineWise>
auto orderBySumDescending(Matrix &A)
{
    constexpr bool IsColumn = LineWise == COLUMN_WISE;
    using LineType = std::conditional_t<IsColumn, Matrix::Column, Matrix::Row>;
    using Pair = std::pair<size_t, int>;

    std::multiset<Pair, valueGreater<Pair>> sums;
    size_t nLines = IsColumn ? A.ncols : A.nrows;
    for (size_t idx = 0; idx < nLines; idx++)
    {
        LineType line_idx(A, idx);
        auto sum = std::accumulate(line_idx.begin(), line_idx.end(), 0);
        sums.emplace(std::make_pair(idx, sum));
    }
    return sums;
}

template <LINETYPE LineWise, bool IsColumn = LineWise == COLUMN_WISE>
auto preprocessingSubRoutine(Matrix &A, std::conditional_t<IsColumn, std::set<size_t> &, void *> keptVariables = nullptr)
{
    using LineType = std::conditional_t<IsColumn, Matrix::Column, Matrix::Row>;

    auto sums = orderBySumDescending<LineWise>(A);

    std::set<size_t> markedForRemoval;
    for (auto k = sums.begin(); k != sums.end(); k++)
    {
        for (auto l = std::next(k); l != sums.end(); l++)
        {
            size_t line_k_index = k->first;
            size_t line_l_index = l->first;
            LineType line_k(A, line_k_index);
            LineType line_l(A, line_l_index);
            if (isSecondSubsetOfFirst(line_k, line_l))
            {
                markedForRemoval.emplace(
                    IsColumn ? line_l_index : line_k_index);
            }
        }
    }

    if constexpr (IsColumn)
    {
        removeVariables(A, markedForRemoval, keptVariables);
        return markedForRemoval;
    }
    else
    {
        removeRestrictions(A, markedForRemoval);
        return markedForRemoval.empty();
    }
}

auto preprocessingStep2(Matrix &A)
{
    return preprocessingSubRoutine<ROW_WISE>(A);
}

auto preprocessingStep3(Matrix &A, std::set<size_t> &keptVariables)
{
    return preprocessingSubRoutine<COLUMN_WISE>(A, keptVariables);
}

// Main preprocessing routine

auto preprocess(Matrix &A)
{
    std::set<size_t> keptVariables;
    fillRange(keptVariables, A.ncols);
    std::set<size_t> removedVariables, selectedVariables;

    bool processed = false;
    while (!processed)
    {
        processed = false;

        auto step1 = preprocessingStep1(A, keptVariables);
        if (!step1.empty())
            processed = true;
        removedVariables.insert(step1.begin(), step1.end());
        selectedVariables.merge(step1);

        if (preprocessingStep2(A))
            processed = true;

        auto step3 = preprocessingStep3(A, keptVariables);
        if (!step3.empty())
            processed = true;
        removedVariables.merge(step3);
    }

    return std::make_tuple(keptVariables, removedVariables, selectedVariables);
}

// Main algorithm:
// Greedy minimum set cover algorithm

auto minimumSetCoverSolveGreedy(Matrix &A)
{
    auto [kept, removed, selected] = preprocess(A);

    while (!A.empty())
    {
        for (size_t j = 0; j < A.ncols; j++)
        {
            // Find S* := subset with most non-covered elements
            auto sums = orderBySumDescending<COLUMN_WISE>(A);
            auto maxCol = sums.begin()->first;
            auto selectedVariable = *std::next(kept.begin(), maxCol);
            // Include S* (x_j) in the solution
            selected.emplace(selectedVariable);

            auto sStar = A.col(maxCol);

            // Update set of non-covered elements (U := U - S*)
            std::set<size_t> rowsToRemove;
            for (size_t i = 0; i < A.nrows; i++)
                if (sStar[i])
                    rowsToRemove.emplace(i);
            removeRestrictions(A, rowsToRemove);

            // Remove S* from the available subsets (remove x_j from problem)
            removeVariables(A, {maxCol}, kept);

            // If any remaining subset becomes empty, remove it
            std::set<size_t> columnsToRemove;
            for (size_t j = 0; j < A.ncols; j++)
            {
                auto col_j = A.col(j);
                auto sum = std::accumulate(col_j.begin(), col_j.end(), 0);
                if (sum == 0)
                    columnsToRemove.emplace(j);
            }
            removeVariables(A, columnsToRemove, kept);
        }
    }

    return selected;
}

// Main program

int main()
{
    std::set<float> test;
    fillRange(test, 10.f, 3.5f, 0.01f);
    std::cout << test << "\n";
    test.clear();
    fillRange(test, 5);
    std::cout << test << std::endl;

    auto cwd = std::filesystem::current_path();
    Matrix A;
    try
    {
        A = readFile(cwd.string() + "/entrada.txt");
    }
    catch (std::runtime_error &err)
    {
        std::cerr << err.what() << "\n";
        return 1;
    }
    std::cout << A;

    std::set<size_t> variables;
    fillRange(variables, A.ncols);

    auto vars = preprocessingStep1(A, variables);
    std::cout << "removed vars = " << vars << "\nkept vars = " << variables << "\n";
    std::cout << A;

    A = readFile(cwd.string() + "/entrada.txt");
    preprocessingStep2(A);
    std::cout << A;

    A = readFile(cwd.string() + "/entrada.txt");
    variables.clear();
    fillRange(variables, A.ncols);
    auto vars3 = preprocessingStep3(A, variables);
    std::vector<size_t> vars3v(vars3.begin(), vars3.end());
    std::cout << "removed vars = " << vars3v << "\nkept vars = " << variables << "\n";
    std::cout << A;

    A = readFile(cwd.string() + "/entrada.txt");
    auto [kep, rem, sel] = preprocess(A);
    std::cout << "removed vars = " << rem << "\nkept vars = " << kep << "\n"
              << "selected vars = " << sel << "\n"
              << A << std::endl;

    A = readFile(cwd.string() + "/entrada.txt");
    auto sol = minimumSetCoverSolveGreedy(A);
    std::cout << sol.size() << ": " << sol << "\n";
}