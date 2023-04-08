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

/// Step 2

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

auto preprocessingStep2(Matrix &A)
{
    using value_type = std::pair<size_t, int>;
    std::multiset<value_type, valueGreater<value_type>> sums;
    for (size_t i = 0; i < A.nrows; i++)
    {
        auto row_i = A.row(i);
        auto sum = std::accumulate(row_i.begin(), row_i.end(), 0);
        sums.emplace(std::make_pair(i, sum));
    }

    std::set<size_t> markedForRemoval;
    for (auto i = sums.begin(); i != sums.end(); i++)
    {
        for (auto k = std::next(i); k != sums.end(); k++)
        {
            size_t row_i_index = i->first;
            size_t row_k_index = k->first;
            auto row_i = A.row(row_i_index);
            auto row_k = A.row(row_k_index);
            if (isSecondSubsetOfFirst(row_i, row_k))
            {
                std::cout << "row_" << row_k_index << " is subset of row_" << row_i_index << "!\n";
                markedForRemoval.emplace(row_i_index);
            }
        }
    }

    removeRestrictions(A, std::vector<size_t>(markedForRemoval.begin(), markedForRemoval.end()));

    return sums;
}

// Step 3

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
    auto m = preprocessingStep2(A);
    std::cout << A;
    for (auto mm : m)
        std::cout << mm.first << ": " << mm.second << "\n";

    // std::vector<int> newCol = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};
    // A.appendColumn(newCol);
    // std::cout << A;

    // A.removeColumn(6);
    // std::cout << A << "\n"
    //           << A.nrows << " "
    //           << A.ncols << "\n";
}

/*
    std::cout << A.nrows << "  " << A.ncols << "\n";
    for (size_t i = 0; i < A.nrows; i++)
    {
        for (size_t j = 0; j < A.ncols; j++)
        {
            std::cout << A[i][j] << " ";
        }
        std::cout << "\n";
    }
    std::cout << "\n";

    for (size_t j = 0; j < A.ncols; j++)
    {
        auto col = A.col(j);
        for (size_t i = 0; i < A.nrows; i++)
        {
            std::cout << col[i] << " ";
        }
        std::cout << "\n";
    }
    std::cout << "\n";

    auto col = A.col(6);
    for (auto c : col) std::cout << c << " ";
    std::cout << "\n";
*/