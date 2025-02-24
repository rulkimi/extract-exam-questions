import json
import logging

def build_extract_section_data_prompt(section_info: dict):
    reference_sections = {
        'Section A': {'file': 'reference_files/with_sections/reference_output_A.json', 'start_page': 4, 'end_page': 26},
        'Section B': {'file': 'reference_files/with_sections/reference_output_B.json', 'start_page': 27, 'end_page': 32},
        'Section C': {'file': 'reference_files/with_sections/reference_output_C.json', 'start_page': 33, 'end_page': 35}
    }
    reference_config = reference_sections.get(section_info['name'])
    
    if not reference_config:
        raise ValueError(f"Unknown section name: {section_info['name']}")
        
    # Load the appropriate reference structure
    try:
        with open(reference_config['file'], 'r', encoding='utf-8') as f:
            reference_structure = f.read()
    except FileNotFoundError:
        raise ValueError(f"Reference file not found: {reference_config['file']}")

    question_range = ""
    if section_info['name'] == 'Bahagian A' or section_info['name'] == 'Section A':
        question_range = "1-8"
    elif section_info['name'] == 'Bahagian B' or section_info['name'] == 'Section B':
        question_range = "9-10"
    elif section_info['name'] == 'Bahagian C' or section_info['name'] == 'Section C':
        question_range = "11"

    section_prompt = f"""
        You are an Exam Paper Structure Extractor. Your task is to:
        
        1. ANALYZE THE PROVIDED PDF CONTENT ONLY
        2. CREATE NEW JSON based on the PDF content
        3. NEVER COPY FROM THE REFERENCE JSON

        First, study the REFERENCE PDF (First PDF) (Pages {reference_config['start_page']} to {reference_config['end_page']}) and its corresponding JSON structure
        Below is how the reference pdf section was correctly extracted:
        {reference_structure}

        Now, ANALYZE YOUR TARGET PDF (Second PDF) SECTION: {section_info['name']}, Pages {section_info['start_page']} to {section_info['end_page']}, and extract questions {question_range}:
        same structure: 
        {reference_structure}

        Return only a valid JSON object. No explanations. No markdown formatting. No unnecessary backslashes \\. Just JSON.
    """
    return section_prompt

# Validate if Sections A, B, C has all the required questions
def validate_section_content(section_data: str, section_name: str) -> None:
    # Validate section content meets requirements.
    try:
        # Parse the JSON string into a dictionary
        data = json.loads(section_data)
        
        if section_name in ['Bahagian A', 'Section A']:
            # Check number of main questions
            main_questions = data.get('main_questions', [])
            question_numbers = [str(q.get('number')) for q in main_questions]  # Convert to strings
            expected_numbers = [str(i) for i in range(1, 9)]  # 1 to 8
            
            missing = set(expected_numbers) - set(question_numbers)
            if missing:
                logging.warning(f"Section A is missing questions: {', '.join(missing)}")
                # No longer raising an error, just logging a warning
        
        if section_name in ['Bahagian B', 'Section B']:
            # Check number of main questions
            main_questions = data.get('main_questions', [])
            question_numbers = [str(q.get('number')) for q in main_questions]
            expected_numbers = [str(i) for i in range(9, 11)]  # 9 to 10
            
            missing = set(expected_numbers) - set(question_numbers)
            if missing:
                logging.warning(f"Section B is missing questions: {', '.join(missing)}")
        
        if section_name in ['Bahagian C', 'Section C']:
            # Check number of main questions
            main_questions = data.get('main_questions', [])
            question_numbers = [str(q.get('number')) for q in main_questions]
            expected_numbers = ['11']
            missing = set(expected_numbers) - set(question_numbers)
            if missing:
                logging.warning(f"Section C is missing questions: {', '.join(missing)}")
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON format: {str(e)}")
        # Still raise error for invalid JSON as this is a critical error
        raise
