# Function to build the structured prompt
def build_prompt(reference_json):
    # First ensure the reference_json is properly formatted
    try:
        if isinstance(reference_json, str):
            # If it's a string, parse it to ensure it's valid JSON
            import json
            json.loads(reference_json)
        else:
            # If it's already a dict/object, convert to string
            reference_json = json.dumps(reference_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid reference JSON provided: {e}")

    # Build the prompt with clearer instructions
    prompt = {
        "instructions": """CRITICAL INSTRUCTION: Your task is to analyze the FIRST PDF (user's PDF) and create a NEW JSON that follows the structure shown in the reference. DO NOT COPY the reference content.

STEP-BY-STEP PROCESS:
1. READ the user's PDF (first input) carefully
2. IDENTIFY these elements from the USER'S PDF:
   - Section titles (Bahagian A, B, C, etc.)
   - Instructions for each section
   - Questions and sub-questions
   - Diagrams and tables
   - Answer spaces
   - Marks allocation

3. CREATE NEW JSON using this exact structure:
   {
     "sections": [
       {
         "section_title": {
           "malay": "EXTRACT FROM USER PDF",
           "english": "EXTRACT FROM USER PDF"
         },
         "instructions": {
           "malay": "EXTRACT FROM USER PDF",
           "english": "EXTRACT FROM USER PDF"
         },
         ...
       }
     ]
   }

IMPORTANT RULES:
✖️ DO NOT COPY the reference content
✖️ DO NOT USE any text from the reference
✔️ ONLY USE content from the user's PDF
✔️ FOLLOW the reference structure
✔️ CREATE NEW content based on user's PDF

Example of WRONG output:
- Copying any content from reference JSON
- Returning empty or placeholder text
- Mixing content from reference and user PDF

Example of CORRECT output:
- New JSON with same structure
- All content extracted from user's PDF
- Proper bilingual text where available
- Accurate question numbering from user's PDF

The following shows ONLY the structure to follow (DO NOT COPY THIS CONTENT):
""",
        "reference": reference_json
    }
    return prompt
