import json

# Load the JSON data from the file
with open('./generated_logs (16).json', 'r') as file:
    data = json.load(file)

# Extract unique ai_model_version values
unique_ai_model_versions = set()

for entry in data:
    # Add the ai_model_version from the main entry
    unique_ai_model_versions.add(entry.get('ai_model_version'))
    
    # If there are retrain_events, check their versions
    if 'retrain_events' in entry:
        for event in entry['retrain_events']:
            version_after_retraining = event.get('retraining_details', {}).get('ai_model_version_after_retraining')
            if version_after_retraining:
                unique_ai_model_versions.add(version_after_retraining)

# Output the unique versions
print(unique_ai_model_versions)