import os
import base64
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import json
from dotenv import load_dotenv
from datetime import datetime
import re
import logging

logging.basicConfig(level=logging.WARNING)

load_dotenv()

app = FastAPI()

origins = ["http://localhost:5173"]  # Or your frontend URL

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
        model_name="gemini-1.5-flash",  # Or your preferred model
        generation_config={"response_mime_type": "application/json"},
    )

# Log Error
def log_error(error_msg: str, response_text: str = None) -> str:
    """Log error details to a file and return the filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    error_log_name = f'error_log_{timestamp}.txt'
    with open(error_log_name, 'w', encoding='utf-8') as f:
        f.write(f"Error: {error_msg}\n\n")
        if response_text:
            f.write(f"Response text:\n{response_text}\n\n")
    return error_log_name

# Identify Sections
async def identify_sections(model, pdf_content_base64: str) -> dict:
    """Make initial call to identify sections and their page ranges."""
    section_prompt = [
        {"text": "ANALYZE THIS PDF AND IDENTIFY THE MAIN SECTIONS:"},
        {'mime_type': 'application/pdf', 'data': pdf_content_base64},
        {"text": """
            Identify the main sections in this PDF marked by 'Section A/B/C' or 'Bahagian A/B/C'.
            Each section starts with one of these markers.
            Return the result as JSON in this format:
            {
                "sections": [
                    {
                        "name": "Section A" or "Bahagian A",
                        "start_page": number,
                        "end_page": number
                    }
                ]
            }
            
            Important:
            - Bahagian A/Section A contains main questions 1-8
            - Bahagian B/Section B contains main questions 9-10
            - Bahagian C/Section C contains main questions 11-12
            - Look specifically for sections marked with "Bahagian A/B/C" or "Section A/B/C"
            - A section ends where the next section begins
            - The last section ends at the last page of the PDF
            - Include both the English and Malay names if present
            - Record the page number where each section marker appears
        """},
        {"text": f"""
            ANSWER SPACE IDENTIFICATION RULES:
            1. Visual Cues:
               - Single-line: One thin line or small box for short answers
               - Multi-line: Multiple lines or large box for paragraphs
               - Blank-space: Large empty area with no lines
               - Multiple-choice: Boxes/circles for ticking/filling

            2. Marks-based Hints:
               - 1 mark questions typically use single-line answers
               - 2-3 marks may use single or multi-line based on context
               - 4+ marks usually require multi-line answers
               
            3. Question Context:
               - Calculation questions usually need single-line for final answer
               - "Name/State/List" typically needs single-line
               - "Explain/Describe/Discuss" typically needs multi-line
               - "Fill in the blanks" always uses single-line
               
            Example formats:
            1. Single-line answer:
            {{
                "type": "answer_space",
                "format": "single-line"
            }}
            
            2. Multi-line answer:
            {{
                "type": "answer_space",
                "format": "multi-line",
                "lines": 4  // if number of lines is visible
            }}
        """},
        {"text": """
            SECTION PAGE BOUNDARY RULES:
            1. Section Start Pages:
               - Look for "Section A" or "Bahagian A" text to determine Section A's start page
               - Look for "Section B" or "Bahagian B" text to determine Section B's start page (Section B's start page marks the end of Section A)
               - Look for "Section C" or "Bahagian C" text to determine Section C's start page (Section C's start page marks the end of Section B)
               - Don't assume fixed start pages (document may have cover pages, formula sheets, etc.)
            
            2. Section End Pages:
               - Section A ends at (Section B start page - 1)
               - Section B ends at (Section C start page - 1)
               - Section C ends at the last page of the document
               
            3. Example:
               If sections are found on these pages:
               - Section A: found on page 4
               - Section B: found on page 21
               - Section C: found on page 27
               
               Then the full ranges should be:
               - Section A: pages 4-20
               - Section B: pages 21-26
               - Section C: pages 27-end
               
            4. Important:
               - Never assume fixed starting pages
               - Look for section titles in text to determine start pages
               - Each section's end page must connect to next section's start page
               - Last section (C) extends to document end
        """},
        {"text": """
            ADDITIONAL JSON FORMATTING RULES:
            1. String Escaping and Line Length:
               - Use proper escape sequences for newlines: "\\n" (not "n")
               - Keep lines under 2000 characters
               - Split long text using proper "\\n"
               - Use array of strings for very long text
               Example:
               WRONG: 
                 "text": "First line nSecond line"
               CORRECT:
                 "text": "First line\\nSecond line"
               
               For very long text:
               "text": [
                 "First part of long text...",
                 "Second part of long text..."
               ]
        """},
        {"text": """
            JSON VALIDATION RULES:
            1. Property Names:
               - ALL property names must be in double quotes
               - Common properties: "type", "text", "malay", "english", "number", "marks", "content_flow"
               
            2. Response Size:
               - Keep responses concise
               - Split long text into smaller chunks
               - Use line breaks only when necessary
               
            3. Structure Completion:
               - Every opening brace/bracket must have a closing pair
               - Every property must have a value
               - Arrays must end with proper closing brackets
               
            4. Common Issues to Avoid:
               - Unquoted property names
               - Truncated responses
               - Incomplete JSON structures
               - Missing closing braces/brackets
        """},
        {"text": """
            QUESTION NESTING RULES:
            1. Critical Structure Rules:
               - sub_questions MUST be nested inside their parent question
               - NEVER place sub_questions as a separate object
               - WRONG:
                 [
                   { "number": "2(b)", "content_flow": [...] },
                   { "sub_questions": [...] }
                 ]
               - CORRECT:
                 [
                   {
                     "number": "2(b)",
                     "content_flow": [...],
                     "sub_questions": [...]
                   }
                 ]
               
            2. Nesting Validation:
               - Every question with sub-questions must contain them inside its own object
               - Check that sub_questions array is a property of its parent question
               - Verify nesting depth matches question numbering
        """},
        {"text": """
            ARRAY HANDLING RULES:
            1. Sub-questions Array:
               - Each question can have ONLY ONE sub_questions array
               - WRONG:
                 {
                   "number": "3(c)",
                   "sub_questions": [...],
                   "sub_questions": [...]  // DUPLICATE!
                 }
               - CORRECT:
                 {
                   "number": "3(c)",
                   "sub_questions": [
                     {"number": "3(c)(i)", ...},
                     {"number": "3(c)(ii)", ...}
                   ]
                 }

            2. Array Delimiters:
               - Use comma between array elements
               - No comma after last element
               - WRONG: ["a", "b",]
               - CORRECT: ["a", "b"]
               
            3. Array Nesting:
               - Keep all related sub-questions in ONE array
               - Don't create separate arrays for each sub-question
               - Group all sub-questions of same parent together
        """},
        {"text": """
            ARRAY AND OBJECT STRUCTURE RULES:
            1. Content Flow Array:
               - Must only contain content items
               - WRONG:
                 "content_flow": [
                   {"type": "text", ...},
                   {"type": "answer_space", ...},
                   "sub_questions": []  // WRONG PLACEMENT!
                 ]
               - CORRECT:
                 {
                   "content_flow": [
                     {"type": "text", ...},
                     {"type": "answer_space", ...}
                   ],
                   "sub_questions": []  // CORRECT PLACEMENT
                 }
               
            2. Array Separators:
               - Every array element must be followed by a comma EXCEPT the last one
               - Every object property must be followed by a comma EXCEPT the last one
               - Example:
                 WRONG:
                   "content_flow": [
                     {"type": "text"} // Missing comma!
                     {"type": "answer_space"}
                   ]
                 CORRECT:
                   "content_flow": [
                     {"type": "text"},
                     {"type": "answer_space"}
                   ]
        """},
        {"text": """
            VERIFICATION CHECKLIST:
            1. Did you extract ALL questions from the PDF? (1-8 for Section A)
            2. Is every piece of content different from the reference?
            3. Are all questions properly numbered and sequential?
            4. Have you included all required fields for each question?
            5. Are languages properly separated (no mixing)?
            6. Are newlines only used within same language text?
            
            ⚠️ FINAL CHECK:
            - Compare your output with reference
            - If ANY content matches reference exactly, REGENERATE with new content
            - Ensure ALL questions (1-8) are included for Section A
            - Verify language separation is correct
            - Check font style to help identify languages
        """},
        {"text": """
            OBJECT BOUNDARY RULES:
            1. Array and Object Closure:
               - Close all arrays and objects before starting new ones
               - WRONG:
                 {
                   "sub_questions": []}, {"number": "2(b)(ii)"  // New object started before proper closure
                 }
               - CORRECT:
                 {
                   "sub_questions": [],
                   "number": "2(b)(ii)"  // Properties within same object
                 }
               
            2. Property Placement:
               - All related properties must be inside the same object
               - Don't start new object for related properties
               Example:
               WRONG:
                 {
                   "number": "2(b)",
                   "content_flow": [...]
                 },
                 {
                   "sub_questions": [...]  // Should be inside previous object
                 }
               CORRECT:
                 {
                   "number": "2(b)",
                   "content_flow": [...],
                   "sub_questions": [...]  // Properly nested
                 }
        """},
        {"text": """
            ARRAY NESTING AND COMMA RULES:
            1. Main Questions Structure:
               - main_questions array contains question objects
               - Each question object must have its questions array
               WRONG:
                 "main_questions": [{"number": "11"}],
                 "questions": [...]  // Separate array
               CORRECT:
                 "main_questions": [{
                   "number": "11",
                   "questions": [...]  // Nested inside main question
                 }]
               
            2. Empty Arrays:
               - Don't include empty arrays unless required
               - If including, place them at correct level
               WRONG:
                 "content_flow": [
                   {"type": "text"},
                   "sub_questions": []  // Wrong placement
                 ]
               CORRECT:
                 {
                   "content_flow": [
                     {"type": "text"}
                   ],
                   "sub_questions": []  // Correct placement
                 }
               
            3. Array Element Separation:
               - ALWAYS use comma between array elements
               - NEVER use comma after last element
               Example:
               WRONG:
                 [
                   {"type": "text"}  // Missing comma
                   {"type": "answer_space"}
                 ]
               CORRECT:
                 [
                   {"type": "text"},
                   {"type": "answer_space"}
                 ]
        """},
    ]
    
    response = model.generate_content(section_prompt)
    if not response:
        raise Exception("Failed to identify sections from the PDF.")
    
    try:
        sections_data = validate_response_sections(response.text)
        
        # Normalize section names and print section info
        for section in sections_data["sections"]:
            name = section["name"].lower()
            if 'bahagian a' in name or 'section a' in name:
                section["name"] = 'Section A'
            elif 'bahagian b' in name or 'section b' in name:
                section["name"] = 'Section B'
            elif 'bahagian c' in name or 'section c' in name:
                section["name"] = 'Section C'
                
            print(f"{section['name']} (pages {section['start_page']}-{section['end_page']})")
        
        # Validate that we found at least one section
        if not sections_data.get("sections") or len(sections_data["sections"]) == 0:
            raise ValueError("No sections (Section A/B/C or Bahagian A/B/C) were found in the PDF")
        
        # Validate each section has required fields
        for section in sections_data["sections"]:
            if not section.get("name"):
                raise ValueError("Section missing name field")
            if not isinstance(section.get("start_page"), (int, float)):
                raise ValueError(f"Invalid start_page for section {section.get('name')}")
            if not isinstance(section.get("end_page"), (int, float)):
                raise ValueError(f"Invalid end_page for section {section.get('name')}")
            if section["start_page"] > section["end_page"]:
                raise ValueError(f"Start page greater than end page for section {section['name']}")
        
        return sections_data
        
    except Exception as e:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_log_name = f'error_log_{timestamp}.txt'
        
        with open(error_log_name, 'w', encoding='utf-8') as f:
            f.write(f"Error identifying sections: {str(e)}\n")
            f.write(f"Model response:\n{response.text}")
            
        raise ValueError(f"Failed to identify sections properly: {str(e)}. See {error_log_name} for details")

# Validate Sections Response from Model
def validate_response_sections(response_text: str) -> dict:
    """Clean and validate the model response."""
    try:
        # First try direct parsing
        try:
            json_data = json.loads(response_text)
            return json_data
        except json.JSONDecodeError:
            pass

        # Basic cleaning
        cleaned_str = response_text.strip()
        start_idx = cleaned_str.find('{')
        end_idx = cleaned_str.rfind('}') + 1
        if start_idx != -1 and end_idx > 0:
            cleaned_str = cleaned_str[start_idx:end_idx]

        # Remove control characters and standardize whitespace
        cleaned_str = ''.join(char for char in cleaned_str if ord(char) >= 32 or char in '\n\r\t')
        cleaned_str = re.sub(r'\s+', ' ', cleaned_str)

        # Fix empty values - more comprehensive patterns
        patterns = [
            (r'"english"\s*:\s*","', '"english": ""'),
            (r'"answer_space"\s*:\s*","', '"answer_space": ""'),
            (r':\s*,([}\]])', r': ""}\1'),  # Fix empty values before closing brackets
            (r':\s*","', r': ""'),          # Fix any remaining empty values with commas
            (r':\s*,$', r': ""'),           # Fix empty values at line ends
        ]
        
        for pattern, replacement in patterns:
            cleaned_str = re.sub(pattern, replacement, cleaned_str)

        # Fix structural issues
        cleaned_str = re.sub(r'}\s*{', '},{', cleaned_str)  # Fix object concatenation
        cleaned_str = re.sub(r']\s*\[', '],[', cleaned_str)  # Fix array concatenation
        cleaned_str = re.sub(r'}\s*\[', '},[', cleaned_str)  # Fix object-array transition
        cleaned_str = re.sub(r']\s*{', '],{', cleaned_str)  # Fix array-object transition

        try:
            return json.loads(cleaned_str)
        except json.JSONDecodeError as e:
            start_pos = max(0, e.pos - 50)
            end_pos = min(len(cleaned_str), e.pos + 50)
            context = cleaned_str[start_pos:end_pos]
            
            error_log = log_error(
                f"JSON Parsing Error near: ...{context}...\n"
                f"Position: {e.pos}, Line: {e.lineno}, Column: {e.colno}",
                cleaned_str
            )
            raise ValueError(f"Failed to parse JSON after cleaning. See {error_log} for details")

    except Exception as e:
        if not str(e).startswith('Failed to parse JSON'):
            error_log = log_error(f"Unexpected error: {str(e)}")
            raise ValueError(f"Failed to process response: {str(e)}. See {error_log} for details")
        raise
      
# Load Reference PDF
def get_reference_pdf_content() -> str:
    """Get the reference PDF content."""
    reference_pdf_path = 'reference_files/reference_input.pdf'
    
    if not os.path.exists(reference_pdf_path):
        raise ValueError(f"Reference PDF not found: {reference_pdf_path}")
        
    with open(reference_pdf_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

# Extract Section Data
async def extract_section_data(model, pdf_content_base64: str, section_info: dict) -> dict:
    """Extract data for a specific section using the appropriate reference structure."""
    
    # Get reference materials
    reference_pdf_content_base64 = get_reference_pdf_content()
    
    # Select reference structure and page range based on section name
    reference_config = {
        'Section A': {'file': 'reference_files/reference_output_A.json', 'start_page': 4, 'end_page': 26},
        'Section B': {'file': 'reference_files/reference_output_B.json', 'start_page': 27, 'end_page': 32},
        'Section C': {'file': 'reference_files/reference_output_C.json', 'start_page': 33, 'end_page': 35}
    }.get(section_info['name'])
    
    if not reference_config:
        raise ValueError(f"Unknown section name: {section_info['name']}")
        
    # Load the appropriate reference structure
    try:
        with open(reference_config['file'], 'r', encoding='utf-8') as f:
            reference_structure = f.read()
    except FileNotFoundError:
        raise ValueError(f"Reference file not found: {reference_config['file']}")

    section_prompt = [
        {"text": """You are an Exam Paper Structure Extractor. Your task is to:
        
        1. ANALYZE THE PROVIDED PDF CONTENT ONLY
        2. CREATE NEW JSON based on the PDF content
        3. ⚠️ NEVER COPY FROM THE REFERENCE JSON
        
        CRITICAL WARNING:
        - The reference materials are ONLY for structure guidance
        - You must EXTRACT NEW CONTENT from the target PDF
        - COPYING from reference will cause FAILURE
        - Each question must be uniquely extracted from the target PDF"""},
        {"text": f"First, study this REFERENCE PDF (Pages {reference_config['start_page']} to {reference_config['end_page']}) and its corresponding JSON structure:"},
        {'mime_type': 'application/pdf', 'data': reference_pdf_content_base64},
        {"text": "This is how the above reference PDF section was correctly extracted:"},
        {"text": reference_structure},
        {"text": f"Now, ANALYZE YOUR TARGET PDF SECTION (Pages {section_info['start_page']} to {section_info['end_page']}):"},
        {'mime_type': 'application/pdf', 'data': pdf_content_base64},
        {"text": f"""
            Extract ALL questions from {section_info['name']} section 
            (pages {section_info['start_page']} to {section_info['end_page']}).
            
            LANGUAGE SEPARATION RULES:
            1. DO NOT mix Malay and English in the same text field
            2. Only use "\\n" (new line) if:
               - The next line is in the SAME language as the previous line
               - Both lines are part of the same continuous text
            3. Language Identification Tips:
               - English text is usually in italic font
               - Malay text is usually in normal/regular font
               - Each question typically has both versions
               
            Example CORRECT format:
            {{
                "text": {{
                    "malay": "Baris pertama\\nBaris kedua",
                    "english": "First line\\nSecond line"
                }}
            }}
            
            Example WRONG format:
            {{
                "text": {{
                    "malay": "Baris pertama\\nFirst line",
                    "english": "Mixed language\\nBaris kedua"
                }}
            }}
            
            DIAGRAM LAYOUT RULES:
            1. Vertical Layout (Most Common):
               - Diagrams stacked one above another
               - Each diagram takes full width
               - Extract as separate diagram entries:
               [
                  {{
                     "type": "diagram",
                     "name": "Rajah 11.1",
                     "page": 27
                  }},
                  {{
                     "type": "diagram",
                     "name": "Rajah 11.2",
                     "page": 27
                  }}
               ]
               
            2. Side-by-Side Layout (Only if clearly horizontal):
               - Diagrams appear next to each other
               - Clearly sharing the same horizontal space
               - Use row layout ONLY in this case:
               {{
                  "type": "row",
                  "layout": "2-columns",
                  "items": [
                     {{ "type": "diagram", "name": "Diagram 2.1", "page": 5 }},
                     {{ "type": "diagram", "name": "Diagram 2.2", "page": 5 }}
                  ]
               }}
            
            ⚠️ IMPORTANT:
            - Default to vertical layout unless diagrams are clearly side-by-side
            - Do not use row layout for diagrams that appear on different vertical positions
            - Check if diagrams share the same horizontal line before using 2-columns
        """},
        {"text": reference_structure},
        {"text": f"""
            ANSWER SPACE IDENTIFICATION RULES:
            1. Visual Cues:
               - Single-line: One thin line or small box for short answers
               - Multi-line: Multiple lines or large box for paragraphs
               - Blank-space: Large empty area with no lines
               - Multiple-choice: Boxes/circles for ticking/filling

            2. Marks-based Hints:
               - 1 mark questions typically use single-line answers
               - 2-3 marks may use single or multi-line based on context
               - 4+ marks usually require multi-line answers
               
            3. Question Context:
               - Calculation questions usually need single-line for final answer
               - "Name/State/List" typically needs single-line
               - "Explain/Describe/Discuss" typically needs multi-line
               - "Fill in the blanks" always uses single-line
               
            Example formats:
            1. Single-line answer:
            {{
                "type": "answer_space",
                "format": "single-line"
            }}
            
            2. Multi-line answer:
            {{
                "type": "answer_space",
                "format": "multi-line",
                "lines": 4  // if number of lines is visible
            }}
        """},
        {"text": """
            QUESTION NESTING RULES:
            1. Question Numbering Patterns:
               - Main questions use numbers: "11"
               - First level questions use letters: "11(a)", "11(b)"
               - Second level sub-questions use roman numerals: "11(a)(i)", "11(a)(ii)"
               
            2. Nesting Structure Example:
               {{
                 "number": "11(a)",
                 "content_flow": [...],
                 "sub_questions": [
                   {{
                     "number": "11(a)(i)",
                     "marks": 1,
                     "content_flow": [...]
                   }},
                   {{
                     "number": "11(a)(ii)",
                     "marks": 5,
                     "content_flow": [...]
                   }}
                 ]
               }}
               
            3. Critical Rules:
               - NEVER place sub_questions array at the same level as questions array (as a separate object)
               - Each question can only contain sub_questions if it has them
               - Questions without sub-questions should not have the sub_questions field
               - sub_questions MUST be nested inside their parent question
               - WRONG:
                 [
                   { "number": "2(b)", "content_flow": [...] },
                   { "sub_questions": [...] }
                 ]
               - CORRECT:
                 [
                   {
                     "number": "2(b)",
                     "content_flow": [...],
                     "sub_questions": [...]
                   }
                 ]
            4. Nesting Validation:
               - Every question with sub-questions must contain them inside its own object
               - Check that sub_questions array is a property of its parent question
               - Verify nesting depth matches question numbering
               
            5. Question Identification Rules:
               - Look for complete question numbers (e.g., "11(a)(i)")
               - Don't split "(a)(i)" into separate "(a)" and "(i)" questions
               - Check mark allocations to verify question boundaries
               - Maintain proper nesting depth based on numbering format
        """},
        {"text": """
            VERIFICATION CHECKLIST:
            1. Did you extract ALL questions from the PDF? (1-8 for Section A)
            2. Is every piece of content different from the reference?
            3. Are all questions properly numbered and sequential?
            4. Have you included all required fields for each question?
            5. Are languages properly separated (no mixing)?
            6. Are newlines only used within same language text?
            
            ⚠️ FINAL CHECK:
            - Compare your output with reference
            - If ANY content matches reference exactly, REGENERATE with new content
            - Ensure ALL questions (1-8) are included for Section A
            - Verify language separation is correct
            - Check font style to help identify languages
            
        **MOST IMPORTANT (VERY STRICT): MAKE SURE THAT YOU ARE RETURNING A VALID JSON OBJECT**
        Ensure:
        1. All keys and values are wrapped in double quotes.
        2. There are no trailing commas.
        3. Proper nesting of brackets and braces.
        4. The response is fully valid JSON.

        If necessary, verify your JSON before responding.
        """},
        {"text": "Return only a valid JSON object. No explanations. No markdown formatting. Just JSON."}
    ]
    
    try:
        print("Waiting for response from model...")
        response = model.generate_content(section_prompt)
        if not response:
            raise Exception("Failed to get response from model")
        
        # Fix model generated JSON before validation
        fixed_json = fix_json_string(response.text)
        # Validate Section Content (Section A, B, C)
        validate_section_content(fixed_json, section_info['name'])
        return fixed_json
        
    except Exception as e:
        print(f"Error in extract_section_data: {str(e)}")
        # Create error log for debugging
        error_log = f"error_logs/error_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(error_log, "w", encoding='utf-8') as f:
            f.write(f"Error: {str(e)}\n\n")
            if 'response' in locals():
                f.write(f"Response text:\n{response.text}")
        raise ValueError(f"Error extracting section data: {str(e)}")

# Fix generated JSON
def fix_json_string(json_string: str) -> str:
    # Cleans a JSON string by removing unnecessary escape characters, newline characters, and extra spaces.
    try:
        # Decode JSON string to remove unnecessary escape characters
        cleaned_json = json.loads(json_string)
        # Re-encode to a properly formatted JSON string with compact representation
        return json.dumps(cleaned_json, ensure_ascii=False, separators=(",", ":"))
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return json_string  # Return the original string if decoding fails

# Validate if Sections A, B, C has all the required questions
def validate_section_content(section_data: str, section_name: str) -> None:
    # Validate section content meets requirements.
    try:
        # Parse the JSON string into a dictionary
        data = json.loads(section_data)
        
        if section_name in ['Bahagian A', 'Section A']:
            # Check number of main questions
            main_questions = data.get('main_questions', [])
            question_numbers = [q.get('number') for q in main_questions]
            expected_numbers = [str(i) for i in range(1, 9)]  # 1 to 8
            
            missing = set(expected_numbers) - set(question_numbers)
            if missing:
                logging.warning(f"Section A is missing questions: {', '.join(missing)}")
                # No longer raising an error, just logging a warning
        
        if section_name in ['Bahagian B', 'Section B']:
            # Check number of main questions
            main_questions = data.get('main_questions', [])
            question_numbers = [q.get('number') for q in main_questions]
            expected_numbers = [str(i) for i in range(9, 11)]  # 9 to 10
            
            missing = set(expected_numbers) - set(question_numbers)
            if missing:
                logging.warning(f"Section B is missing questions: {', '.join(missing)}")
        
        if section_name in ['Bahagian C', 'Section C']:
            # Check number of main questions
            main_questions = data.get('main_questions', [])
            question_numbers = [q.get('number') for q in main_questions]
            expected_numbers = ['12']
            missing = set(expected_numbers) - set(question_numbers)
            if missing:
                logging.warning(f"Section C is missing questions: {', '.join(missing)}")
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON format: {str(e)}")
        # Still raise error for invalid JSON as this is a critical error
        raise

# Main Function
@app.post("/extract_questions")
async def analyse_pdf(pdf_file: UploadFile = File(...)):
    try:
        if not pdf_file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Input PDF file must end with .pdf")

        user_pdf_content = await pdf_file.read()
        user_pdf_content_base64 = base64.standard_b64encode(user_pdf_content).decode("utf-8")

        model = configure_model()
        
        # Step 1: Identify sections and their page ranges
        print("Identifying sections...")
        sections_data = await identify_sections(model, user_pdf_content_base64)
        
        # Step 2: Extract data for each section
        # NOTE: Gemini is inconsistent in giving valid JSONs (Sometimes ok sometimes not)
        # Consider cleaning the JSONs (which i've done but errors like delimiter, and double quotes still persists)
        print("Extracting data from sections...")
        all_sections_data = []
        for section in sections_data["sections"]:
            print(f"Processing section: {section['name']}")
            section_data = await extract_section_data(
                model, 
                user_pdf_content_base64, 
                section
            )
            all_sections_data.append(section_data)
        
        # Step 3: Combine results
        combined_data = {
            "sections": all_sections_data
        }
        
        return {
            "status": "success",
            "message": "Successfully extracted all sections",
            "data": combined_data
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e), "data": None}
        )