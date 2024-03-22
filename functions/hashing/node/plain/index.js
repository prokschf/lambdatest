exports.handler = async (event) => {
    try {
        const matrix = event.matrix;

        // Validate the matrix is square
        if (!matrix.every(row => row.length === matrix.length)) {
            return response(400, "Matrix must be square.");
        }

        const size = matrix.length;
        const inverse = invertMatrix(matrix, size);

        if (!inverse) {
            return response(400, "Matrix is not invertible.");
        }

        return response(200, { inverseMatrix: inverse });
    } catch (error) {
        console.error(error);
        return response(500, "An error occurred during matrix inversion.");
    }
};

function invertMatrix(matrix, size) {
    // Create the augmented matrix: original + identity
    for (let i = 0; i < size; i++) {
        matrix[i] = [...matrix[i], ...Array(size).fill(0).map((_, j) => (i === j ? 1 : 0))];
    }

    // Apply Gaussian elimination
    for (let i = 0; i < size; i++) {
        // Find the pivot row
        let maxRow = i;
        for (let j = i + 1; j < size; j++) {
            if (Math.abs(matrix[j][i]) > Math.abs(matrix[maxRow][i])) {
                maxRow = j;
            }
        }

        // Swap the maximum row with the current row
        if (i !== maxRow) {
            const temp = matrix[i];
            matrix[i] = matrix[maxRow];
            matrix[maxRow] = temp;
        }

        // Make all rows below this one 0 in the current column
        for (let j = i + 1; j < size; j++) {
            const c = -matrix[j][i] / matrix[i][i];
            for (let k = i; k < size * 2; k++) {
                if (i === k) {
                    matrix[j][k] = 0;
                } else {
                    matrix[j][k] += c * matrix[i][k];
                }
            }
        }
    }

    // Solve equation Ax=b for an upper triangular matrix A
    for (let i = size - 1; i >= 0; i--) {
        for (let j = i - 1; j >= 0; j--) {
            const c = -matrix[j][i] / matrix[i][i];
            for (let k = size; k < size * 2; k++) {
                matrix[j][k] += c * matrix[i][k];
            }
        }
    }

    // Normalize the diagonal
    for (let i = 0; i < size; i++) {
        const c = matrix[i][i];
        for (let j = size; j < size * 2; j++) {
            matrix[i][j] /= c;
        }
    }

    // Extract the right half of the augmented matrix as the inverse
    const inverse = matrix.map(row => row.slice(size, size * 2));

    return inverse;
}

function response(statusCode, body) {
    return {
        statusCode,
        body: JSON.stringify(body),
        headers: {
            "Content-Type": "application/json"
        }
    };
}
