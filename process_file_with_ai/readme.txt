Overview
--------
process_file_with_ai.py is a Python script that allows users to process a file with AI (ChatGPT 4o) based on instructions documented in another text file.

Features
--------
The script supports the following formats for the file to process:
* Plain text files with any extension.
* PDF files, which will be converted to text using the PyPDF2 library. Use the --debug option to view the result of the PDF-to-text conversion.

How It Works
------------
process_file_with_ai.py interacts with ChatGPT in the following steps:
1. The script sends the content of the instructions file.
2. The script sends the content of the file to process.
3. The script displays the response from ChatGPT.

Prerequisites
-------------
Before running the script, ensure you have the following installed:
1. Python: Make sure Python is installed on your system.
2. OpenAI API: Install the OpenAI API library using the command:
py -m pip install openai
3. PyPDF2: Install the PyPDF2 library using the command:
py -m pip install PyPDF2
4. pdfminer: Install the pdfminer library using the command:
py -m pip install pdfminer.six==20201018
5. Environment Variable: Set the environment variable AZURE_OPENAI_API_KEY with the provided API key.
6. The Azure endpoint, API version, and model are read from a config.json file in the same directory by default. Example config.json:
{
    "azure_endpoint": "https://becopenaidev3.openai.azure.com/",
    "api_version": "2024-10-21",
    "model": "gpt-4o"
}

How to Run the Script
---------------------
Run the script:
py process_file_with_ai.py <file_to_process> <instructions_file> [--debug] [--config <config.json>]

	--debug: If set, the pdf to text conversion will be written in file with same name as pdf but with extension .txt
	--config: Path to the config.json file containing Azure endpoint, API version, and model (optional, defaults to config.json)


Example 1: Perform a multi pass review of a ASCII DOC design document
------------------------------------------------------------------------

py .\process_file_with_ai.py detailed_design_msg_server.adoc review_detailed_design.txt



