using System;
using System.Security.Cryptography;
using System.Text;
using Amazon.Lambda.Core;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace Sha256Function
{
    public class Function
    {
        public string FunctionHandler(Request request, ILambdaContext context)
        {
            try
            {
                if (string.IsNullOrEmpty(request?.InputString))
                {
                    return "Error: inputString not provided";
                }

                using (SHA256 sha256Hash = SHA256.Create())
                {
                    byte[] bytes = sha256Hash.ComputeHash(Encoding.UTF8.GetBytes(request.InputString));

                    StringBuilder builder = new StringBuilder();
                    for (int i = 0; i < bytes.Length; i++)
                    {
                        builder.Append(bytes[i].ToString("x2"));
                    }
                    return builder.ToString();
                }
            }
            catch (Exception e)
            {
                context.Logger.LogLine($"Exception: {e.Message}");
                return null;
            }
        }
    }

    public class Request
    {
        public string InputString { get; set; }
    }
}
