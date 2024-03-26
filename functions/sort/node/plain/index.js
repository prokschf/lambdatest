
exports.handler = async (event, context) => {
    // The event is expected to directly contain the list under 'list'
    const numList = event.list;
    
    // Validate the input is an array
    if (!Array.isArray(numList)) {
        return {
            statusCode: 400,
            body: JSON.stringify('Input is not a list')
        };
    }
    
    // Sort the list
    const sortedList = numList.sort((a, b) => a - b);
    
    // Return the sorted list
    return {
        statusCode: 200,
        body: JSON.stringify(sortedList)
    };
};
