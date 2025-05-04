import base64
import json
from pathlib import Path
from typing import Optional, Dict, Any
from mistralai import Mistral
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, mistral_api_key: str, openai_api_key: str):
        self.mistral_client = Mistral(api_key=mistral_api_key)
        self.openai_client = OpenAI(api_key=openai_api_key)
    
    def encode_pdf(self, pdf_path: str) -> Optional[str]:
        """Encode the pdf to base64."""
        try:
            with open(pdf_path, "rb") as pdf_file:
                return base64.b64encode(pdf_file.read()).decode('utf-8')
        except FileNotFoundError:
            logger.error(f"Error: The file {pdf_path} was not found.")
            return None
        except Exception as e:
            logger.error(f"Error encoding PDF: {e}")
            return None

    def process_with_ocr(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        """Process PDF with OCR and structure the content."""
        try:
            base64_pdf = self.encode_pdf(pdf_path)
            if not base64_pdf:
                return None

            # Get OCR response
            ocr_response = self.mistral_client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{base64_pdf}"
                }
            )

            # Process OCR response
            structured_content = self._process_ocr_content(ocr_response)
            if structured_content:
                # Save to file and return path
                output_path = self._save_output(structured_content, pdf_path)
                return {
                    "status": "success",
                    "output_path": output_path,
                    "content": structured_content
                }
            return None

        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return None

    def _process_ocr_content(self, ocr_response: str) -> Optional[Dict[str, Any]]:
        """Process OCR response using OpenAI to structure the content."""
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
Return the response as a valid JSON string.
You must return a valid JSON object without ant additional info and delimeters following this exact schema. Ensure all values are properly formatted and quoted."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Process and structure this OCR text into the specified JSON format:\n\n{ocr_response}"}
                ]
            )
            
            content = response.choices[0].message.content
            logger.info(f"OpenAI Response Content: {content}")
            
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"JSON Decode Error: {e}")
                logger.error(f"Failed content: {content}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing content with OpenAI: {e}")
            return None

    def _save_output(self, content: Dict[str, Any], original_pdf_path: str) -> str:
        """Save the structured content to a JSON file."""
        try:
            pdf_name = Path(original_pdf_path).stem
            output_path = f"app/output/{pdf_name}_structured.json"
            
            with open(output_path, 'w') as f:
                json.dump(content, f, indent=2)
            
            return output_path
        except Exception as e:
            logger.error(f"Error saving output: {e}")
            raise 