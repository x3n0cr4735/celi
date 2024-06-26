import json

# Read the JSON from a file
with open('output/gpt/alpaca_eval_auto_output.json', 'r') as file:
    data = json.load(file)

# Convert to list of dicts, sort by key, and keep only specified keys
result = []
for key in sorted(data.keys(), key=int):
    item = data[key]
    filtered_item = {
        'instruction': item['instruction'],
        'output': item['final_response'],
        'generator': 'celi'
    }
    result.append(filtered_item)

# Write the result to a new JSON file
with open('output/gpt/alpaca_eval_auto_output_list.json', 'w') as file:
    json.dump(result, file, indent=2)

# Print the result (optional)
print(json.dumps(result, indent=2))