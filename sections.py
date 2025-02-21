import json
from datetime import datetime
import re
import fitz
import base64
  
def get_last_page(pdf_content: bytes) -> int:
    """Returns the last page number of a PDF."""
    doc = fitz.open(stream=pdf_content, filetype="pdf")  # Open PDF from bytes
    last_page = len(doc)  # Get total page count
    doc.close()
    return last_page

# Identify Sections
async def identify_sections(model, pdf_content: bytes) -> dict:
    # Convert PDF bytes to Base64
    pdf_content_base64 = base64.standard_b64encode(pdf_content).decode("utf-8")
    
    #Make initial call to identify sections and their page ranges.
    section_prompt = [
    {"text": "ANALYZE THIS PDF AND IDENTIFY THE MAIN QUESTIONS:"},
    {'mime_type': 'application/pdf', 'data': pdf_content_base64},
    {"text": """
        This PDF contains main questions from 1-11.
        INSTRUCTIONS:
        - Identify the **start and end pages** for the main questions in this PDF.
        - The start page is the page where the main question starts (e.g., "1").
        - The main question does not end until the next main question starts.
        - Some main questions may **overlap across pages**, meaning the start page of one main question might also be the end page of the previous question.
        
        Return the result as JSON in this format:
        ```json
        [
          {"main_question": "1", "start_page": start_1, "end_page": end_1},
          {"main_question": "2", "start_page": start_2, "end_page": end_2},
          {"main_question": "3", "start_page": start_3, "end_page": end_3},
          {"main_question": "4", "start_page": start_4, "end_page": end_4},
          {"main_question": "5", "start_page": start_5, "end_page": end_5},
          {"main_question": "6", "start_page": start_6, "end_page": end_6},
          {"main_question": "7", "start_page": start_7, "end_page": end_7},
          {"main_question": "8", "start_page": start_8, "end_page": end_8},
          {"main_question": "9", "start_page": start_9, "end_page": end_9},
          {"main_question": "10", "start_page": start_10, "end_page": end_10},
          {"main_question": "11", "start_page": start_11, "end_page": end_11}
        ]
        ```
     
      **Important Considerations**:
      - If a question starts on the same page where another ends, reflect this in the output.
      - Ensure no pages are skipped between questions.

    """},
    # {"text": """
    #     This PDF contains main questions from 1-11.
    #     Identify the **start pages only** for the main questions in this PDF.
        
    #     Return the result as JSON in this format:
    #     ```json
    #     {
    #         "main_questions": {
    #             "1": start_page_number,
    #             "2": start_page_number,
    #             "3": start_page_number,
    #             "4": start_page_number,
    #             "5": start_page_number,
    #             "6": start_page_number,
    #             "7": start_page_number,
    #             "8": start_page_number,
    #             "9": start_page_number,
    #             "10": start_page_number,
    #             "11": start_page_number
    #         }
    #     }
    #     ```
    # """}
    ]
    
    response = model.generate_content(section_prompt)
    if not response:
        raise Exception("Failed to identify sections from the PDF.")
    
    try:
      sections_data=json.loads(response.text)
      # section_start_pages=json.loads(response.text)
      # start_1 = int(section_start_pages["main_questions"]["1"])
      # start_2 = int(section_start_pages["main_questions"]["2"])
      # start_3 = int(section_start_pages["main_questions"]["3"])
      # start_4 = int(section_start_pages["main_questions"]["4"])
      # start_5 = int(section_start_pages["main_questions"]["5"])
      # start_6 = int(section_start_pages["main_questions"]["6"])
      # start_7 = int(section_start_pages["main_questions"]["7"])
      # start_8 = int(section_start_pages["main_questions"]["8"])
      # start_9 = int(section_start_pages["main_questions"]["9"])
      # start_10 = int(section_start_pages["main_questions"]["10"])
      # start_11 = int(section_start_pages["main_questions"]["11"])
      # last_page = get_last_page(pdf_content)
      # sections_data = [
      #     {"main_question": "1", "start_page": start_1, "end_page": start_2 - 1},
      #     {"main_question": "2", "start_page": start_2, "end_page": start_3 - 1},
      #     {"main_question": "3", "start_page": start_3, "end_page": start_4 - 1},
      #     {"main_question": "4", "start_page": start_4, "end_page": start_5 - 1},
      #     {"main_question": "5", "start_page": start_5, "end_page": start_6 - 1},
      #     {"main_question": "6", "start_page": start_6, "end_page": start_7 - 1},
      #     {"main_question": "7", "start_page": start_7, "end_page": start_8 - 1},
      #     {"main_question": "8", "start_page": start_8, "end_page": start_9 - 1},
      #     {"main_question": "9", "start_page": start_9, "end_page": start_10 - 1},
      #     {"main_question": "10", "start_page": start_10, "end_page": start_11 - 1},
      #     {"main_question": "11", "start_page": start_11, "end_page": last_page}
      # ]
      
      # Normalize section names and print section info
      for section in sections_data:
          print(f"Question {section['main_question']} (pages {section['start_page']}-{section['end_page']})")
      
      # Validate that we found at least one section
      if not sections_data or len(sections_data) == 0:
          raise ValueError("No sections (Section A/B/C or Bahagian A/B/C) were found in the PDF")
      
      # # Validate each section has required fields
      # for section in sections_data:  # Directly iterate over the list
      #     if not section.get("main_question"):
      #         raise ValueError("Section missing main_question field")
      #     if not isinstance(section.get("start_page"), (int, float)):
      #         raise ValueError(f"Invalid start_page for section {section.get('main_question')}")
      #     if not isinstance(section.get("end_page"), (int, float)):
      #         raise ValueError(f"Invalid end_page for section {section['main_question']}")
      #     if section["start_page"] > section["end_page"]:
      #         raise ValueError(f"Start page greater than end page for section {section['main_question']}")

      
      return sections_data
        
    except Exception as e:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_log_name = f'error_log_{timestamp}.txt'
        
        with open(error_log_name, 'w', encoding='utf-8') as f:
            f.write(f"Error identifying sections: {str(e)}\n")
            f.write(f"Model response:\n{response.text}")
            
        raise ValueError(f"Failed to identify sections properly: {str(e)}. See {error_log_name} for details")
