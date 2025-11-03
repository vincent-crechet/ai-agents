import os
import logging
from openai import AzureOpenAI
import argparse
import PyPDF2
from pdfminer.high_level import extract_text


# Load config.json for endpoint and api_version
import json

def load_config(config_path: str = "config.json") -> dict:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading config file: {e}")
        return {}


def main(file_to_process: str, processing_instructions_file: str, debug: bool = False, config_path: str = "config.json") -> None:
    """
    Main function to process the file with AI based on the provided instructions.
    """
    logging.basicConfig(level=logging.INFO)
    try:
        client = create_azure_openai_client(config_path)
        if not client:
            logging.error("Failed to create Azure OpenAI client")
            return
        processing_instructions = load_processing_instructions(processing_instructions_file)
        process_file_with_processing_instructions(client, file_to_process, processing_instructions, debug, config_path)
    except Exception as e:
        logging.error(f"Error in main: {e}")
 
def process_file_with_processing_instructions(client, file_to_process: str, processing_instructions: str, debug: bool = False, config_path: str = "config.json") -> None:
    """
    Process the file with the given processing instructions.
    """
    try:
        messages = create_processing_instructions(processing_instructions)
        process_file(client, messages, file_to_process, debug, config_path)
    except Exception as e:
        logging.error(f"Error in process_file_with_processing_instructions: {e}")


def read_file_to_process(file_to_process: str, debug: bool = False) -> str:
    """
    Read the content of the file to be processed.
    """
    try:
        if file_to_process[-4:].lower() == ".pdf":
            file_content = extract_text_from_pdf(file_to_process, debug)
        else:
            file_content = read_file(file_to_process)
        return file_content
    except Exception as e:
        logging.error(f"Error in read_file_to_process: {e}")


def create_processing_instructions(processing_instructions: str) -> list:
    """
    Create processing instructions from the given instructions file.
    """
    try:
        messages = [{"role": "system", "content": processing_instructions}]
        return messages
    except Exception as e:
        logging.error(f"Error in create_processing_instructions: {e}")

def process_file(client, messages: list, file_to_process: str, debug: bool = False, config_path: str = "config.json") -> str:
    """
    Process the file content with AI using the given messages.
    """
    try:
        file_content = read_file_to_process(file_to_process, debug)
        config = load_config(config_path)
        model = config.get("model", "gpt-4o")
        result = process_file_with_ai(client, messages, file_content, model)
        logging.info(f"Result of file processing:\n{result}")
        return result
    except Exception as e:
        logging.error(f"Error in process_file: {e}")
 
# Function to interact with the GPT model
def process_file_with_ai(client, messages: list, file_content: str, model: str = "gpt-4o") -> str:
    """
    Interact with the GPT model to process the file content.
    """
    try:
        messages.append({"role": "user", "content": file_content})
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2
        )
        response = completion.choices[0].message.content
        messages.append({"role": "assistant", "content": response})
        return response
    except Exception as e:
        logging.error(f"Error in process_file_with_ai: {e}")

def load_processing_instructions(processing_instructions_file: str) -> str:
    """
    Load processing instructions from the given file.
    """
    try:
        return read_file(processing_instructions_file)
    except Exception as e:
        logging.error(f"Error in load_processing_instructions: {e}")


def delete_file(file_name: str) -> None:
    if os.path.exists(file_name):
        os.remove(file_name)

def read_file(input_file_name: str) -> str:
    with open(input_file_name, encoding="utf-8") as f:
        return f.read()

def write_file(output_file_name: str, content: str) -> None:
    with open(output_file_name, 'a', encoding="utf-8") as output_file:
        output_file.write(f"{content}\n")

def extract_text_from_pdf(pdf_path: str, debug: bool = False) -> str:
    try:
        text = extract_text(pdf_path)
        if debug:
            output_file_name = pdf_path.replace('.pdf', '.txt')
            if output_file_name != pdf_path:
                write_file(output_file_name, text)
        return text
    except Exception as e:
        logging.error(f"Error extract_text_from_pdf: {e}")
    
    


def create_azure_openai_client(config_path: str = "config.json") -> AzureOpenAI | None:
    try:
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API key environment variable 'AZURE_OPENAI_API_KEY' not found")
        config = load_config(config_path)
        azure_endpoint = config.get("azure_endpoint", "https://becopenaidev3.openai.azure.com/")
        api_version = config.get("api_version", "2024-10-21")
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint
        )
        return client
    except Exception as e:
        logging.error(f"Error creating Azure OpenAI client: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform a AI review on a file based on a text file containing the instructions")
    parser.add_argument("file_to_process", type=str, help="Path to the file to be processed template file")
    parser.add_argument("processing_instructions_file", type=str, help="Path to the file containing the instructions to process the file.")
    parser.add_argument("--debug", action="store_true", help="if set, the pdf to text conversion will be written in file with same name as pdf but with extension .txt")
    parser.add_argument("--config", type=str, default="config.json", help="Path to the config.json file containing Azure endpoint and API version.")
    args = parser.parse_args()
    main(args.file_to_process, args.processing_instructions_file, args.debug, args.config)