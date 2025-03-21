from datetime import datetime
from modules.utils import get_last_page  

def build_identify_sections_prompt():
    return f"""
        ANALYZE THIS PDF AND IDENTIFY THE MAIN SECTIONS:
        Identify the **start pages** for the main sections in this PDF marked by 'Section A/B/C' or 'Bahagian A/B/C'.
        
        Return the result as JSON in this format:
        ```json
        {{
            "sections": {{
                "A": start_page_number,
                "B": start_page_number,
                "C": start_page_number
            }},
            "first_page_number": first_page_number
        }}
        ```
        
        **Rules for Identifying Sections:**
        - Look for **"Section A" / "Bahagian A"** and return the page number as shown in the PDF.
        - Look for **"Section B" / "Bahagian B"** and return the page number as shown in the PDF.
        - Look for **"Section C" / "Bahagian C"** and return the page number as shown in the PDF.
        - Also identify the first page number shown in the PDF (e.g., if PDF starts at page 4, return 4).
        - Do **not** calculate the end pages.
    """

async def identify_sections(response, pdf_content):
    try:
        section_start_pages = response
        start_C = int(section_start_pages["sections"]["C"])
        start_A = int(section_start_pages["sections"]["A"])
        start_B = int(section_start_pages["sections"]["B"])
        first_page = int(section_start_pages.get("first_page_number", 1))  # Default to 1 if not provided
        
        # Calculate the page offset
        offset = first_page - 1
        last_page = get_last_page(pdf_content) + offset
        
        sections_data = [
            {"name": "Section A", "start_page": start_A, "end_page": start_B - 1},
            {"name": "Section B", "start_page": start_B, "end_page": start_C - 1},
            {"name": "Section C", "start_page": start_C, "end_page": last_page}
        ]

        # Normalize section names and print section info
        for section in sections_data:
            name = section["name"].lower()
            if 'bahagian a' in name or 'section a' in name:
                section["name"] = 'Section A'
            elif 'bahagian b' in name or 'section b' in name:
                section["name"] = 'Section B'
            elif 'bahagian c' in name or 'section c' in name:
                section["name"] = 'Section C'
                
            print(f"{section['name']} (pages {section['start_page']}-{section['end_page']})")
        
        # Validate that we found at least one section
        if not sections_data or len(sections_data) == 0:
            raise ValueError("No sections (Section A/B/C or Bahagian A/B/C) were found in the PDF")
        
        # Validate each section has required fields
        for section in sections_data:  # Directly iterate over the list
            if not section.get("name"):
                raise ValueError("Section missing name field")
            if not isinstance(section.get("start_page"), (int, float)):
                raise ValueError(f"Invalid start_page for section {section.get('name')}")
            if not isinstance(section.get("end_page"), (int, float)):
                raise ValueError(f"Invalid end_page for section {section['name']}")
            if section["start_page"] > section["end_page"]:
                raise ValueError(f"Start page greater than end page for section {section['name']}")

        
        return sections_data
        
    except Exception as e:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_log_name = f'error_log_{timestamp}.txt'
        
        with open(error_log_name, 'w', encoding='utf-8') as f:
            f.write(f"Error identifying sections: {str(e)}\n")
            # f.write(f"Model response:\n{response.text}")
            
        raise ValueError(f"Failed to identify sections properly: {str(e)}. See {error_log_name} for details")
