import re
import json

def extract_content_between(file_path, first_start, first_end, second_start, second_end):
    with open(file_path, 'r') as file:
        content = file.read()

    first_pattern = f"{first_start}(.*?){first_end}"
    first_pass_matches = re.findall(first_pattern, content, re.DOTALL)

    second_pattern = f"{second_start}(.*?){second_end}"
    results = []
    for match in first_pass_matches:
        second_pass_matches = re.findall(second_pattern, match, re.DOTALL)
        results.extend(second_pass_matches)

    return results

def save_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    file_path = 'raw_for_parse.txt'
    first_start = '<a class="topic-curation__item-link link" href="'
    first_end = '"></a>'
    second_start = '<h4 class="topic-curation__title thread-list-block__title">'
    second_end = '</h4>'
    
    extracted_content = extract_content_between(file_path, first_start, first_end, second_start, second_end)
    
    for content in extracted_content:
        print(content)

    # Save the extracted content to a JSON file
    output_filename = 'output.json'
    save_to_json(extracted_content, output_filename)
    print(f"Extracted content saved to {output_filename}")

if __name__ == "__main__":
    main()



# import re

# def extract_content(file_path, start_tag, end_tag):
#     # Read the entire file content
#     with open(file_path, 'r') as file:
#         content = file.read()

#     # Define the regex pattern
#     pattern = f"{start_tag}(.*?){end_tag}"
    
#     # Find all matches
#     matches = re.findall(pattern, content, re.DOTALL)

#     return matches

# # Example usage
# file_path = 'raw_for_parse.htm'
# start_tag = '<a class="topic-curation__item-link link" href="'
# end_tag = '"></a>'
# extracted_content = extract_content(file_path, start_tag, end_tag)
# print(extracted_content)
