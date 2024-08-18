from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from PyPDF2 import PdfReader
import base64
import io
import os
import tempfile
import whisper

app = FastAPI()

# Carrega o modelo Whisper uma vez durante o startup
model = whisper.load_model("tiny")

class PDFBase64(BaseModel):
    file_base64: str

def fix_base64_padding(b64_string):
    return b64_string + '=' * (4 - len(b64_string) % 4)

@app.get("/")
async def read_root():
    return {"message": "Welcome to my FastAPI application!"}

@app.post("/extract_pdf_content/")
async def extract_pdf_content(data: PDFBase64):
    try:
        # Decodifica a string base64
        fixed_base64 = fix_base64_padding(data.file_base64)
        pdf_bytes = base64.b64decode(fixed_base64)

        # Usa um buffer de memória para simular um arquivo
        pdf_file = io.BytesIO(pdf_bytes)

        # Lê o conteúdo do PDF
        pdf_reader = PdfReader(pdf_file)
        text_content = {}

        for i, page in enumerate(pdf_reader.pages):
            text_content[f"page_{i+1}"] = page.extract_text()

        # Retorna o conteúdo como JSON
        return {"pdf_content": text_content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe_audio/")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Salva o áudio MP3 em um arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_audio.write(file.file.read())
            temp_audio_path = temp_audio.name

        # Transcreve o áudio
        transcription = model.transcribe(temp_audio_path)

        # Remove o arquivo temporário
        os.remove(temp_audio_path)
        del model

        return {"transcription": transcription['text']}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
