const CryptoJS = require("crypto-js");

exports.handler = async (event) => {
    // Check if the inputString is provided
    if (!event.inputString) {
        return { error: 'inputString not provided' };
    }

    // Calculate the SHA-256 hash of the input string using crypto-js
    const hash = CryptoJS.SHA256(event.inputString).toString(CryptoJS.enc.Hex);

    // Return the calculated hash
    return { sha256Hash: hash };
};
