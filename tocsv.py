import json
import csv

def detailed_convert_json_file_to_csv(input_json_file_path, output_csv_file_path):
    """
    Read JSON data from a file, deeply convert it into CSV format considering tasks, languages, and libraries,
    and save it to another file.

    Parameters:
    - input_json_file_path: The file path of the input JSON file.
    - output_csv_file_path: The file path where the output CSV should be saved.
    """
    # Read the JSON data from the input file
    with open(input_json_file_path, 'r') as json_file:
        json_data = json.load(json_file)

    # Prepare to open the CSV file for writing
    with open(output_csv_file_path, mode='w', newline='') as file:
        # Define the CSV column names
        fieldnames = ['Task', 'Language', 'Library', 'Payload', 'Memory_Used_MB_Average', 'Memory_Used_MB_Median',
                      'Memory_Used_MB_Std_Dev', 'Billed_Duration_MS_Average', 'Billed_Duration_MS_Median',
                      'Billed_Duration_MS_Std_Dev', 'Billed_Duration_Init_Value']
        
        # Create a CSV DictWriter object
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Iterate through each task
        for task_name, task_data in json_data.items():
            # Iterate through each language within the task
            for language_name, language_data in task_data.items():
                # Iterate through each library within the language
                for library_name, library_data in language_data.items():
                    # Now, we are at the "plain" level in your given JSON structure
                    for item in library_data:
                        row = {
                            'Task': task_name,
                            'Language': language_name,
                            'Library': library_name,
                            'Payload': item['payload'],
                            'Memory_Used_MB_Average': item['memory_used_mb']['average'],
                            'Memory_Used_MB_Median': item['memory_used_mb']['median'],
                            'Memory_Used_MB_Std_Dev': item['memory_used_mb']['std_dev'],
                            'Billed_Duration_MS_Average': item['billed_duration_ms']['average'],
                            'Billed_Duration_MS_Median': item['billed_duration_ms']['median'],
                            'Billed_Duration_MS_Std_Dev': item['billed_duration_ms']['std_dev'],
                            'Billed_Duration_Init_Value': item['billed_duration_init']['value']
                        }
                        writer.writerow(row)

# Example usage:
# detailed_convert_json_file_to_csv('path/to/lambda_stats.json', 'path/to/your/output.csv')

# Example usage:
detailed_convert_json_file_to_csv('lambda_stats.json', 'output.csv')
