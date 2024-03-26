const FFT = require('fft-js').fft;
const FFTUtil = require('fft-js').util;

exports.handler = async (event, context) => {
    // Assuming the input data is passed as a list of numbers under 'data'
    const data = event.data;

    if (!data || !Array.isArray(data) || data.length === 0) {
        return {
            statusCode: 400,
            body: JSON.stringify('No valid data provided')
        };
    }
    
    // Check if the length of data is a power of two
    const isPowerOfTwo = (n) => (Math.log2(n) % 1 === 0);
    let adjustedData = data;
    if (!isPowerOfTwo(data.length)) {
        // Calculate the next power of two
        const nextPowerOfTwo = Math.pow(2, Math.ceil(Math.log2(data.length)));
        adjustedData = [...data, ...new Array(nextPowerOfTwo - data.length).fill(0)];
    }
    
    // Convert the data to an array of complex numbers where each complex number is an array [real, imaginary]
    const complexData = adjustedData.map(real => [real, 0]);
    
    try {
        // Perform FFT
        const fftResult = FFT(complexData);
        
        // Convert the complex FFT result to a list of strings for JSON serialization
        const fftResultStr = fftResult.map(([real, imag]) => `${real} + ${imag}i`);
        
        return {
            statusCode: 200,
            body: JSON.stringify({'fft_result': fftResultStr})
        };
    } catch (error) {
        console.error('FFT processing error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify('Error processing FFT')
        };
    }
};
