import json

def lambda_handler(event, context):
    # The event is expected to directly contain the list under 'list'
    num_list = event.get('list', [])
    
    # Validate the input is a list
    if not isinstance(num_list, list):
        return {
            'statusCode': 400,
            'body': json.dumps('Input is not a list')
        }
    
    # Sort the list
    sorted_list = sorted(num_list)
    
    # Return the sorted list
    return {
        'statusCode': 200,
        'body': json.dumps(sorted_list)
    }
