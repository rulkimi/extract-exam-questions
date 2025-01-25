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
	Extract the questions, question description, and relevant structure from the following text description of the image. Only extract English content, ignoring bilingual elements or diagram text.

	Image description:
	{image_description}

	The output must follow this structure:
	{{
		"question_number": "string",  // e.g., "5"
		"question_text": "string",    // Main question description
		"diagram": "string",          // Diagram reference, if any
		"sub_questions": [
			{{
				"sub_question": "string",   // Sub-question identifier (e.g., "a", "b")
				"question_text": "string",  // Text of the sub-question
				"answer": "string",         // Answer, if included
				"sub_sub_questions": [      // Nested sub-questions, if any
					{{
						"sub_sub_question": "string",
						"question_text": "string",
						"answer": "string"
					}}
				]
			}}
		]
	}}
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

		return {"status": "success", "message": "Success", "data": aggregated_questions}

	except Exception as e:
		raise HTTPException(
			status_code=500,
			detail={"status": "error", "message": str(e), "data": None},
		)
