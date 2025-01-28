import os
import base64
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import json
from dotenv import load_dotenv
from prompt import build_prompt

load_dotenv()

app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

def configure_model():
  genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
  return genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={"response_mime_type": "application/json"},
  )

@app.post("/extract_questions")
async def analyse_pdf(file: UploadFile = File(...)):
  try:
    if not file.filename.endswith(".pdf"):
      raise HTTPException(status_code=400, detail="Only PDF files are supported.")
  
    pdf_content = await file.read()
    pdf_content_base64 = base64.standard_b64encode(pdf_content).decode("utf-8")
  
    model = configure_model()
    prompt = build_prompt()

    print(f"Analysing {file.filename} file...")
    response = model.generate_content([
      {'mime_type': 'application/pdf', 'data': pdf_content_base64}, 
      prompt
    ])

    if not response:
      raise Exception("Failed to generate response from the AI model.")
  
    return {
      "status": "success", 
      "message": "Success", 
      "data": json.loads(response.text)
    }
  
  except Exception as e:
    raise HTTPException(
      status_code=500,
      detail={"status": "error", "message": str(e), "data": None},
    )
