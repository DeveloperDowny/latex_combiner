import os
import re

class TexCombiner:
    def __init__(self, resume_type='back', base_dir=None):
        self.RESUME_TYPE = resume_type
        self.base_dir = base_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "latex_project")

    def preprocess_1(self):
        pattern = r'\{'+self.RESUME_TYPE+r'\}(.*)'
        text = ""
        with open(os.path.join(self.base_dir, "main.tex"), "r") as file:
            text = file.read()
            text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)
            text = text.replace("\n", "<newline>")

        matches = re.findall(pattern, text)
        if matches:
            inp_list = matches[0].split("<newline>")
            # find index of {fs} and remove left of it
            for i in range(len(inp_list)):
                if inp_list[i].strip() == "{"+self.RESUME_TYPE+"}":
                    inp_list = inp_list[i+1:]
                    break
            with open(os.path.join(self.base_dir, "out2.tex"), "w") as file:
                for inp in inp_list:
                    if "}" in inp and "{" in inp and "input" not in inp:
                        break
                    if inp.strip() == "":
                        continue
                    if inp.strip().startswith("%"):
                        continue
                    if inp.strip().startswith("\\input"):
                        file.write(inp.strip() + "\n")

    def preprocess_2(self):
        input_text = ""
        with open(os.path.join(self.base_dir, 'main.tex'), 'r') as file:
            input_text = file.read()
        
        file_path = os.path.join(self.base_dir, 'out2.tex')

        def replace_block_with_file(input_text, file_path):
            # Pattern to match the entire \IfStrEqCase block
            pattern = r'\\IfStrEqCase{(.*)% Default case'

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
        with open(os.path.join(self.base_dir, 'main_processed.tex'), 'w') as file:
            file.write(output_text)

    def replace_input(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()

        def process_input(match):
            input_file = match.group(1)
            input_file = input_file.replace("/", os.sep)
            input_file_path = os.path.join(self.base_dir, input_file + '.tex')
            if os.path.exists(input_file_path):
                return self.replace_input(input_file_path)
            else:
                return f'% Warning: File {input_file_path} not found\n'

        def process_ifstrequalcase(match):
            cases = match.group(1)
            default_case = match.group(2)
            
            # Match the desired case
            case_pattern = r'\{' + re.escape(self.RESUME_TYPE) + r'\}\s*\{([^}]*)\}'
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

        return content

    def final_process(self):
        main_file_path = os.path.join(self.base_dir, 'main_processed.tex')  # Path to your main LaTeX file
        combined_content = self.replace_input(main_file_path)

        with open(os.path.join(self.base_dir, 'combined_main.tex'), 'w') as output_file:
            output_file.write(combined_content)

    def run_pipeline(self):
        self.preprocess_1()
        self.preprocess_2()
        self.final_process()

# Example usage:
if __name__ == '__main__':
    combiner = TexCombiner()
    combiner.run_pipeline()