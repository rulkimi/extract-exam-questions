import os
import json
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
import logging
from sections import identify_sections
from questions import extract_section_data

logging.basicConfig(level=logging.WARNING)

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

# Configure Model
def configure_model():
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={"response_mime_type": "application/json"},
    )

# Log Errors into error_logs folder
def log_error(error_msg: str, response_text: str = None) -> str:
    """Log error details to a file and return the filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    error_log_name = f'error_log_{timestamp}.txt'
    with open(error_log_name, 'w', encoding='utf-8') as f:
        f.write(f"Error: {error_msg}\n\n")
        if response_text:
            f.write(f"Response text:\n{response_text}\n\n")
    return error_log_name

def log_json(json_data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_log_name = f'json_log_{timestamp}.json'

    # 🔍 Ensure `json_data` is a valid JSON structure
    if isinstance(json_data, list) and all(isinstance(item, str) for item in json_data):
        # Convert each string entry to a dictionary
        json_data = [json.loads(item) for item in json_data]
    elif isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)  # Convert single JSON string to dict
        except json.JSONDecodeError:
            print("❌ Invalid JSON string provided!")
            return

    # 🔄 Merge all "main_questions" into one list
    if isinstance(json_data, list):  # If input is a list of objects
        combined_main_questions = [q for entry in json_data if "main_questions" in entry for q in entry["main_questions"]]
        json_data = {"main_questions": combined_main_questions}

    # 📝 Save merged JSON
    with open(json_log_name, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Merged JSON saved to {json_log_name}")


# Main Function
@app.post("/extract_questions")
async def analyse_pdf(pdf_file: UploadFile = File(...)):
  try:
      if not pdf_file.filename.endswith(".pdf"):
          raise HTTPException(status_code=400, detail="Input PDF file must end with .pdf")

      user_pdf_content = await pdf_file.read()

      model = configure_model()
      
      # Step 1: Identify sections and their page ranges
      print("Identifying sections...")
      sections_data = await identify_sections(model, user_pdf_content)
      
      # Step 2: Extract data for each section
      # NOTE: Gemini is inconsistent in giving valid JSONs (Sometimes ok sometimes not)
      # Consider cleaning the JSONs (which i've done but errors like delimiter, and double quotes still persists)
      print("Extracting data from sections...")
      all_sections_data = []
      for section in sections_data:
          print(f"Processing section: {section['name']}")
          section_data = await extract_section_data(
              model, 
              user_pdf_content, 
              section
          )    
          # Ensure section_data is a dictionary
          if isinstance(section_data, str):
              section_data = json.loads(section_data)          
          all_sections_data.append(section_data)
      
      # Step 3: Combine results
      combined_data = {
          "sections": all_sections_data 
      }
      
      log_json(combined_data)

      return {
          "status": "success",
          "message": "Successfully extracted all sections",
          "data": json.dumps(combined_data)
      }

  except Exception as e:
      import traceback
      traceback.print_exc()
      raise HTTPException(
          status_code=500,
          detail={"status": "error", "message": str(e), "data": None}
      )