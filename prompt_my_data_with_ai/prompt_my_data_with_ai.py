import os
from openai import AzureOpenAI
import subprocess
import json
import argparse

# you can use "where py" to get the correct path to your py executable
python_executable = 'C:\\Users\\vcrechet\\AppData\\Local\\Programs\\Python\\Launcher\\py.exe'

def load_config(config_path: str = "config.json") -> dict:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config file: {e}")
        return {}

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
        print(f"Error creating Azure OpenAI client: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Perform AI-powered data analysis on files")
    parser.add_argument("--config", type=str, default="config.json", help="Path to the config.json file")
    args = parser.parse_args()

    config_path = args.config
    config = load_config(config_path)
    client = create_azure_openai_client(config_path)
    
    if not client:
        print("Failed to create Azure OpenAI client. Exiting.")
        return
    
    try:
        continue_data_analysis = True
        while continue_data_analysis:
            file_name = ask_question("\nDo you want to perform data analysis on a file? If yes enter the name of the file, otherwise enter no\n")
            if file_name.lower() not in ['no', 'n']:
                keep_asking = True
                while keep_asking:
                    prompt = ask_question("\nDo you have a question about the data? If yes enter the question, otherwise enter no\n")
                    if prompt.lower() not in ['no', 'n']:
                        if prompt.lower().startswith("what do you think"):
                            perform_advanced_data_analysis(client, file_name, prompt, config)
                        elif prompt.lower().startswith("any interesting insights about this document?"):
                            perform_ai_selected_data_analysis(client, file_name, prompt, config)
                        else:
                            perform_data_analysis(client, file_name, prompt, config)
                    else:
                        keep_asking = False
            else:
                continue_data_analysis = False
    except Exception as e:
        print(f"Error in main: {e}")    
 
def perform_data_analysis(client, file_name, prompt, config):
    try:
        completion = execute_prompt_with_instructions(
            client,
            create_data_prompt_instructions(file_name),
            prompt,
            config)
        if completion:
            script_content = completion.choices[0].message.content
            result = run_generated_script(script_content)
            if result:
                print(f"\n{result}")
    except Exception as e:
        print(f"Error in perform_data_analysis: {e}")
    
def perform_advanced_data_analysis(client, file_name, prompt, config):
    try:
        completion = execute_prompt_with_instructions(
            client,
            create_advanced_data_first_prompt_instructions(file_name),
            prompt,
            config)
        script_content = completion.choices[0].message.content
        data_analysis_result = run_generated_script(script_content)
        completion = execute_prompt_with_instructions(
            client,
            create_advanced_data_second_prompt_instructions(file_name),
            prompt + "\nThe statistics to provide comment about are the following\n" + data_analysis_result,
            config)
        print(f"\n{completion.choices[0].message.content}")
    except Exception as e:
        print(f"Error in perform_advanced_data_analysis: {e}")    

def perform_ai_selected_data_analysis(client, file_name, prompt, config):
    try:
        completion = execute_prompt_with_instructions(
            client,
            create_ai_selected_data_prompt_instructions(file_name),
            prompt,
            config)
        script_content = completion.choices[0].message.content
        data_analysis_result = run_generated_script(script_content)
        completion = execute_prompt_with_instructions(
            client,
            create_advanced_data_second_prompt_instructions(file_name),
            prompt + "\nThe statistics to provide comment about are the following\n" + data_analysis_result,
            config)
        print(f"\n{completion.choices[0].message.content}")
    except Exception as e:
        print(f"Error in perform_ai_selected_data_analysis: {e}")    
        
   
def execute_prompt_with_instructions(client, prompt_instructions, prompt, config):
    try:
        model = config.get("model", "gpt-4o")
        messages = [
            {"role": "system", "content": prompt_instructions},
            {"role": "user", "content": prompt}
        ]
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        return completion
    except Exception as e:
        print(f"Error calling chat completion API: {e}")
        return None
        
