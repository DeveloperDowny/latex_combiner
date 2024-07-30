import os
import re

# Define the resume type you want to use
RESUME_TYPE = 'fs'  # Change this to the desired case
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "latex_project")

def replace_input(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    def process_input(match):
        input_file = match.group(1)
        input_file = input_file.replace("/", os.sep)
        input_file_path = os.path.join(base_dir, input_file + '.tex')
        if os.path.exists(input_file_path):
            return replace_input(input_file_path)
        else:
            return f'% Warning: File {input_file_path} not found\n'

    def process_ifstrequalcase(match):
        cases = match.group(1)
        default_case = match.group(2)
        
        # Match the desired case
        case_pattern = r'\{' + re.escape(RESUME_TYPE) + r'\}\s*\{([^}]*)\}'
        case_match = re.search(case_pattern, cases)
        if case_match:
            return re.sub(r'\\input{([^}]+)}', process_input, case_match.group(1))
        else:
            return re.sub(r'\\input{([^}]+)}', process_input, default_case)

    # Replace all \input{...} commands
    content = re.sub(r'%.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'\\input{([^}]+)}', process_input, content)

    # Replace \IfStrEqCase{...}{...} with the chosen case or default
    content = re.sub(
        r'\\IfStrEqCase{[^}]+}{([^[]+)}\[\s*([^]]+)\s*\]', 
        process_ifstrequalcase, 
        content, 
        flags=re.DOTALL
    )

    # Remove comments from content before further processing

    return content

def main():
    main_file_path = os.path.join(base_dir, 'main_processed.tex')  # Path to your main LaTeX file
    combined_content = replace_input(main_file_path)

    with open(os.path.join(base_dir, 'combined_main.tex'), 'w') as output_file:
        output_file.write(combined_content)

if __name__ == '__main__':
    main()
