import os
import logging
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from ..core.pdf_processor import PDFProcessor
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF Processing API")

# Initialize PDF processor
pdf_processor = PDFProcessor(
    mistral_api_key=os.getenv("MISTRAL_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

@app.post("/ingest")
async def ingest_pdf(file: UploadFile = File(...)):
    """
    Endpoint to process a PDF file and return structured content.
    The file is temporarily saved, processed, and then deleted.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")

        # Create temporary directory if it doesn't exist
        temp_dir = Path("app/temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Save uploaded file temporarily
        temp_path = temp_dir / file.filename
        try:
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Process the PDF
            result = pdf_processor.process_with_ocr(str(temp_path))
            
            if result is None:
                raise HTTPException(status_code=500, detail="Failed to process PDF")
            
            return JSONResponse(content={
                "status": "success",
                "message": "PDF processed successfully",
                "output_path": result["output_path"],
                "content": result["content"]  # Including content in response, but in practice might want to omit for large files
            })
            
        finally:
            # Clean up temporary file
            if temp_path.exists():
                temp_path.unlink()
                
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"} 