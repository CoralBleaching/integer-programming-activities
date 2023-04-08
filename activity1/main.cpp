#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
#include <set>
#include <string>

#include "matrix.hpp"

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

template <typename Pair>
std::ostream &operator<<(std::ostream &os, std::vector<Pair> vector)
{
    os << "{ ";
    for (auto &elem : vector)
        os << elem << " ";
    os << "}";
    return os;
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

void removeRestrictions(Matrix &A, std::vector<size_t> restrictions)
{
    std::sort(restrictions.begin(), restrictions.end());
    size_t restrictionIndexOffset = 0;
    for (const auto &restrictionIndex : restrictions)
        A.removeRow(restrictionIndex - restrictionIndexOffset++);
}

void removeVariables(Matrix &A, std::vector<size_t> variablesToRemove, std::vector<size_t> &variablesToKeep)
{
    std::sort(variablesToRemove.begin(), variablesToRemove.end());
    size_t variableIndexOffset = 0;
    for (const auto &variableIndex : variablesToRemove)
    {
        A.removeColumn(variableIndex - variableIndexOffset);
        variablesToKeep.erase(variablesToKeep.begin() + variableIndex - variableIndexOffset);
        variableIndexOffset++;
    }
}

std::vector<size_t> preprocessingStep1(Matrix &A, std::vector<size_t> &keptVariables)
{
    std::vector<size_t> restrictions, variables;

    for (size_t i = 0; i < A.nrows; i++)
    {
        try
        {
            auto [isUnitVectorResult, j] = isUnitVector(A.row(i));
            switch (isUnitVectorResult)
            {
            case Step1Output::IsUnitary:
                variables.push_back(j);
            case Step1Output::IsZero:
                restrictions.push_back(i);
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
                restrictions.push_back(i);

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

template <bool IsColumn>
auto preprocessingSubRoutine(Matrix &A, std::conditional_t<IsColumn, std::vector<size_t> &, void *> keptVariables = nullptr)
{
    using LineType = std::conditional_t<IsColumn, Matrix::Column, Matrix::Row>;
    using value_type = std::pair<size_t, int>;

    std::multiset<value_type, valueGreater<value_type>> sums;
    size_t nLines = IsColumn ? A.ncols : A.nrows;
    for (size_t idx = 0; idx < nLines; idx++)
    {
        LineType line_idx(A, idx);
        auto sum = std::accumulate(line_idx.begin(), line_idx.end(), 0);
        sums.emplace(std::make_pair(idx, sum));
    }

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
        removeVariables(A, std::vector<size_t>(markedForRemoval.begin(), markedForRemoval.end()), keptVariables);
        return markedForRemoval;
    }
    else
        removeRestrictions(A, std::vector<size_t>(markedForRemoval.begin(), markedForRemoval.end()));
}

auto preprocessingStep2(Matrix &A)
{
    preprocessingSubRoutine<false>(A);
}

auto preprocessingStep3(Matrix &A, std::vector<size_t> &keptVariables)
{
    return preprocessingSubRoutine<true>(A, keptVariables);
}

// Main program

int main()
{
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

    std::vector<size_t> variables(A.ncols);
    std::iota(variables.begin(), variables.end(), 0);

    auto vars = preprocessingStep1(A, variables);
    std::cout << "removed vars = " << vars << "\nkept vars = " << variables << "\n";
    std::cout << A;

    A = readFile(cwd.string() + "/entrada.txt");
    preprocessingStep2(A);
    std::cout << A;

    A = readFile(cwd.string() + "/entrada.txt");
    variables.resize(A.ncols);
    std::iota(variables.begin(), variables.end(), 0);
    auto vars3 = preprocessingStep3(A, variables);
    std::vector<size_t> vars3v(vars3.begin(), vars3.end());
    std::cout << "removed vars = " << vars3v << "\nkept vars = " << variables << "\n";
    std::cout << A;
}