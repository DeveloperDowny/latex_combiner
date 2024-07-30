import os
import re

# Define the resume type you want to use
RESUME_TYPE = 'fs'  # Change this to the desired case
base_dir = os.path.dirname(os.path.abspath(__file__), "latex_project")

def replace_input(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    def process_input(match):
        input_file = match.group(1)
        input_file = input_file.replace("/", os.sep)
        #os.path.dirname(file_path),
        input_file_path = os.path.join( input_file + '.tex')
        if os.path.exists(input_file_path):
            return replace_input(input_file_path)
        else:
            return f'% Warning: File {input_file_path} not found\n'

    # Replace all \input{...} commands
    content = re.sub(r'\\input{([^}]+)}', process_input, content)

    def process_ifstrequalcase(match):
        cases = match.group(1)
        default_case = match.group(2)
        
        case_match = re.search(r'{' + re.escape(RESUME_TYPE) + r'}\s*{([^}]+)}', cases)
        if case_match:
            return re.sub(r'\\input{([^}]+)}', process_input, case_match.group(1))
        else:
            return re.sub(r'\\input{([^}]+)}', process_input, default_case)

    # Replace \IfStrEqCase{...}{...} with the chosen case or default
    content = re.sub(r'\\IfStrEqCase{[^}]+}{([^[]+)}\[\s*([^]]+)\s*\]', process_ifstrequalcase, content, flags=re.DOTALL)

    return content

def main():
    main_file_path = 'main.tex'  # Path to your main LaTeX file
    combined_content = replace_input(main_file_path)

    with open('combined_main.tex', 'w') as output_file:
        output_file.write(combined_content)

if __name__ == '__main__':
    main()
