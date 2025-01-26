import os
import base64
from fastapi import FastAPI, HTTPException, File, UploadFile
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
    try:
        # Check if the uploaded file is a PDF
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        # Read the PDF content (await the asynchronous read)
        pdf_content = await file.file.read()
        print(pdf_content)

        # Encode the PDF content in Base64
        pdf_content_base64 = base64.standard_b64encode(pdf_content).decode("utf-8")
        print(pdf_content_base64)

        # Configure the Gemini AI model
        model = configure_model()

        # Define the prompt for question extraction
        prompt = f"""Extract questions from this document and put them in a JSON file in this format:
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
        - Preserve complete question semantics"""

        # Generate content using the Gemini AI model
        response = model.generate_content([
            {'mime_type': 'application/pdf', 'data': pdf_content_base64}, 
            prompt
        ])

        if not response:
            raise Exception("Failed to generate response from the AI model.")

        # Return the extracted questions as JSON
        return {
            "status": "success",
            "message": "Success",
            "data": response.text
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": str(e),
                "data": None,
            },
        )