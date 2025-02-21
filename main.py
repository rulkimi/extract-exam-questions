import json
import asyncio
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from modules.sections import identify_sections
from modules.questions import build_extract_section_data_prompt, validate_section_content
from modules.sections import build_identify_sections_prompt, identify_sections
from modules.utils import get_reference_pdf

from config.logger import log_error
from config.ai_client import get_ai_response, convert_pdf_to_part

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

# Main Function
@app.post("/extract_questions")
async def analyse_pdf(pdf_file: UploadFile = File(...)):
    try:
        if not pdf_file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Input PDF file must end with .pdf")

        user_pdf_content = await pdf_file.read()
        pdf = convert_pdf_to_part(user_pdf_content)

        # Step 1: Identify sections and their page ranges
        print("Identifying sections...")
        indentify_sections_prompt = build_identify_sections_prompt()
        sections_response = get_ai_response([pdf, indentify_sections_prompt])
        sections_response_json = json.loads(sections_response.text)
        sections = await identify_sections(sections_response_json, user_pdf_content)

        reference_pdf_content = get_reference_pdf()
        reference_pdf = convert_pdf_to_part(reference_pdf_content)

        # Step 2: Extract data for each section
        print("Extracting data from sections...")
        sections_data = []
        for section in sections:
            print(f"Processing section: {section['name']}")
            prompt = build_extract_section_data_prompt(section) + f"IMPORTANT: ONLY GET THE ENGLISH CONTENT FOR NOW"
            try:
                response = get_ai_response([reference_pdf, pdf, prompt])
                validate_section_content(response.text, section['name'])
                print(response.text)
                response_json = json.loads(response.text)
                sections_data.append(response_json)
            except Exception as e:
                print(f"Error in extract_section_data: {str(e)}")
                log_error(str(e), response.text if 'response' in locals() else None)
                raise ValueError(f"Error extracting section data: {str(e)}")
            # Add a delay before processing the next section
            await asyncio.sleep(5)  # Wait for 2 seconds
        
        with open("outputs/temporary_output_data.json", "w", encoding="utf-8") as json_file:
            json.dump(sections_data, json_file, ensure_ascii=False, indent=4)
        return {"status": "Success", "data": sections_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e), "data": None})