import json
import re
import os
from datetime import datetime
from dotenv import load_dotenv
import time
import jwt
import gc

from fastapi import FastAPI, HTTPException, File, UploadFile, BackgroundTasks, Request, Path, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from modules.wordgen import generate
from modules.extract_images import get_images_and_update_json

from config.ai_client import AIClient

from db.init import init_db

load_dotenv()

app = FastAPI()
supabase = init_db()

RAILWAY_URL = os.getenv("RAILWAY_STATIC_URL") 
GITHUB_PAGES_URL = os.getenv("GITHUB_PAGES_URL")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

origins = ["http://localhost:5173"]

if RAILWAY_URL:
    origins.append(RAILWAY_URL)
if GITHUB_PAGES_URL:
    origins.append(GITHUB_PAGES_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        if not SUPABASE_JWT_SECRET:
            raise HTTPException(status_code=500, detail="JWT secret not configured")
        
        payload = jwt.decode(
            token, 
            SUPABASE_JWT_SECRET, 
            algorithms=["HS256"],
            audience="authenticated"
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: user not found")
        return {"id": user_id, "payload": payload}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/documents")
def get_documents(user: dict = Depends(get_current_user)):
    response = supabase.table("documents").select("*").order("uploaded_date", desc=True).execute()
    return {
        "status": "success",
        "message": "Documents fetched successfully",
        "data": {
            "documents": response.data
        }
    }

@app.get("/documents/{id}")
def get_document_by_id(id: str, user: dict = Depends(get_current_user)):
    response = supabase.table("documents").select("*").eq("id", id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "status": "success",
        "message": "Document fetched successfully",
        "data": response.data[0]
    }

@app.delete("/documents/{id}")
def delete_document(id: str = Path(...), user: dict = Depends(get_current_user)):
	response = supabase.table("documents").delete().eq("id", id).execute()
	# Supabase Python client returns deleted rows in response.data
	if response.data and len(response.data) > 0:
		return {
			"status": "success",
			"message": "Document deleted successfully."
		}
	else:
		raise HTTPException(status_code=404, detail="Document not found")

@app.post("/extract_questions")
async def analyse_pdf(background_tasks: BackgroundTasks, pdf_file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    try:
        if not pdf_file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Input PDF file must end with .pdf")

        user_pdf_content = await pdf_file.read()
    
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S") + '_' + pdf_file.filename.lower().replace(" ", "_")
        supabase.storage.from_("files").upload(unique_id, user_pdf_content)
        download_link = supabase.storage.from_("files").get_public_url(unique_id)

        insert_response = supabase.table("documents").insert({"file_name": pdf_file.filename, "file_url": download_link}).execute()
        document_id = insert_response.data[0]['id']
        print(f"Processing PDF: {pdf_file.filename}, assigned ID: {document_id}")
        background_tasks.add_task(extract_data, user_pdf_content, document_id)
        
        return {
            "status": "success", 
            "message": "File uploaded successfully. Please wait while it being processed.", 
            "data": { "document_id": document_id, "file_url": download_link }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e), "data": None})

def extract_data(pdf, document_id):
    start_time = time.time()  # Capture the start time
    data = {}
    image_data = {}
    ai_client = AIClient()

    try:
        # Start extract full JSON
        data = ai_client.extract_full(pdf)
        print("Initial JSON extraction complete.")

        image_data = get_images_and_update_json(data, pdf, supabase, "img", document_id)

        # Clean up AI client
        ai_client.cleanup()
        del ai_client
        gc.collect()

        supabase.table("documents").update({"data": data, "status": "extracted", "image_data": image_data}).eq("id", document_id).execute()
        end_time = time.time()  # Capture the end time
        elapsed_time = end_time - start_time  # Calculate elapsed time
        print(f"Total elapsed time: {elapsed_time} seconds")
        
        return {
            "status": "success",
            "message": "Questions extracted successfully",
            "elapsed_time": elapsed_time,
            "data": data,
            "image_data": image_data
        }
    except Exception as e:
        print(f"Error extracting questions: {str(e)}")
        supabase.table("documents").update({"status": "failed"}).eq("id", document_id).execute()
        raise HTTPException(status_code=500, detail=str(e))

    
@app.post("/generate_word")
async def generate_word(request: Request, user: dict = Depends(get_current_user)):
    data = await request.json()
    json_data = data.get('jsonData')  # Access jsonData
    image_data = data.get('imageData')  # Access imageData
    filename = data.get('filename')  # Access filename
    buffer = generate(json_data, image_data=image_data)
    return StreamingResponse(buffer, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', headers={"Content-Disposition": f"attachment; filename={filename}"})
