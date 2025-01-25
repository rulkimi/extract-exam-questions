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

def build_prompt(image_description):
    prompt = f"""
    STRICT EXTRACTION GUIDELINES:

    1. Question Number Parsing Rules:
    - ONLY use numeric integers for main question numbers (1, 2, 3, etc.)
    - Use alphabetic characters (a, b, c) ONLY for sub-questions
    - Use roman numerals (i, ii, iii) for sub-sub-questions

    2. Extraction Process:
    - Identify the MAIN question number as a numeric value
    - Identify sub-questions with alphabetic labels
    - Identify sub-sub-questions with roman numerals
    - NEVER use a, b, c as primary question numbers

    3. Structural Requirements:
    Produce a JSON with this EXACT structure:
    {{
        "question_number": "integer",  // MUST be a number
        "question_text": "string",     // Full main question description
        "diagram": "string",           // Diagram reference or description
        "sub_questions": [
            {{
                "sub_question": "string",   // Use "a", "b", "c" etc.
                "question_text": "string",  // Sub-question text
                "answer": "string",         // Optional answer
                "sub_sub_questions": [
                    {{
                        "sub_sub_question": "string", // Use "i", "ii", "iii"
                        "question_text": "string",
                        "answer": "string"
                    }}
                ]
            }}
        ]
    }}

    4. Content Extraction Instructions:
    - Extract ONLY English content
    - Ignore bilingual elements
    - Ignore diagram text not part of the actual question
    - Be precise and comprehensive

    Image description:
    {image_description}

    CRITICAL: If no clear question structure is found, return an empty JSON with an explanation in a comment.
    """
    return prompt

def build_aggregation_prompt(aggregated_questions):
	prompt = f"""
	Consolidate and organize the following extracted questions from multiple pages into a comprehensive, structured document. 

	Aggregated Questions:
	{json.dumps(aggregated_questions, indent=2)}

	Requirements:
	1. Group questions by their original question number
	2. Preserve all details from the original extraction
	3. Resolve any potential duplicates or overlapping information
	4. Maintain the original nested structure of sub-questions
	5. If the page does not explicitly show a new question number:
	   - Assume the content belongs to the previous question's sub-questions
	   - If no previous question exists, treat as a new question
	6. Identify and categorize:
	   - Main question number
	   - Question text
	   - Sub-questions (if any)
	   - Sub-sub-questions (if present)

	Output the consolidated questions in the same JSON structure as the original prompt.
	"""
	return prompt

@app.post("/extract_questions")
async def analyse_pdf(file: UploadFile = File(...)):
	aggregated_questions = []

	try:
		if not file.filename.endswith(".pdf"):
			raise HTTPException(status_code=400, detail="Only PDF files are supported.")

		pdf_content = await file.read()
		images = convert_from_bytes(pdf_content)

		model = configure_model()

		for page_number, image in enumerate(images, start=1):
			try:
				image_description = "The image contains a physics diagram showing an experiment setup for studying the relationship between current and force."
				prompt = build_prompt(image_description)

				response = model.generate_content([prompt, image])
				print(response.text) 

				if not response:
					raise Exception(f"Failed to generate response from the AI model for page {page_number}.")

				questions = json.loads(response.text)
				aggregated_questions.append(questions)

			except Exception as e:
				print(f"Error on page {page_number}: {str(e)}")
				continue
		
		# Aggregate questions across all pages
		aggregation_prompt = build_aggregation_prompt(aggregated_questions)
		aggregation_response = model.generate_content(aggregation_prompt)
		
		consolidated_questions = json.loads(aggregation_response.text)

		return {
			"status": "success", 
			"message": "Success", 
			# "original_page_questions": aggregated_questions,
			"consolidated_questions": consolidated_questions
		}

	except Exception as e:
		raise HTTPException(
			status_code=500,
			detail={"status": "error", "message": str(e), "data": None},
		)