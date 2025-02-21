from google import genai
import os
import base64
import google.generativeai as genai

def configure_model():
  genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
  return genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={"response_mime_type": "application/json"},
  )

def get_ai_response(contents, response_schema=None, model="gemini-1.5-flash"):
  model = configure_model()
  response = model.generate_content(contents)
  return response

def convert_pdf_to_part(pdf_file):
  pdf_content_base64 = base64.b64encode(pdf_file).decode("utf-8")
  return {"mime_type": "application/pdf", "data": pdf_content_base64}


# Gemini 2.0 Configurations here:

# client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# def get_ai_response(contents, response_schema=None, model="gemini-1.5-flash"):
#   response = client.models.generate_content(
#     model=model,
#     contents=contents,
#     config={
#         "response_mime_type": "application/json",
#         **({"response_schema": response_schema} if response_schema is not None else {})
#     }
#   )
#   return response

# def convert_pdf_to_part(pdf_file):
#   pdf_content_base64 = base64.b64encode(pdf_file).decode("utf-8")
#   return genai.types.Part.from_bytes(data=pdf_content_base64, mime_type="application/pdf")