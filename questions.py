import os
import base64
import json
from datetime import datetime
import logging

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
        # Normalize escaped characters and newline issues
        json_string = json_string.replace("\\n", " ").replace("\\t", " ")
        # Decode JSON string to remove unnecessary escape characters
        cleaned_json = json.loads(json_string)
        # Re-encode to a properly formatted JSON string with compact representation
        return json.dumps(cleaned_json, ensure_ascii=False, indent=4)
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
