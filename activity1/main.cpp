#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
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

template <typename T>
std::ostream &operator<<(std::ostream &os, std::vector<T> vector)
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

std::vector<size_t> preprocessingStep1(Matrix &A)
{
    std::vector<size_t> sets, variables;
    for (size_t i = 0; i < A.nrows; i++)
    {
        try
        {
            auto [isUnitVectorResult, variableIndex] = isUnitVector(A.row(i));
            switch (isUnitVectorResult)
            {
            case Step1Output::IsUnitary:
                sets.push_back(i);
            case Step1Output::IsZero:
                variables.push_back(variableIndex);
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
    size_t setIndexOffset = 0;
    for (const auto &setIndex : sets)
    {
        A.removeRow(setIndex - setIndexOffset++);
    }
    return variables;
}

/// Step 2

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

    auto vars = preprocessingStep1(A);
    std::cout << "vars = " << vars << "\n";
    std::cout << A;

    std::vector<int> newCol = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};
    A.appendColumn(newCol);
    std::cout << A;
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