package main

import (
	"github.com/aws/aws-lambda-go/lambda"
	"gonum.org/v1/gonum/mat"
)

// Define a new struct to match the incoming JSON payload
type Input struct {
	Matrix [][]float64 `json:"matrix"`
}

// Adjust the HandleRequest function to accept the new Input struct
func HandleRequest(input Input) ([][]float64, error) {
	// Extract the matrix from the input struct
	inputMatrix := input.Matrix

	// Convert input 2D slice to Gonum Dense matrix
	r, c := len(inputMatrix), len(inputMatrix[0])
	flat := make([]float64, r*c)
	for i, row := range inputMatrix {
		copy(flat[i*c:(i+1)*c], row)
	}
	m := mat.NewDense(r, c, flat)

	var mInv mat.Dense
	err := mInv.Inverse(m)
	if err != nil {
		return nil, err
	}

	// Convert Gonum Dense matrix back to 2D slice
	invMatrix := make([][]float64, r)
	for i := range invMatrix {
		invMatrix[i] = make([]float64, c)
		for j := range invMatrix[i] {
			invMatrix[i][j] = mInv.At(i, j)
		}
	}

	return invMatrix, nil
}

func main() {
	lambda.Start(HandleRequest)
}
