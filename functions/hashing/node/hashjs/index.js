const hash = require('hash.js');

exports.handler = async (event) => {
    // Check if the inputString is provided
    if (!event.inputString) {
        return { error: 'inputString not provided' };
    }

    // Calculate the SHA-256 hash of the input string using hash.js
    const hashOutput = hash.sha256().update(event.inputString).digest('hex');

    // Return the calculated hash
    return { sha256Hash: hashOutput };
};
