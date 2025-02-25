import json
import asyncio
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from modules.sections import identify_sections
from modules.questions import build_extract_section_data_prompt, validate_section_content
from modules.sections import build_identify_sections_prompt, identify_sections
from modules.utils import get_reference_pdf

from config.logger import log_error
from config.ai_client import get_ai_response, convert_pdf_to_part

from db.init import init_db

load_dotenv()

app = FastAPI()
supabase = init_db()

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
async def analyse_pdf(background_tasks: BackgroundTasks, pdf_file: UploadFile = File(...)):
    try:
        if not pdf_file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Input PDF file must end with .pdf")

        user_pdf_content = await pdf_file.read()
        pdf = convert_pdf_to_part(user_pdf_content)

        print("Identifying sections...")
        indentify_sections_prompt = build_identify_sections_prompt()
        sections_response = get_ai_response([pdf, indentify_sections_prompt])
        sections_response_json = json.loads(sections_response.text)
        sections = await identify_sections(sections_response_json, user_pdf_content)

        # insert document and get the inserted record's ID
        insert_response = supabase.table("documents").insert({"file_name": pdf_file.filename}).execute()
        document_id = insert_response.data[0]['id'] 

        background_tasks.add_task(extract_data, pdf, sections, document_id)

        return {
            "status": "success", 
            "message": "File uploaded successfully. Please wait while it being processed.", 
            "data": { "document_id": document_id }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e), "data": None})

def extract_data(pdf, sections, document_id: str):
    reference_pdf_content = get_reference_pdf()
    reference_pdf = convert_pdf_to_part(reference_pdf_content)

    print("Extracting data from sections...")
    sections_data = []
    for section in sections:
        print(f"Processing section: {section['name']}")
        prompt = build_extract_section_data_prompt(section)
        try:
            response = get_ai_response([reference_pdf, pdf, prompt])
            validate_section_content(response.text, section['name'])
            print(response.text)
            response_json = json.loads(response.text)
            sections_data.append(response_json)
        except Exception as e:
            print(f"Error in extract_section_data: {str(e)}")
            supabase.table("documents").update({"status": "failed"}).eq("id", document_id).execute()
            log_error(str(e), response.text if 'response' in locals() else None)
            raise ValueError(f"Error extracting section data: {str(e)}")
    
    supabase.table("documents").update({"data": sections_data, "status": "extracted"}).eq("id", document_id).execute()

    with open("outputs/temporary_output_data.json", "w", encoding="utf-8") as json_file:
        json.dump(sections_data, json_file, ensure_ascii=False, indent=4)
    return {"status": "Success", "data": sections_data}
