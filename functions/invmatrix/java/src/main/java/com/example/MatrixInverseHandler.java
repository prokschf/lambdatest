package com.example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import org.apache.commons.math3.linear.Array2DRowRealMatrix;
import org.apache.commons.math3.linear.LUDecomposition;
import org.apache.commons.math3.linear.RealMatrix;

import java.util.List;
import java.util.Map;

public class MatrixInverseHandler implements RequestHandler<Map<String, Object>, double[][]> {

    @Override
    public double[][] handleRequest(Map<String, Object> input, Context context) {
        // Extract the matrix from the input map
        List<List<Number>> matrixList = (List<List<Number>>) input.get("matrix");

        // Convert List<List<Number>> to double[][]
        double[][] matrixData = matrixList.stream()
                .map(list -> list.stream().mapToDouble(Number::doubleValue).toArray())
                .toArray(double[][]::new);

        // Perform matrix inversion
        RealMatrix matrix = new Array2DRowRealMatrix(matrixData);
        LUDecomposition luDecomposition = new LUDecomposition(matrix);
        RealMatrix inverseMatrix = luDecomposition.getSolver().getInverse();
        
        return inverseMatrix.getData();
    }
}