def create_data_prompt_instructions(data_file_name: str) -> str:
    prompt_instructions = (
        f"I have a file called {data_file_name} which contains a list of records. "
        "Based on the prompt you will provide python code to perform specific data analysis on this document. "
        "Only provide the code, do not provide explanation about the code because I want to execute directly "
        "what you will provide. The code should start with import. No '''python and should not end with '''. "
        "The code should finish with a print statement which displays the requested statistics in natural "
        "language format. The code should not contain plot or chart generation."
    )
    prompt_instructions += give_extra_context(data_file_name)
    return prompt_instructions  


def create_ai_selected_data_prompt_instructions(data_file_name: str) -> str:
    prompt_instructions = (
        "I have a file which contains a list of records. "
        "Based on the specific content of the file, I would like you to select 3 statistics which are worth exploring. "
        "Provide the python code which can be used to compute the 3 statistics on this file. "
        "Only provide the code, do not provide explanation about the code because I want to execute directly what you will provide. "
        "The code should start with import. No '''python and should not end with '''. "
        "The code should contain print statements so that the output of the python code displays, in a natural language, the statistics but also why it was interesting to look at these statistics. "
        "The code should not contain plot or chart generation."
    )
    prompt_instructions += give_extra_context(data_file_name)
    return prompt_instructions 

  
       
def create_advanced_data_first_prompt_instructions(data_file_name: str) -> str:
    prompt_instructions = (
        f"I have a file called {data_file_name} which contains a list of records. "
        "Based on the prompt you will provide python code to perform specific data analysis on this document. "
        "Only provide the code, do not provide explanation about the code because I want to execute directly what you will provide. "
        "The code should start with import. No '''python and should not end with '''. "
        "The code should finish with a print statement which displays the required statistics in natural language format. "
        "The code should not contain plot or chart generation."
    )
    prompt_instructions += give_extra_context(data_file_name)
    return prompt_instructions   

def create_advanced_data_second_prompt_instructions(data_file_name: str) -> str:
    prompt_instructions = (
        "I have extracted some statistics from a data file. I will provide the statistics extracted from the data file. Review the statistics "
        "and provide comments about these statistics based on what you know about. The objective is for example to detect unusual patterns. "
        "Limit your answer to 350 characters. Do not use '**' for title of bullet points."
    )
    prompt_instructions += give_extra_context(data_file_name)
    return prompt_instructions      
        

def give_extra_context(data_file_name: str) -> str:
    try:
        first10lines = ""
        with open(data_file_name, encoding="utf-8") as f:
            for n in range(1, 11):
                first10lines += f.readline()
        return f"\nThe file is called {data_file_name} and the first 10 lines of the data file are the following:\n{first10lines}"
    except Exception as e:
        print(f"Error reading file context: {e}")
        return f"\nThe file is called {data_file_name}." 

def remove_python_header_and_footer(script_content: str) -> str:
    lines = script_content.split('\n')
    
    # Check if the first line is "```python"
    if lines and lines[0].strip() == "```python":
        # Remove the first and last lines
        lines = lines[1:-1]
    
    # Join the remaining lines back into a single string
    return '\n'.join(lines)

def run_generated_script(script_content: str) -> str:
    try:
        script_file = 'generatedscript.py'
        script_content = remove_python_header_and_footer(script_content)
        # Write the content to generatedscript.py
        with open(script_file, 'w', encoding='utf-8') as script:
            script.write(script_content)

        # Execute generatedscript.py and capture its output
        result = subprocess.run([python_executable, script_file], capture_output=True, text=True)

        # Return the output of generatedscript.py
        if result.returncode != 0:
            print(f"Script execution error: {result.stderr}")
            return ""
        return result.stdout
    except Exception as e:
        print(f"Error running generated script: {e}")
        return ""


def ask_question(question: str) -> str:
    return input(question)

        
if __name__ == "__main__":
    main()