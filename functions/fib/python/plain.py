import json

def lambda_handler(event, context):
    # Parse the input to extract 'len'
    sequence_length = event.get('len', 0)
    
    # Validate input
    if not isinstance(sequence_length, int) or sequence_length <= 0:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid input for sequence length')
        }
    
    # Calculate the Fibonacci sequence
    fib_sequence = calculate_fibonacci(sequence_length)
    
    # Return the Fibonacci sequence
    return {
        'statusCode': 200,
        'body': json.dumps(fib_sequence)
    }

def calculate_fibonacci(length):
    """
    Generates a list of Fibonacci numbers up to the specified length.
    
    :param length: The number of Fibonacci numbers to generate.
    :return: A list containing the Fibonacci sequence up to the specified length.
    """
    if length == 1:
        return [0]
    elif length == 2:
        return [0, 1]
    
    sequence = [0, 1]
    while len(sequence) < length:
        sequence.append(sequence[-1] + sequence[-2])
    
    return sequence
