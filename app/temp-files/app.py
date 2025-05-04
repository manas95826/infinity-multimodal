import base64
import requests
import os
import json
from mistralai import Mistral
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def encode_pdf(pdf_path):
    """Encode the pdf to base64."""
    try:
        with open(pdf_path, "rb") as pdf_file:
            return base64.b64encode(pdf_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {pdf_path} was not found.")
        return None
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")
        return None

def process_ocr_content(ocr_response):
    """Process OCR response using OpenAI to structure the content."""
    openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    
    system_prompt = """Analyze the OCR text and structure it into a JSON format with the following schema:

{
  "metadata": {
    "document_date": "YYYY-MM-DD",
    "other_dates": [
      { "date": "YYYY-MM-DD", "event": "description" }
    ],
    "references": {
      "letters": [
        {
          "name": "letter reference",
          "page_number": "integer"
        }
      ],
      "clauses_articles_acts": [
        {
          "reference": "reference text",
          "type": "clause | article | act",
          "page_number": "integer"
        }
      ],
      "persons": [
        {
          "name": "person name",
          "role": "person role",
          "page_number": "integer"
        }
      ]
    }
  },
  "content": [
    {
      "type": "one of: title, paragraph, list, table, figure, header, footer",
      "text": "content text",
      "page_number": "integer",
      "metadata": {
        "additional_info": "any relevant additional information"
      }
    }
  ]
}

For tables, include both raw text and formatted HTML/markdown.
For figures, include bbox coordinates if available.
Ensure all dates are in YYYY-MM-DD format.
Return the response as a valid JSON string."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Process and structure this OCR text into the specified JSON format:\n\n{ocr_response}"}
            ],
            response_format={ "type": "json_object" }
        )
        
        # Parse the response to ensure valid JSON and pretty print
        structured_content = json.loads(response.choices[0].message.content)
        return json.dumps(structured_content, indent=2)
    except Exception as e:
        print(f"Error processing content with OpenAI: {e}")
        return None

# Path to your pdf
pdf_path = "Contract Agreement.pdf"

# Getting the base64 string
base64_pdf = encode_pdf(pdf_path)

api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

# Get OCR response
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": f"data:application/pdf;base64,{base64_pdf}" 
    }
)

# Process the OCR response to get structured content
structured_content = process_ocr_content(ocr_response)

# Print the structured content
print("\nStructured Content:")
print(structured_content)