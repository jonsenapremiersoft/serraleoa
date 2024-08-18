python from fastapi import FastAPI, HTTPExceptionfrom pydantic import BaseModelfrom PyPDF2 import PdfReaderimport base64import ioimport json

app = FastAPI()
class PDFBase64(BaseModel):
    file_base64: str@app.post("/extract_pdf_content/")async def extract_pdf_content(data: PDFBase64):
    try:
        # Decodifica o base64        pdf_bytes = base64.b64decode(data.file_base64)                # Usa um buffer de memória para simular um arquivo        pdf_file = io.BytesIO(pdf_bytes)                # Lê o conteúdo do PDF        pdf_reader = PdfReader(pdf_file)        text_content = {}                for i, page in enumerate(pdf_reader.pages):
            text_content[f"page_{i+1}"] = page.extract_text()
                # Retorna o conteúdo como JSONreturn {"pdf_content": text_content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
 