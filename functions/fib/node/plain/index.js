const AWS = require('aws-sdk');

exports.handler = async (event, context) => {
    // Parse the input to extract 'len'
    const sequenceLength = event.len || 0;
    
    // Validate input
    if (typeof sequenceLength !== 'number' || sequenceLength <= 0) {
        return {
            statusCode: 400,
            body: JSON.stringify('Invalid input for sequence length')
        };
    }
    
    // Calculate the Fibonacci sequence
    const fibSequence = calculateFibonacci(sequenceLength);
    
    // Return the Fibonacci sequence
    return {
        statusCode: 200,
        body: JSON.stringify(fibSequence)
    };
};

function calculateFibonacci(length) {
    /**
     * Generates an array of Fibonacci numbers up to the specified length.
     * 
     * @param {number} length - The number of Fibonacci numbers to generate.
     * @return {Array} An array containing the Fibonacci sequence up to the specified length.
     */
    if (length === 1) {
        return [0];
    } else if (length === 2) {
        return [0, 1];
    }
    
    const sequence = [0, 1];
    for (let i = 2; i < length; i++) {
        sequence.push(sequence[i - 1] + sequence[i - 2]);
    }
    
    return sequence;
}
