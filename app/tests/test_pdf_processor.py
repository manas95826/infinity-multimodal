import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from ..core.pdf_processor import PDFProcessor

@pytest.fixture
def pdf_processor():
    return PDFProcessor(
        mistral_api_key="test_mistral_key",
        openai_api_key="test_openai_key"
    )

def test_encode_pdf_file_not_found(pdf_processor):
    """Test handling of non-existent PDF file"""
    result = pdf_processor.encode_pdf("nonexistent.pdf")
    assert result is None

@pytest.mark.asyncio
async def test_process_with_ocr_success(pdf_processor):
    """Test successful PDF processing flow"""
    # Mock the encode_pdf method
    pdf_processor.encode_pdf = Mock(return_value="mock_base64")
    
    # Mock Mistral OCR response
    mock_ocr_response = "Sample OCR text"
    pdf_processor.mistral_client.ocr.process = Mock(return_value=mock_ocr_response)
    
    # Mock OpenAI response
    mock_structured_content = {
        "metadata": {
            "document_date": "2024-03-20",
            "other_dates": []
        },
        "content": []
    }
    
    with patch.object(pdf_processor.openai_client.chat.completions, 'create') as mock_create:
        mock_create.return_value.choices = [
            Mock(message=Mock(content=mock_structured_content))
        ]
        
        # Create a temporary test file
        test_file = "test.pdf"
        Path(test_file).touch()
        
        try:
            result = pdf_processor.process_with_ocr(test_file)
            
            assert result is not None
            assert result["status"] == "success"
            assert "output_path" in result
            assert Path(result["output_path"]).exists()
            
        finally:
            # Clean up
            Path(test_file).unlink()
            if result and "output_path" in result:
                Path(result["output_path"]).unlink()

@pytest.mark.asyncio
async def test_process_ocr_content_edge_case(pdf_processor):
    """Test processing of OCR content with edge cases"""
    # Test with empty OCR response
    result = pdf_processor._process_ocr_content("")
    assert result is None
    
    # Test with malformed OCR response
    result = pdf_processor._process_ocr_content("malformed content")
    assert result is None 