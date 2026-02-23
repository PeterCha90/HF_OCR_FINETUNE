import json
import os
import sys

def remove_checked_from_jsonl(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    output_lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                if "checked" in data:
                    del data["checked"]
                output_lines.append(json.dumps(data, ensure_ascii=False))
            except json.JSONDecodeError:
                print(f"Warning: Could not decode line. Skipping.")
                output_lines.append(line)

    # Overwrite the file with modified content
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in output_lines:
            f.write(line + '\n')
            
    print(f"Successfully processed {file_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Process the active QA dataset
    files_to_process = [
        os.path.join(base_dir, 'dataset', 'jsonl', 'results_with_QA.jsonl'),
        os.path.join(base_dir, 'dataset', 'jsonl', 'results_without_QA.jsonl')
    ]
    
    for file_path in files_to_process:
        remove_checked_from_jsonl(file_path)
