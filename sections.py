import json
from datetime import datetime
import re

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
  