# PDF Processing API

A robust API service that processes PDF documents using OCR and AI to extract structured content. The service uses Mistral AI for OCR and OpenAI's GPT-4o for content structuring.

## Features

- **PDF Processing**
  - OCR processing using Mistral AI
  - Intelligent content structuring using GPT-4
  - Extraction of tables, lists, headers, footers, and more
  - Automatic date and reference extraction

- **Content Structure**
  - Document metadata (dates, references)
  - Tables in both raw text and HTML/Markdown format
  - Lists with proper formatting
  - Headers and footers identification
  - Image detection with bounding boxes
  - Page number tracking for all elements

- **API Features**
  - FastAPI-based REST API
  - File upload endpoint
  - Health check endpoint
  - Comprehensive error handling
  - Automatic cleanup of temporary files

## Output Format

The API structures the content in the following JSON format:

```json
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
          "page_number": 5
        }
      ],
      "clauses_articles_acts": [
        {
          "reference": "reference text",
          "type": "clause | article | act",
          "page_number": 7
        }
      ],
      "persons": [
        {
          "name": "person name",
          "role": "role description",
          "page_number": 3
        }
      ]
    }
  },
  "content": [
    {
      "type": "title | paragraph | list | table | figure | header | footer",
      "text": "content text",
      "page_number": 1,
      "metadata": {
        "additional_info": "extra information"
      }
    }
  ]
}
```

## Setup

### Prerequisites

- Python 3.9+
- Docker (optional)
- Mistral AI API key
- OpenAI API key

### Environment Variables

Create a `.env` file in the root directory:

```env
MISTRAL_API_KEY=your_mistral_api_key
OPENAI_API_KEY=your_openai_api_key
```

### Local Setup

1. Clone the repository:
```bash
git clone 
cd pdf-processor
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
uvicorn app.api.main:app --reload
```

### Docker Setup

1. Build the image:
```bash
docker build -t pdf-processor .
```

2. Run the container:
```bash
docker run -p 8000:8000 \
  -e MISTRAL_API_KEY=your_mistral_key \
  -e OPENAI_API_KEY=your_openai_key \
  -v $(pwd)/app/output:/app/app/output \
  pdf-processor
```

## API Usage

### Process PDF Document

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/document.pdf"
```

Response:
```json
{
  "status": "success",
  "message": "PDF processed successfully",
  "output_path": "app/output/document_structured.json",
  "content": { ... }
}
```

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy"
}
```

## Testing

Run the test suite:

```bash
pytest app/tests/
```

## Project Structure

```
.
├── app/
│   ├── api/
│   │   └── main.py           # FastAPI application
│   │   └── pdf_processor.py  # Core processing logic
│   ├── tests/
│   │   └── test_pdf_processor.py  # Test cases
│   ├── output/               # Processed JSON files
│   └── temp/                 # Temporary files
├── Dockerfile
├── requirements.txt
└── README.md
```

## Error Handling

The API includes comprehensive error handling for:
- Invalid file types
- File processing failures
- OCR processing errors
- Content structuring issues
- File system operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
