import re

 

# Example usage:
input_text = r'''Your original text here, including the \IfStrEqCase block'''
with open('latex_project/main.tex', 'r') as file:
    input_text = file.read()
    
file_path = 'latex_project/out2.tex'
 

import re

def replace_block_with_file(input_text, file_path):
    # Pattern to match the entire \IfStrEqCase block
    pattern = r'\\IfStrEqCase{(.*)% Default case'
    print(pattern)

    # Read the contents of the specified file
    try:
        with open(file_path, 'r') as file:
            replacement_text = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return input_text
    except IOError:
        print(f"Error: Unable to read file '{file_path}'.")
        return input_text

    # Define a replacement function
    def replace_func(match):
        return replacement_text

    # Replace the matched block with the file contents
    result = re.sub(pattern, replace_func, input_text, flags=re.DOTALL)
    return result
  

output_text = replace_block_with_file(input_text, file_path)
print(output_text)
with open('latex_project/main_processed.tex', 'w') as file:
    file.write(output_text)