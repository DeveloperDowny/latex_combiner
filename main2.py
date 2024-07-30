import os
import re
import logging
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileProcessor(ABC):
    @abstractmethod
    def process(self, input_path: str, output_path: str):
        pass

class Preprocessor(FileProcessor):
    def __init__(self, resume_type: str):
        self.resume_type = resume_type

    def process(self, input_path: str, output_path: str):
        try:
            with open(input_path, "r", encoding='utf-8') as file:
                text = file.read()
                text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)
                text = text.replace("\n", "<newline>")

            pattern = rf'\\IfStrEqCase{{[^}}]+}}{{(.*?){{{self.resume_type}}}(.*?)}}'
            matches = re.findall(pattern, text, re.DOTALL)
            
            if matches:
                content = matches[0][1]  # Extract content for the specified resume type
                inp_list = content.split("<newline>")
                
                with open(output_path, "w", encoding='utf-8') as file:
                    for inp in inp_list:
                        inp = inp.strip()
                        if inp and not inp.startswith("%"):
                            if inp.startswith("\\input"):
                                file.write(inp + "\n")
                
                logger.info(f"Preprocessor: Successfully processed {input_path} to {output_path}")
            else:
                logger.warning(f"Preprocessor: Resume type '{self.resume_type}' not found in {input_path}")
        
        except IOError as e:
            logger.error(f"Preprocessor: Error processing file {input_path}: {str(e)}")

class Preprocessor2(FileProcessor):
    def process(self, input_path: str, output_path: str):
        try:
            with open(input_path, 'r', encoding='utf-8') as file:
                input_text = file.read()

            pattern = r'\\IfStrEqCase{[^}]+}{(.*)}'
            
            try:
                with open(output_path, 'r', encoding='utf-8') as file:
                    replacement_text = file.read()
            except FileNotFoundError:
                logger.error(f"Preprocessor2: File '{output_path}' not found.")
                return
            except IOError:
                logger.error(f"Preprocessor2: Unable to read file '{output_path}'.")
                return

            result = re.sub(pattern, replacement_text, input_text, flags=re.DOTALL)
            
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(result)
            
            logger.info(f"Preprocessor2: Successfully processed {input_path} to {output_path}")
        
        except IOError as e:
            logger.error(f"Preprocessor2: Error processing file {input_path}: {str(e)}")

class MainProcessor(FileProcessor):
    def __init__(self, resume_type: str, base_dir: str):
        self.resume_type = resume_type
        self.base_dir = base_dir

    def process(self, input_path: str, output_path: str):
        try:
            combined_content = self._replace_input(input_path)
            
            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write(combined_content)
            
            logger.info(f"MainProcessor: Successfully processed {input_path} to {output_path}")
        
        except IOError as e:
            logger.error(f"MainProcessor: Error processing file {input_path}: {str(e)}")

    def _replace_input(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        content = re.sub(r'%.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'\\input{([^}]+)}', self._process_input, content)
        content = re.sub(
            r'\\IfStrEqCase{[^}]+}{([^[]+)}\[\s*([^]]+)\s*\]', 
            self._process_ifstrequalcase, 
            content, 
            flags=re.DOTALL
        )

        return content

    def _process_input(self, match):
        input_file = match.group(1).replace("/", os.sep)
        input_file_path = os.path.join(self.base_dir, input_file + '.tex')
        if os.path.exists(input_file_path):
            return self._replace_input(input_file_path)
        else:
            logger.warning(f"MainProcessor: File {input_file_path} not found")
            return f'% Warning: File {input_file_path} not found\n'

    def _process_ifstrequalcase(self, match):
        cases = match.group(1)
        default_case = match.group(2)
        
        case_pattern = r'\{' + re.escape(self.resume_type) + r'\}\s*\{([^}]*)\}'
        case_match = re.search(case_pattern, cases)
        if case_match:
            return re.sub(r'\\input{([^}]+)}', self._process_input, case_match.group(1))
        else:
            return re.sub(r'\\input{([^}]+)}', self._process_input, default_case)

class ResumeProcessor:
    def __init__(self, resume_type: str, base_dir: str):
        self.resume_type = resume_type
        self.base_dir = base_dir
        self.preprocessor = Preprocessor(resume_type)
        self.preprocessor2 = Preprocessor2()
        self.main_processor = MainProcessor(resume_type, base_dir)

    def process(self):
        try:
            input_path = os.path.join(self.base_dir, 'main.tex')
            intermediate_path = os.path.join(self.base_dir, 'out2.tex')
            processed_path = os.path.join(self.base_dir, 'main_processed.tex')
            output_path = os.path.join(self.base_dir, 'combined_main.tex')

            self.preprocessor.process(input_path, intermediate_path)
            self.preprocessor2.process(input_path, processed_path)
            self.main_processor.process(processed_path, output_path)

            logger.info("Resume processing completed successfully")
        
        except Exception as e:
            logger.error(f"An error occurred during resume processing: {str(e)}")

if __name__ == '__main__':
    RESUME_TYPE = 'fs'  # Change this to the desired case
    BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "latex_project")
    
    processor = ResumeProcessor(RESUME_TYPE, BASE_DIR)
    processor.process()