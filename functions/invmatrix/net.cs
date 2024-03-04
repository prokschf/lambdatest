using Amazon.Lambda.Core;
using MathNet.Numerics.LinearAlgebra;

[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

public class Function
{
    public Matrix<double> FunctionHandler(Matrix<double> inputMatrix, ILambdaContext context)
    {
        var inverseMatrix = inputMatrix.Inverse();
        return inverseMatrix;
    }
}
