import os
from pdf2image import convert_from_bytes
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

origins = ["http://localhost:5173"]
if "PATH" in os.environ:
  os.environ["PATH"] += ":/opt/homebrew/bin"

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

def build_prompt(image_description, prev_question):
  prompt = f"""
  PREVIOUS main question: {prev_question}
  
  QUESTION EXTRACTION PROTOCOL:
  
  VERY IMPORTANT, PLEASE EXTRACT CAREFULLY HERE. CHECK IF THERE ARE ANY OF THESE:
    1. Strict Numbering Format: IMPORTANT!!! CHECK THESE PATTENRS
      - Main Questions: "1", "2", "3"
      - Sub-Questions: "(a)", "(b)", "(c)"
      - Sub-Sub-Questions: "(i)", "(ii)", "(iii)"
  
    2. Contextual Attachment Rules:
      - If NO main question present:
        * Attach to PREVIOUS main question
      - If NO sub-question present:
        * Attach to PREVIOUS main question's sub-question
      - Preserve exact semantic context
  
    3. Comprehensive Content Capture:
      - Capture ALL question variations
      - Prepare for consolidation in aggregation stage
      - Maintain original question numbering
  
  OUTPUT STRUCTURE:
  {{
    "question_number": "...", 
    "question_text": "Question text",
    "sub_questions": [
      {{
        "sub_question": "...",
        "question_text": "Sub-question text",
        "sub_sub_questions": [
          {{
            "sub_sub_question": "...",
            "question_text": "Sub-sub-question text"
          }}
        ]
      }}
    ]
  }}
  
  CONTENT CONSTRAINTS:
    - English only
    - Ignore bilingual elements
    - Preserve complete question semantics
  
  Image Description:
  {image_description}
  """
  return prompt

def build_aggregation_prompt(aggregated_questions):
  prompt = f"""
  QUESTION CONSOLIDATION PROTOCOL:
  
  MERGE STRATEGY:
    1. Question Number Consolidation
      - Identify and merge ALL questions with SAME number
      - Combine question texts
      - Merge sub-questions and sub-sub-questions
      - Preserve FULL semantic content
  
    2. Hierarchical Reconstruction
      - Maintain original question number
      - Comprehensive sub-question merging
      - Eliminate redundant content
  
    3. Attachment Rules
      - Preserve original question hierarchy
      - Intelligently combine overlapping content
      - Maintain precise semantic nuances
  
  INPUT DATA:
  {json.dumps(aggregated_questions, indent=2)}
  
  OUTPUT REQUIREMENTS:
  {{
    "question_number": "...", 
    "question_text": "Comprehensive combined question text",
    "sub_questions": [
      {{
        "sub_question": "...",
        "question_text": "Merged sub-question content",
        "sub_sub_questions": [
          {{
            "sub_sub_question": "...",
            "question_text": "Consolidated sub-sub-question"
          }}
        ]
      }}
    ]
  }}
  
  CRITICAL: Preserve original question numbering while merging identical questions
  """
  return prompt

@app.post("/extract_questions")
async def analyse_pdf(file: UploadFile = File(...)):
  aggregated_questions = []
  current_question_number = None  # Initialize the question number

  try:
    if not file.filename.endswith(".pdf"):
      raise HTTPException(status_code=400, detail="Only PDF files are supported.")
  
    pdf_content = await file.read()
    images = convert_from_bytes(pdf_content)
  
    model = configure_model()
  
    for page_number, image in enumerate(images, start=1):
      try:
        if page_number < 4:  # Skip first 3 pages
          continue
        image_description = "The image contains a physics diagram showing an experiment setup for studying the relationship between current and force."
        print(f"prev ques number {current_question_number}")
  
        prompt = build_prompt(image_description, current_question_number)
  
        response = model.generate_content([prompt, image])
        print(page_number, response.text)
  
        if not response:
          raise Exception(f"Failed to generate response from the AI model for page {page_number}.")
  
        questions = json.loads(response.text)
        aggregated_questions.append(questions)
  
        # to ensure the main question is updated correctly
        current_question_number = questions.get("question_number")  
  
      except Exception as e:
        print(f"Error on page {page_number}: {str(e)}")
        continue
  
    aggregation_prompt = build_aggregation_prompt(aggregated_questions)
    aggregation_response = model.generate_content(aggregation_prompt)
  
    consolidated_questions = json.loads(aggregation_response.text)
  
    return {
      "status": "success", 
      "message": "Success", 
      "consolidated_questions": consolidated_questions
    }
  
  except Exception as e:
    raise HTTPException(
      status_code=500,
      detail={"status": "error", "message": str(e), "data": None},
    )
