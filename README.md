# Invoice Processor

This service accepts invoice files, extracts structured line items using a generative AI model, assigns tax categories, and computes tax totals. Processed results are persisted as JSON files in the `output/` directory.

## Run locally

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Create a `.env` file in the project root

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

### 4. Start the API

```bash
python -m uvicorn app.main:app --reload
```

The service will start at:

```text
http://127.0.0.1:8000
```

### 5. Process a sample invoice

```bash
curl -X POST "http://127.0.0.1:8000/process-invoice" \
  -F "file=@data/sample_invoices/Invoice 1.pdf"
```

Processed invoice results will be written to the `output/` directory as JSON files.

## Run with Docker

### 1. Build the image

```bash
docker build -t invoice-processor .
```

### 2. Run the container

```bash
docker run --rm -p 8000:8000 --env-file .env invoice-processor
```

### 3. Submit a sample invoice

```bash
curl -X POST "http://127.0.0.1:8000/process-invoice" \
  -F "file=@data/sample_invoices/Invoice 1.pdf"
```
