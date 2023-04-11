#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
#include <set>
#include <string>

#include "matrix.hpp"

// TO DO: remove the "remove variables" tracking variable? Superfluous?

///////////////////////
// Utility functions //
///////////////////////

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
        throw std::runtime_error("File not found. File path searched: " + filepath);
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

// Overloads the `<<` operator to allow printing of containers.
template <template <typename...> typename Container, typename valueType>
std::ostream &operator<<(std::ostream &os, const Container<valueType> &vector)
{
    os << "{ ";
    for (auto &elem : vector)
        os << elem << " ";
    os << "}";
    return os;
}

// Fills a container `c` with `n` elements, starting at `start`, with an increment of `increment`.
template <typename Container, typename valueType = size_t>
void fillRange(Container &c, valueType n, valueType start = static_cast<valueType>(0), valueType increment = static_cast<valueType>(1))
{
    valueType i = start;
    std::generate_n(std::inserter(c, c.begin()), n, [increment, &i]() mutable
                    { auto prev = i; i += increment; return prev; });
}

//////////////////////////
// Pre-processing steps //
//////////////////////////

/////////////
/// Step 1 //
/////////////

enum class Step1Output
{
    IsUnit,
    IsNotUnit,
    IsZero
};

//  Takes a matrix row as input and checks if it is a unit vector. Returns a pair consisting of a `Step1Output` and the index of the non-zero element.
std::pair<Step1Output, size_t> isUnitVector(Matrix::Row row)
{
    int sum = std::accumulate(row.begin(), row.end(), 0);
    if (sum > 1)
        return std::make_pair(Step1Output::IsNotUnit, static_cast<size_t>(-1));
    if (sum == 0)
        return std::make_pair(Step1Output::IsZero, static_cast<size_t>(-1));
    size_t variableIndex = 0;
    for (auto &j : row)
    {
        if (j != 0 && j != 1)
            throw std::runtime_error("Defective entries (not in {0, 1}) detected in data.");
        if (j)
            return std::make_pair(Step1Output::IsUnit, variableIndex);
        variableIndex++;
    }
    throw std::runtime_error("Unkown error: this step is unreachable.");
}

void removeRestrictions(Matrix &A, std::set<size_t> restrictions)
{
    A.removeRows(restrictions);
}

// Removes columns from the matrix `A` with indices in `variablesToRemove`. The remaining column indices are returned in `variablesToKeep`.
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

// The first step of pre-processing. The indices of remaining variables are stored in `keptVariables`. Returns the variables (indexes) it removed.
std::set<size_t> preprocessingStep1(Matrix &A, std::set<size_t> &keptVariables)
{
    std::set<size_t> restrictions, variables;

    for (size_t i = 0; i < A.nrows; i++)
    { // identify unit vector rows and removes them as restrictions
        auto [isUnitVectorResult, j] = isUnitVector(A.row(i));
        switch (isUnitVectorResult)
        { // identifying variables associated with those rows
        case Step1Output::IsUnit:
            variables.emplace(j);
        case Step1Output::IsZero:
            restrictions.emplace(i);
            break;
        default:
            break;
        }
    }
    removeRestrictions(A, restrictions);
    restrictions.clear();

    // look for further restrictions associated with those variables
    for (size_t j : variables)
        for (size_t i = 0; i < A.nrows; i++)
            if (A.at(i, j) == 1)
                restrictions.emplace(i);
    // and remove them
    removeRestrictions(A, restrictions);

    removeVariables(A, variables, keptVariables);

    return variables;
}

///////////////////
// Steps 2 and 3 //
///////////////////

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

// Takes a matrix `A` and returns a `multiset` of pairs where the first element is the index of a row or column in `A` and the second element is the sum of that row or column. If `LineWise` is `COLUMN_WISE`, the multiset is ordered by column sums in descending order, otherwise it's ordered by row sums in descending order.
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
        LineType line(A, idx);
        auto sum = std::accumulate(line.begin(), line.end(), 0);
        sums.emplace(std::make_pair(idx, sum));
    }
    return sums;
}

// Preprocessing routine for both steps 2 and 3 that takes a matrix and performs one step of the preprocessing algorithm by removing some rows or columns based on a criterion.
template <LINETYPE LineWise, bool IsColumn = LineWise == COLUMN_WISE>
auto preprocessingSubRoutine(Matrix &A, std::conditional_t<IsColumn, std::set<size_t> &, void *> keptVariables = nullptr)
{
    // `LineWise` is used to specialize the function to either remove columns or rows.
    using LineType = std::conditional_t<IsColumn, Matrix::Column, Matrix::Row>;
    // let's start by the lines with more "1"s
    auto sums = orderBySumDescending<LineWise>(A);
    // compare each line to one another. If row-wise mode, we mark
    // removal the rows which have others as subsets. If column-wise
    // mode, we mark the columns which are subsets of others.
    std::set<size_t> markedForRemoval;
    for (auto k = sums.begin(); k != sums.end(); k++)
    {
        for (auto l = std::next(k); l != sums.end(); l++)
        {
            LineType line_k(A, k->first);
            LineType line_l(A, l->first);
            if (isSecondSubsetOfFirst(line_k, line_l))
            {
                markedForRemoval.emplace(
                    IsColumn ? l->first : k->first);
            }
        }
    }

    // If column mode, it's step 3 and we return the removed variables
    if constexpr (IsColumn)
    {
        removeVariables(A, markedForRemoval, keptVariables);
        return markedForRemoval;
    }
    else // otherwise it's step 2 and we only report if something was done
    {
        removeRestrictions(A, markedForRemoval);
        return markedForRemoval.size() != 0;
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

////////////////////////////////
// Main preprocessing routine //
////////////////////////////////

auto preprocess(Matrix &A)
{
    // We create the variables that keep track of which columns
    // we keep, which we remove and which we select for our
    // solution after the preprocessing step
    std::set<size_t> keptVariables;
    fillRange(keptVariables, A.ncols);
    std::set<size_t> removedVariables, selectedVariables;

    bool processed = true;
    while (processed)
    {
        processed = false;
        // steps 1 and 3 return sets of variables removed.
        // removed on step 1 implies being selected
        auto step1 = preprocessingStep1(A, keptVariables);
        if (step1.size() != 0)
            processed = true;
        removedVariables.insert(step1.begin(), step1.end());
        selectedVariables.merge(step1);

        if (preprocessingStep2(A))
            processed = true;

        auto step3 = preprocessingStep3(A, keptVariables);
        if (step3.size() != 0)
            processed = true;
        removedVariables.merge(step3);
    }

    return std::make_tuple(keptVariables, removedVariables, selectedVariables);
}

////////////////////////////////////////
// Main algorithm:                    //
// Greedy minimum set cover algorithm //
////////////////////////////////////////

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

//////////////////
// Main program //
//////////////////

int main()
{
    auto cwd = std::filesystem::current_path();
    Matrix A;
    try
    {
        A = readFile(cwd.string() + "/entrada.txt");
        // I don't agree with putting a print statement on the minimumSetCoverSolveGreedy function,
        // thus I'll preprocess the matrix twice just in order to fulfill the printing requirements.
        auto B = A;
        auto [kept, removed, selected] = preprocess(A);
        auto sol = minimumSetCoverSolveGreedy(B);
        std::cout << "No. of variables remaining after preprocessing: " << kept.size()
                  << "\nNo. of restrictions remaining after preprocessing: " << A.nrows;
        std::cout << "\nFinal No. of selected variables: " << sol.size();
    }
    catch (std::exception &err)
    {
        std::cerr << err.what() << std::endl;
        return 1;
    }
    return 0;
}