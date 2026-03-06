from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from document_extraction.content_understanding_sdk import analyze_document

app = FastAPI()

# Enable CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze-document")
async def analyze(file: UploadFile = File(...)):
    file_bytes = await file.read()

    result = analyze_document(
        file_bytes=file_bytes,
        filename=file.filename
    )

    return result