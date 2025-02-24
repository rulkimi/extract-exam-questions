import os
import base64
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import json
from dotenv import load_dotenv
from sanitize import parse_json_with_retry
# from ver3.prompt3 import build_prompt

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

prompt = """
   Extract structured data from the user input PDF and format it **exactly** in the following JSON structure. Follow these rules strictly:

   1. **Maintain JSON Structure**
      - The output **must match this JSON format exactly**.
      - Keep all **nested elements, section hierarchy, and attributes** intact.
      - **Do not flatten** or simplify the data structure.

   2. **Extract Sections & Instructions**
      - Identify **sections** (e.g., Bahagian A, B, C).
      - Extract section **instructions**.

   3. **Extract Questions & Maintain Nesting**
      - Preserve the exact numbering and **hierarchy**:
      - Main questions (1, 2, 3)
      - Sub-questions (1a, 1b, 1c)
      - Sub-sub-questions (1a(i), 1a(ii))
      - Ensure all text fields include **both `malay` and `english` keys**.
      - If no translation exists, use an **empty string** (`""`).

   4. **Extract Diagrams & Tables**
      - **All diagrams and tables must be extracted with page references**.
      - If **multiple diagrams are side by side**, use this structure:
      ```json
      {
         "type": "row",
         "layout": "2-columns",
         "items": [
            { "type": "diagram", "name": "Diagram 2.1" },
            { "type": "diagram", "name": "Diagram 2.2" }
         ]
      }
      ```
      - If a diagram **occupies a full row**, extract it as `{ "type": "diagram" }`.

   5. **Answer Spaces**
      - Identify and classify answer spaces:
      - `"single-line"`
      - `"multi-line"`
      - `"blank-space"`
      - `"multiple-choice"` (extract all options)

   6. **Marks Assignment Rules**
      - If **all `sub_questions` have marks**, then assign marks **only inside each sub-question**.
      - If **at least one `sub_question` has no marks**, assign the marks at the `question` level instead.
      - **Do not** assign marks to `main_questions`.

   7. **Ensure JSON Output Matches the Expected Format Exactly**
      - **Do not modify the structure**.
      - Ensure that **all elements appear in the correct order**.
      - If any information is missing, **return an empty string (`""`) instead of skipping it**.

   ## **Example JSON Output**
   ```json
   {
   "sections": [
      {
         "section_title": {
         "malay": "Bahagian A",
         "english": "Section A"
         },
         "instructions": {
         "malay": "Jawab semua soalan.",
         "english": "Answer all questions."
         },
         "main_questions": [
         {
            "number": "1",
            "content_flow": [
               {
               "type": "text",
               "text": {
                  "malay": "Rajah 1 menunjukkan satu spektrum gelombang elektromagnet.",
                  "english": "Diagram 1 shows an electromagnetic wave spectrum."
               }
               },
               {
               "type": "diagram",
               "name": "Diagram 1",
               "page": 4
               },
               {
               "type": "question",
               "number": "1(a)"
               }
            ],
            "questions": [
               {
               "number": "1(a)",
               "marks": 1,
               "content_flow": [
                  {
                     "type": "text",
                     "text": {
                     "malay": "Tandakan (V) untuk jawapan yang betul dalam kotak yang disediakan.",
                     "english": "Tick (V) for the correct answer in the box provided."
                     }
                  },
                  {
                     "type": "answer_space",
                     "format": "multiple-choice",
                     "options": [
                     {
                        "malay": "spektrum garis",
                        "english": "line spectrum"
                     },
                     {
                        "malay": "spektrum selanjar",
                        "english": "continuous spectrum"
                     }
                     ]
                  }
               ]
               }
            ]
         }
         ]
      }
   ]
   }
   """

@app.post("/extract_questions")
async def analyse_pdf(file: UploadFile = File(...)):
  try:
    if not file.filename.endswith(".pdf"):
      raise HTTPException(status_code=400, detail="Only PDF files are supported.")
  
    pdf_content = await file.read()
    pdf_content_base64 = base64.standard_b64encode(pdf_content).decode("utf-8")
  
    model = configure_model()

    print(f"Analysing {file.filename} file...")
    response = model.generate_content([
      {'mime_type': 'application/pdf', 'data': pdf_content_base64}, 
      prompt
    ])

    if not response:
      raise Exception("Failed to generate response from the AI model.")
  
    try:
      json_output = parse_json_with_retry(response.text)
      return {
        "status": "success",
        "message": "Success",
        "data": json_output
      }
    except ValueError as e:
      print(f"Error processing response: {e}")
      print(f"Raw response text: {response.text}")
      raise HTTPException(
        status_code=500,
        detail=f"Invalid JSON response from model: {str(e)}. Raw response printed to logs."
      )

  except Exception as e:
    raise HTTPException(
      status_code=500,
      detail={"status": "error", "message": str(e), "data": None}
    )
