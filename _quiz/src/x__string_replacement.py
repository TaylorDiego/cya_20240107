
# Example Python code to open a text file, replace three different strings with '\n\n', and save the modified content
# to a new file "output.txt"

# Define the path to the original file
file_path = 'raw_for_parse.txt'  # Replace with your file path

# Strings to be replaced
string1 = "string_to_replace_1"
string2 = "string_to_replace_2"
string3 = "string_to_replace_3"

# Open the original file and read its content
with open(file_path, 'r') as file:
    content = file.read()

# Replace the specified strings with '\n\n'
content = content.replace(string1, '\n\n')
content = content.replace(string2, '\n\n')
content = content.replace(string3, '\n\n')

# Define the path to the new file "output.txt"
new_file_path = 'output.txt'

# Write the modified content to the new file
with open(new_file_path, 'w') as new_file:
    new_file.write(content)
