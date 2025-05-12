import os
import json
import uuid
import re
import logging
from dotenv import load_dotenv
import google.generativeai as genai


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


load_dotenv()


API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")


genai.configure(api_key=API_KEY)

def extract_json_from_text(text):
    """Extract a valid JSON object from a string."""
    try:
        match = re.search(r'\{.*?\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            raise ValueError("Could not extract valid JSON from the response.")
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON: {e}")
        raise ValueError("Invalid JSON format in extracted text.")

def get_extracted_keywords(natural_input):
    
    try:
        
        extract_prompt = f"""
        From the following sentence, extract two lists:
        1. Positive prompts (categories to include)
        2. Negative prompts (categories to avoid)

        Return JSON format like this:
        {{"positive": [...], "negative": [...]}}

        Sentence: "{natural_input}"
        """
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        extraction_response = model.generate_content(extract_prompt)
        extracted_text = extraction_response.text.strip()

        if extracted_text.startswith("```"):
            extracted_text = extracted_text.split("```")[1].strip()

        extracted_json = extract_json_from_text(extracted_text)
        print({"positive": extracted_json["positive"], "negative": extracted_json["negative"]})
        return {"positive": extracted_json["positive"], "negative": extracted_json["negative"]}
    
    except Exception as e:
        logging.error(f"Error extracting keywords: {e}")
        raise

def build_category_prompt(positive, negative=None):
    
    try:
        if negative:
            return f"""
            You are an expert in e-commerce category generation.

            Generate a detailed product category tree in CSV format with the headers: 
            Category ID,Parent ID,Category Name.

            Use the following keywords to guide the content:

            Positive keywords: {positive}

            Exclude anything related to the following negative keywords: {negative}

            Ensure the structure is fully detailed practical for a real online store.
            
            The structure should form a hierarchy using Parent ID.
            Root categories should have Parent ID = 0.

            Output ONLY the CSV content. Do not include any commentary, markdown formatting, or code block.
            """
        else:
            print(f"It come when only positive parts extract..{positive}")
            return f"""
            You are an e-commerce category expert.

            Generate a detailed product category tree in CSV format with the headers: 
            
            Category ID,Parent ID,Category Name.

            Use the following positive keywords to guide the content:

            Positive keywords: {positive}
            
            Exclude anything related to the following negative keywords: {negative}
            
            Only include categories strictly related to these keywords.
            
            Ensure the structure is fully detailed practical for a real online store.
            
            The structure should form a hierarchy using Parent ID.
            Root categories should have Parent ID = 0.

            Output ONLY the CSV content. Do not include any commentary, markdown formatting, or code block.
            """
    except Exception as e:
        logging.error(f"Error building category prompt: {e}")
        raise

def clean_csv(csv_content, negative_keywords):
   
    try:
        lines = csv_content.strip().split("\n")
        header = lines[0]
        cleaned_lines = [header]

        for line in lines[1:]:
            # if not any(neg.strip().lower() in line.lower() for neg in negative_keywords.split(",")):
            if not any(re.search(rf"\b{re.escape(neg.strip())}\b", line, re.IGNORECASE) for neg in negative_keywords.split(",")):

                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)
    except Exception as e:
        logging.error(f"Error cleaning CSV content: {e}")
        raise

def save_csv_file(content):
   
    try:
        filename = f"category_tree_{uuid.uuid4()}.csv"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info(f"CSV file saved as {filename}")
        return filename
    except IOError as e:
        logging.error(f"Error saving CSV file: {e}")
        raise

# Main execution flow
def main():
    try:
       
        natural_input = input("🗣️ Describe your shop's product focus (e.g. what to include or avoid):\n> ")
        
        if not natural_input.strip():
            raise ValueError("Please enter your requirements.")
        
        
        keywords = get_extracted_keywords(natural_input)
        positive, negative = keywords["positive"], keywords["negative"]

        
        category_prompt = build_category_prompt(positive, negative)
        print(f"📝 Generating category tree with the following prompt:\n{category_prompt}")
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(category_prompt)
        csv_output = response.text.strip()

        if csv_output.startswith("```"):
            csv_output = csv_output.split("```")[1].strip()

        
        cleaned_csv = clean_csv(csv_output, ",".join(negative))

        
        saved_filename = save_csv_file(cleaned_csv)
        print(f"✅ Category tree saved to '{saved_filename}'.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
