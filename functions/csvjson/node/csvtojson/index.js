const csvtojson = require('csvtojson');

exports.handler = async (event, context) => {
    // Assuming the CSV data is passed as a string under 'csv_string' in the event
    const csvString = event.csv_string;
    
    if (!csvString) {
        return {
            statusCode: 400,
            body: JSON.stringify('No CSV data provided')
        };
    }
    
    try {
        // Convert CSV string to JSON
        const jsonArray = await csvtojson().fromString(csvString);
        
        // Convert the JSON array to a JSON string to conform to the Lambda response body requirements
        const jsonStr = JSON.stringify(jsonArray);
        
        return {
            statusCode: 200,
            body: jsonStr
        };
    } catch (error) {
        console.error('Error converting CSV to JSON:', error);
        return {
            statusCode: 500,
            body: JSON.stringify('Error processing your request')
        };
    }
};
