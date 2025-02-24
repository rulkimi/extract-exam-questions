import fitz
import os

def get_last_page(pdf_content: bytes) -> int:
    """Returns the last page number of a PDF."""
    doc = fitz.open(stream=pdf_content, filetype="pdf")  # Open PDF from bytes
    last_page = len(doc)  # Get total page count
    doc.close()
    return last_page

def get_reference_pdf() -> str:
    """Get the reference PDF content."""
    reference_pdf_path = 'reference_files/reference_input.pdf'
    
    if not os.path.exists(reference_pdf_path):
        raise ValueError(f"Reference PDF not found: {reference_pdf_path}")
        
    with open(reference_pdf_path, 'rb') as f:
        return f.read()