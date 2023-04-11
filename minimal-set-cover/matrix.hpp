#include <cstdlib>
#include <stdexcept>
#include <vector>

// Matrix data structure to facilitate optimized storage and access
struct Matrix
{
    Matrix(int m = 0, int n = 0) : nrows(m), ncols(n), data(std::vector<int>(m * n)) {}

    struct Row
    {
        Row(Matrix &matrix, size_t index) : matrix(matrix), index(index) {}
        int &operator[](size_t j)
        {
            if (j >= matrix.ncols)
                throw std::invalid_argument("Tried to access beyond number of columns.");
            return matrix.at(j + index * matrix.ncols);
        }
        auto begin() { return matrix.data.begin() + index * matrix.ncols; }
        auto end() { return matrix.data.begin() + (index + 1) * matrix.ncols; }
        Matrix &matrix;
        size_t index;
    };

    struct Column
    {
        Column(Matrix &matrix, size_t index) : matrix(matrix),
                                               index(index)
        {
            for (size_t i = 0; i < matrix.nrows; i++)
                references.emplace_back(operator[](i));
        }
        int &operator[](size_t i)
        {
            if (i >= matrix.nrows)
                throw std::invalid_argument("Tried to access beyond number of rows.");
            return matrix.at(index + i * matrix.ncols);
        }
        auto begin() { return references.begin(); }
        auto end() { return references.end(); }
        Matrix &matrix;
        size_t index;
        std::vector<std::reference_wrapper<int>> references;
    };

    template <typename InputIterator>
    void appendRow(InputIterator begin, InputIterator end)
    {
        auto [quotient, remainder] = std::div(end - begin, ncols);
        if (remainder != 0)
            throw std::invalid_argument("Tried to append row of size not multiple of ncols.");
        std::for_each(begin, end, [this](auto elem)
                      { data.push_back(elem); });
        nrows += quotient;
    }

    template <typename InputIterator>
    void appendColumn(InputIterator begin, InputIterator end)
    {
        auto [quotient, remainder] = std::div(end - begin, nrows);
        if (remainder != 0)
            throw std::invalid_argument("Tried to append column of size not multiple of nrows.");
        for (int k = 0; k < quotient; k++)
        {
            size_t insertionOffset = 0;
            for (size_t i = 1; i <= nrows; i++)
            {
                data.insert(data.begin() + ncols * i + insertionOffset++, (*begin)++);
            }
            ncols++;
        }
    }

    void appendRow(std::vector<int> vec) { appendRow(vec.begin(), vec.end()); }

    void appendColumn(std::vector<int> vec) { appendColumn(vec.begin(), vec.end()); }

    bool empty() { return data.empty(); }

    void removeRow(size_t index)
    {
        data.erase(data.begin() + index * ncols, data.begin() + (index + 1) * ncols);
        nrows--;
    }

    void removeRows(std::set<size_t> rows)
    {
        size_t rowIndexOffset = 0;
        for (const auto &rowIndex : rows)
            removeRow(rowIndex - rowIndexOffset++);
    }

    void removeColumn(size_t index)
    {
        auto begin = data.begin();
        size_t deletionOffset = 0;
        for (size_t i = 0; i < nrows; i++)
        {
            data.erase(begin + index + i * ncols - deletionOffset++);
        }
        ncols--;
    }

    void removeColumns(std::set<size_t> columns)
    {
        size_t columnIndexOffset = 0;
        for (const auto &columnIndex : columns)
            removeColumn(columnIndex - columnIndexOffset++);
    }

    int &at(size_t k)
    {
        if (k >= data.size())
            throw std::invalid_argument("Tried to access beyond number of elements.");
        return data[k];
    }

    int &at(size_t i, size_t j)
    {
        if (i >= nrows)
            throw std::invalid_argument("Tried to access beyond number of rows.");
        if (j >= ncols)
            throw std::invalid_argument("Tried to acess beyond number of columns.");
        return data[i * ncols + j];
    }

    Row operator[](size_t i)
    {
        if (i >= nrows)
            throw std::invalid_argument("Tried to access beyond number of rows.");
        return row(i);
    }

    Row row(size_t i)
    {
        if (i >= nrows)
            throw std::invalid_argument("Tried to access beyond number of rows.");
        return Row(*this, i);
    }

    Column col(size_t j)
    {
        if (j >= ncols)
            throw std::invalid_argument("Tried to access beyond number of columns.");
        return Column(*this, j);
    }

    friend std::ostream &operator<<(std::ostream &os, Matrix &matrix)
    {
        os << "\n";
        for (size_t i = 0; i < matrix.nrows; i++)
        {
            for (size_t j = 0; j < matrix.ncols; j++)
                os << matrix[i][j] << " ";
            os << "\n";
        }
        os << "\n";
        return os;
    }

    size_t nrows, ncols;
    std::vector<int> data;
};
