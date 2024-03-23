using Amazon.Lambda.Core;
using System;
using System.Collections.Generic;
using System.Linq;

[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace KnnLambdaFunction
{
    public class Function
    {
        public string FunctionHandler(KnnInput input, ILambdaContext context)
        {
           context.Logger.LogLine($"Received input: {input.Input_Embedding}");            
            if (input == null)
            {
                throw new ArgumentNullException(nameof(input), "Input is null.");
            }

            if (input.Embeddings == null || !input.Embeddings.Any())
            {
                throw new ArgumentNullException(nameof(input.Embeddings), "Embeddings are null or empty.");
            }

            if (input.Input_Embedding == null)
            {
                throw new ArgumentNullException(nameof(input.Input_Embedding), "Input embedding is null.");
            }            
            // Convert embeddings to Points
            var points = input.Embeddings.Select(e => new Point { Features = e }).ToList();

            var neighbors = FindNeighbors(points, input.Input_Embedding, input.K);
            var mostCommonLabel = "N/A"; // Assuming you might want to classify or do something with the neighbors

            return $"Found {neighbors.Count} nearest neighbors"; // Modify as needed for your application
        }

        private List<Point> FindNeighbors(List<Point> points, double[] queryPoint, int k)
        {
            if (points == null || queryPoint == null) throw new ArgumentNullException("points or queryPoint cannot be null.");

            return points.Select(point => new Point
                {
                    Features = point.Features,
                    Distance = CalculateDistance(point.Features, queryPoint)
                })
                .OrderBy(p => p.Distance)
                .Take(k)
                .ToList();
        }

        private double CalculateDistance(double[] features, double[] queryPoint)
        {
            return Math.Sqrt(features.Zip(queryPoint, (f, q) => Math.Pow(f - q, 2)).Sum());
        }
    }

    public class KnnInput
    {
        public List<double[]> Embeddings { get; set; }
        public double[] Input_Embedding { get; set; }
        public int K { get; set; }
    }

    public class Point
    {
        public double[] Features { get; set; }
        public double Distance { get; set; }
    }
}
