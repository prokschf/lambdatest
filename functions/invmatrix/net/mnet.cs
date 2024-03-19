using Amazon.Lambda.Core;
using MathNet.Numerics.LinearAlgebra;
using System;
using System.Text.Json;

[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]
namespace MyLambdaFunctions
{
    public class Function
    {
        public string FunctionHandler(MatrixInput input, ILambdaContext context)
        {
            // Log input for debugging
            context.Logger.LogLine($"Received input: {JsonSerializer.Serialize(input)}");

            // Explicitly check for null values
            if (input == null)
            {
                throw new ArgumentNullException(nameof(input), "Input is null.");
            }
            
            if (input.Matrix == null)
            {
                throw new ArgumentNullException(nameof(input.Matrix), "Matrix data is null.");
            }

            // Proceed with the assumption that input is not null
            var matrix = Matrix<double>.Build.DenseOfRowArrays(input.Matrix);
            var inverseMatrix = matrix.Inverse();
            return JsonSerializer.Serialize(inverseMatrix);
        }
    }

    public class MatrixInput
    {
        public double[][] Matrix { get; set; }
    }
}

