from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PyPDF2 import PdfReader
import base64
import io

app = FastAPI()

class PDFBase64(BaseModel):
    file_base64: str

@app.post("/extract_pdf_content/")
async def extract_pdf_content(data: PDFBase64):
    try:
        # Decode the base64 string
        pdf_bytes = base64.b64decode(data.file_base64)

        # Use a memory buffer to simulate a file
        pdf_file = io.BytesIO(pdf_bytes)

        # Read the content of the PDF
        pdf_reader = PdfReader(pdf_file)
        text_content = {}

        for i, page in enumerate(pdf_reader.pages):
            text_content[f"page_{i+1}"] = page.extract_text()

        # Return the content as JSON
        return {"pdf_content": text_content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
