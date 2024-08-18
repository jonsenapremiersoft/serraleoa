from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from PyPDF2 import PdfReader
import base64
import io
from moviepy.editor import VideoFileClip
import whisper
import os
import tempfile

app = FastAPI()

class PDFBase64(BaseModel):
    file_base64: str

def fix_base64_padding(b64_string):
    return b64_string + '=' * (4 - len(b64_string) % 4)

@app.post("/extract_pdf_content/")
async def extract_pdf_content(data: PDFBase64):
    try:
        # Decode the base64 string
        fixed_base64 = fix_base64_padding(data.file_base64)
        pdf_bytes = base64.b64decode(fixed_base64)

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



model = whisper.load_model("base")
    
@app.post("/convert_and_transcribe/")
async def convert_and_transcribe(file: UploadFile = File(...)):
    try:
        # Salvar o arquivo de vídeo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(file.file.read())
            temp_video_path = temp_video.name

        # Converter o vídeo em MP3
        video_clip = VideoFileClip(temp_video_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            video_clip.audio.write_audiofile(temp_audio.name)
            temp_audio_path = temp_audio.name

        # Transcrever o áudio usando Whisper
        transcription = model.transcribe(temp_audio_path)

        # Remover arquivos temporários
        os.remove(temp_video_path)
        os.remove(temp_audio_path)

        return {"transcription": transcription['text']}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
