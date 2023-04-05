#include <vector>
#include <fstream>
#include <string>
#include <stdexcept>
#include <algorithm>
#include <cstdlib>
#include <iostream>


// Matrix data structure to facilitate optimized storage and access
struct Matrix
{
    Matrix(int m = 0, int n = 0) : nrows(m), ncols(n), data(std::vector<int>(m * n)) {}

    enum LineType { ROW, COLUMN };

    template<LineType type>
    struct Line 
    {
        Line(Matrix& matrix, size_t index) : matrix(matrix), index(index) {}
        int& operator[](size_t);
        Matrix& matrix;
        size_t index;
    };

    void append(std::vector<int> vec) 
    {
        if (vec.size() % ncols != 0) throw std::invalid_argument("Tried to append vector of size not multiple of ncols.");
        for (const int& vi : vec) data.push_back(vi);
        nrows++;
    }
    int& at(size_t k) 
    { 
        if (k >= data.size()) throw std::invalid_argument("Tried to access beyond number of elements.");
        return data[k]; 
    }
    Line<ROW> operator[](size_t i) 
    { 
        if (i>= nrows) throw std::invalid_argument("Tried to access beyond number of rows.");
        return row(i); 
    }
    Line<ROW> row(size_t i) { return Line<ROW>(*this, i); }
    Line<COLUMN> col(size_t j) { return Line<COLUMN>(*this, j); }

    size_t nrows, ncols;
    std::vector<int> data;
    
};

template<>
int& Matrix::Line<Matrix::ROW>::operator[](size_t j)
{
    if (j >= matrix.ncols) throw std::invalid_argument("Tried to access beyond number of columns.");
    return matrix.at(j + index * matrix.ncols);
}

template<>
int& Matrix::Line<Matrix::COLUMN>::operator[](size_t i)
{
    if (i>= matrix.nrows) throw std::invalid_argument("Tried to access beyond number of rows.");
    return matrix.at(index + i * matrix.ncols);
}

// Utility functions

std::vector<int> parseToIntVector(std::string line)
{
    std::vector<int> res;
    std::transform(line.begin(), line.end(), std::back_inserter(res), [](auto c) { return c - '0'; });
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

    std::string line;
    std::getline(file, line);
    A.ncols = line.size();
    A.append(parseToIntVector(line));
    while (std::getline(file, line)) 
    {
        A.append(parseToIntVector(line));
    }
    file.close();
    return A;
}

int main()
{
    auto A = readFile("entrada.txt");
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
}
