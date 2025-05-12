## E-commerce Product Category Tree Generator



This Python script uses Google Gemini AI to generate an e-commerce product category tree based on natural language input. It processes user input to extract positive and negative keywords and uses these to create a hierarchical CSV representation of a product category structure


## Requirements
    
    - Python 3.x

The following Python packages:

    - google-generativeai
    - python-dotenv
    - uuid
    - re
    - json
    - logging

## You can install the required packages using pip:

    pip install google-generativeai python-dotenv 

    or 

    pip install -r requirements.txt


## Setup

1. Set Up the API Key

    This script requires a Google Gemini API key to interact with the AI model.

    - Obtain an API key from Google Generative AI (Gemini).

    - Create a .env file in the project root directory with the following content:
    
      GEMINI_API_KEY=your_api_key_here


2. Add Logging Configuration (Optional)

Logging is set up in the script to track the application's flow. You can configure the logging format in the script, which will be saved to the console.


3. Prepare Environment

Make sure your .env file is correctly configured with your API key, as the script checks for this environment variable.


## How It Works

1. Natural Language Input:

The user is prompted to describe their product focus (e.g., the types of products they want to include or exclude).

2. Keyword Extraction:

The input is processed by the Gemini model to extract positive and negative keywords.

    - Positive Keywords: Categories you want to include in the product tree.

    - Negative Keywords: Categories you want to avoid in the product tree.
    
3. Generate Category Tree:

The positive and negative keywords are used to generate a product category tree in CSV format. This is done by interacting with the Gemini model using the generated prompt.

4. Clean the Generated CSV:

The generated category tree may contain irrelevant or unwanted categories based on the negative keywords. The script filters these out.

5. Save CSV File:

The cleaned CSV file is saved to the disk with a unique filename.



## How to Use

1. Run the Python script:

    - python generator_category.py

2. When prompted, enter a description of your shop's product focus:

    -   🗣️ Describe your shop's product focus (e.g. what to include or avoid):
    > Electronics, but exclude clothing and accessories

3. The script will process the input, generate a product category tree, clean it, and save it to a CSV file.

- Example output:

    ✅ Category tree saved to 'category_tree_1234-5678-90ab.csv'.

- The CSV file will have the structure:
    Category ID,Parent ID,Category Name
    1,              0,      Used
    2,              1,      Refurbished

## Error Handling

If the input is empty, an error message will be shown:
    
    ❌ Error: Please enter your requirements.


## Files Generated

CSV File: A CSV file containing the e-commerce product category tree. The file is saved with a unique UUID-based filename (e.g., category_tree_1234-5678-90ab.csv).

## Troubleshooting

- Missing API Key: Make sure the .env file is correctly configured with the GEMINI_API_KEY value.

- API Limitations: Ensure that your API key has sufficient quota for Gemini requests.