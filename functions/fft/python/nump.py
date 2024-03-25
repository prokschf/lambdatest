import json
import numpy as np

def lambda_handler(event, context):
    # Assuming the input data is passed as a list of numbers under 'data'
    data = event.get('data')
    
    if not data:
        return {
            'statusCode': 400,
            'body': json.dumps('No data provided')
        }
    
    # Convert the data to a NumPy array
    np_data = np.array(data)
    
    # Perform FFT
    fft_result = np.fft.fft(np_data)
    
    # Convert the complex FFT result to a list of strings for JSON serialization
    fft_result_str = [str(x) for x in fft_result]
    
    return {
        'statusCode': 200,
        'body': json.dumps({'fft_result': fft_result_str})
    }
