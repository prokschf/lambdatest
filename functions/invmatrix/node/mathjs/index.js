
const math = require('mathjs');
exports.handler = async (event) => {
    try {
      // When invoked directly through the SDK, the event is the payload.
      const payload = event.body ? JSON.parse(event.body) : event;
  
      // Extract the matrix directly from the payload or its `matrix` property
      const matrix = payload.matrix || payload;
  
      // Ensure the matrix is provided
      if (!matrix || !Array.isArray(matrix) || matrix.length === 0) {
        return {
          statusCode: 400,
          body: JSON.stringify({ message: "Matrix not provided or invalid." })
        };
      }
  
      // Calculate the inverse of the matrix
      const inverseMatrix = math.inv(matrix);
  
      // Return the inverse matrix
      return {
        statusCode: 200,
        body: JSON.stringify({ inverseMatrix }),
        headers: {
          "Content-Type": "application/json"
        }
      };
    } catch (error) {
      // Handle errors (e.g., matrix not invertible)
      console.error(error);
      return {
        statusCode: 500,
        body: JSON.stringify({ message: "An error occurred during matrix inversion." })
      };
    }
  };
  