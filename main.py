import os
import io
from PIL import Image
from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Query, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import json

from dotenv import load_dotenv

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

@app.post("/analyse")
async def analyse_image(file: UploadFile = File(...)):
  try:
    image = Image.open(io.BytesIO(await file.read()))

    model = configure_model()
    prompt = f"""
      Extract the questions, and the question description (it is bilingual Malay and English, only extract English) from the image.

      The format is usually this way:
      2) Question/Question Description
        <DIAGRAM> (DO not extract image and texts from diagram)

        a) Question
        b) Question

        ...etc

      Respond like this:

      {{
        "questions": [
          {{ 
            "question_description": "...", // usually start with number
            "subquestions": [  // usually start with a, b, c, d etc
              "question": string
              "marks": number
                // ...
            ]
          }}
        ]
      }}
      
    """
    response = model.generate_content([prompt, image])
    questions = json.loads(response.text)

    return {"status": "success", "message" : " Sccuess", "data": questions}

  except Exception as e:
    raise HTTPException(status_code=500, detail={"status" : "error", "message": str(e), "data": None})
