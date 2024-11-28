import json

def calculate_percentage_with_score_1(file_path):
    """
    Reads a JSON file and calculates the percentage of entries with a score of 1.0.
    
    :param file_path: Path to the JSON file.
    :return: Percentage of entries with a score of 1.0.
    """
    try:
        # Load the JSON data
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Total entries in the JSON file
        total_entries = len(data)
        
        # Count entries with a score of 1.0
        score_1_count = sum(1 for entry in data if entry.get('Score') == 1.0)
        
        # Calculate the percentage
        if total_entries > 0:
            percentage = (score_1_count / total_entries) * 100
        else:
            percentage = 0
        
        print(f"Total entries: {total_entries}")
        print(f"Entries with Score 1.0: {score_1_count}")
        print(f"Percentage with Score 1.0: {percentage:.2f}%")
        
        return percentage
    except Exception as e:
        print(f"Error reading or processing the JSON file: {e}")
        return None

# Replace 'results.json' with the path to your JSON file
results_file = "results_gpt-4o-mini_text-embedding-ada-002_relevancy.json"
calculate_percentage_with_score_1(results_file)
