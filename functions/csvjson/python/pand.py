import json
import pandas as pd
from io import StringIO

def lambda_handler(event, context):
    # Assuming the CSV data is passed as a string under 'csv_string' in the event
    csv_string = event.get('csv_string')
    
    if not csv_string:
        return {
            'statusCode': 400,
            'body': json.dumps('No CSV data provided')
        }
    
    # Convert CSV string to DataFrame
    csv_data = StringIO(csv_string)
    df = pd.read_csv(csv_data)
    
    # Convert DataFrame to JSON
    json_data = df.to_json(orient='records')
    
    # You can now process the JSON data further or return it
    return {
        'statusCode': 200,
        'body': json_data
    }
