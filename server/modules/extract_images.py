import json
import os
import fitz  # PyMuPDF
import cv2
import numpy as np
from ultralytics import YOLO
import easyocr
import re
import copy

# --- find_objects ---
def find_objects(data_structure, target_types):
    """Recursively find all objects of specified types, even when nested."""
    found_objects = []
    if isinstance(data_structure, dict):
        if data_structure.get("type") in target_types:
            found_objects.append(data_structure)
        
        for value in data_structure.values():
            found_objects.extend(find_objects(value, target_types))

    elif isinstance(data_structure, list):
        for item in data_structure:
            found_objects.extend(find_objects(item, target_types))
            
    return found_objects

# --- merge_urls_into_json ---
def merge_urls_into_json(data_structure, match_dictionary):
    """Recursively traverses the JSON and adds the 'url' where data matches."""
    if isinstance(data_structure, dict):
        obj_type = data_structure.get("type")
        obj_page = data_structure.get("page")
        obj_number = data_structure.get("number")
        # Only clean obj_number if it's not None
        if obj_number is not None:
            obj_number_clean = str(obj_number).replace(' ', '')
        else:
            obj_number_clean = None

        # Check if the current dictionary is a target we need to update
        if obj_type and obj_page and obj_number_clean:
            match_key = (int(obj_page), obj_type, obj_number_clean)
            if match_key in match_dictionary:
                data_structure['url'] = match_dictionary[match_key]

        # This allows the function to find content nested within other objects.
        for value in data_structure.values():
            merge_urls_into_json(value, match_dictionary)

    elif isinstance(data_structure, list):
        for item in data_structure:
            merge_urls_into_json(item, match_dictionary)

def run_pipeline(pdf, page_numbers, model, reader, supabase_client, bucket_name, document_id):
    """
    The main pipeline: detects, crops, OCRs, uploads to Supabase, and returns structured data.
    """
    all_detections = []
    doc = fitz.Document(stream=pdf)

    for page_num in page_numbers:
        print(f"Processing page {page_num}...")
        page = doc.load_page(page_num - 1)
        pix = page.get_pixmap(dpi=300)
  
        # Convert to OpenCV image
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        # 1. Run YOLO detection
        results = model(img_bgr, conf=0.5)

        # 2. Process each detection
        for result in results:
            for i, box in enumerate(result.boxes.xyxy):
                class_id = int(result.boxes.cls[i])
                class_name = model.names[class_id]

                if class_name not in ['diagram', 'table']:
                    continue

                x1, y1, x2, y2 = map(int, box)
                
                # --- OCR on Caption Area ---
                caption_area = img_bgr[y2:min(y2 + 250, img_bgr.shape[0]), x1:x2]
                if caption_area.size == 0: continue
                
                # Run OCR on the caption area
                ocr_result = reader.readtext(caption_area, detail=0, paragraph=True, blocklist='&')
                ocr_text = ocr_result[0] if ocr_result else ""
                print(f"  -> OCR Text: {ocr_text}")
                
                object_number = None
    
                diagram_pattern = r'(Rajah|Diagram)\s*([\d\.]+(?:\s*\([a-hA-H]\))?)'
                table_pattern = r'(Jadual|Table)\s*([\d\.]+(?:\s*\([a-hA-H]\))?)'
                
                # Find all matches in the OCR text
                all_diagram_matches = re.findall(diagram_pattern, ocr_text, re.IGNORECASE)
                all_table_matches = re.findall(table_pattern, ocr_text, re.IGNORECASE)
                
                object_number = "NA"
                if all_diagram_matches and class_name == 'diagram':
                    print('Caption below diagram matched!')
                    # The result is a list of tuples, e.g., [('Rajah', '1(b)'), ('Diagram', '11(b)')]
                
                    # Sort the matches based on the length of the number string
                    best_match = max(all_diagram_matches, key=lambda match: len(match[1]))
                    
                    # The longest number is the second item in the best_match tuple
                    object_number = best_match[1].strip()
                    object_number = object_number.replace(' ', '')
                elif all_table_matches and class_name == 'table':
                    print('Caption below table matched!')
                    best_match = max(all_table_matches, key=lambda match: len(match[1]))
                    object_number = best_match[1].strip()
                    object_number = object_number.replace(' ', '')
                else:
                    print('No caption below matched, checking above diagam/table...')
                    caption_area_above = img_bgr[max(y1 - 250, 0):y1, x1-250:x2]
                    if caption_area_above.size == 0: continue
                    ocr_result_above = reader.readtext(caption_area_above, detail=0, paragraph=True)
                    ocr_text_above = " ".join(ocr_result_above)
                    
                    all_diagram_matches_above = re.findall(diagram_pattern, ocr_text_above, re.IGNORECASE)
                    all_table_matches_above = re.findall(table_pattern, ocr_text_above, re.IGNORECASE)
                    if all_diagram_matches_above and class_name == 'diagram':
                        print('Diagram number above diagram matched!')
                        best_match = max(all_diagram_matches_above, key=lambda match: len(match[1]))
                        object_number = best_match[1].strip()
                        object_number = object_number.replace(' ', '')
                    elif all_table_matches_above and class_name == 'table':
                        print('Table number above table matched!')
                        best_match = max(all_table_matches_above, key=lambda match: len(match[1]))
                        object_number = best_match[1].strip()
                        object_number = object_number.replace(' ', '')
                    else:
                        print('No number above found, checking previous page...')
                        # Run OCR detection on the full previous page
                        prev_page = doc.load_page(page_num - 2)
                        prev_pix = prev_page.get_pixmap(dpi=300)
                        prev_img_array = np.frombuffer(prev_pix.samples, dtype=np.uint8).reshape(prev_pix.height, prev_pix.width, prev_pix.n)
                        prev_img_bgr = cv2.cvtColor(prev_img_array, cv2.COLOR_RGB2BGR)
                        prev_ocr_result = reader.readtext(prev_img_bgr, detail=0, paragraph=True)
                        prev_ocr_text = " ".join(prev_ocr_result)
                        print(f"Previous page OCR: {prev_ocr_text}")
                        # Find all matches for diagram and table on the previous page
                        all_diagram_matches_prev = list(re.finditer(r'(Rajah|Diagram)\s*([\d\.]+)\s*(\([a-zA-Z0-9]+\))?', prev_ocr_text, re.IGNORECASE))
                        all_table_matches_prev = list(re.finditer(r'(Jadual|Table)\s*([\d\.]+)\s*(\([a-zA-Z0-9]+\))?', prev_ocr_text, re.IGNORECASE))
                        
                        print('diagram matches:', all_diagram_matches_prev)
                        print('table matches:', all_table_matches_prev)
                        # Get the last match for the correct class
                        if class_name == 'diagram' and all_diagram_matches_prev:
                            print('Diagram number on previous page found!')
                            last_match = all_diagram_matches_prev[-1]
                            object_number = last_match.group(2)
                            if last_match.group(3):
                                object_number += last_match.group(3)
                        elif class_name == 'table' and all_table_matches_prev:
                            print('Table number on previous page found!')
                            last_match = all_table_matches_prev[-1]
                            object_number = last_match.group(2)
                            if last_match.group(3):
                                object_number += last_match.group(3)

                if not object_number:
                    print(f"  -> Warning: Could not find number for a {class_name} on page {page_num}. Skipping upload.")
                    continue
                
                # --- Crop, Upload, and Get URL ---
                try:
                    # 1. Crop the detected object from the original image
                    cropped_image = img_bgr[y1:y2, x1:x2]

                    # 2. Encode image to bytes to upload from memory
                    _, buffer = cv2.imencode('.jpg', cropped_image)
                    image_bytes = buffer.tobytes()

                    # 3. Upload to Supabase
                    file_path = f"{document_id}/page_{page_num}_{class_name}_{object_number}.jpg"
                    print(f"  -> Uploading {file_path} to Supabase...")
                    supabase_client.storage.from_(bucket_name).upload(
                        file=image_bytes,
                        path=file_path,
                        file_options={"content-type": "image/jpeg", "upsert": "true"}
                    )

                    # 4. Get the public URL
                    image_url = supabase_client.storage.from_(bucket_name).get_public_url(file_path)
                    print(f"  -> Success! URL: {image_url}")

                    # 5. Store all collected data
                    all_detections.append({
                        "page": page_num,
                        "type": class_name,
                        "number": object_number,
                        "url": image_url
                    })
                except Exception as e:
                    print(f"  -> ERROR during Supabase upload: {e}")

    doc.close()
    return all_detections

# --- Main Script Execution ---
def get_images_and_update_json(original_json_data, pdf, supabase, bucket_name, document_id):
    # ✅ FIX: Create a deep copy immediately to avoid modifying the original data.
    json_with_urls = copy.deepcopy(original_json_data)
    
    # --- 1. Load Models ---
    print("Loading models...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model = YOLO(os.path.join(base_dir, "..", "assets", "my_model.pt"))
    reader = easyocr.Reader(['en'], gpu=False)
    
    # --- 2. Identify Target Pages (now working on the copied data) ---
    types_to_find = ["diagram", "table"]
    found_items = find_objects(json_with_urls, types_to_find)
    page_numbers = sorted(set(int(item['page']) for item in found_items))
    print(f"Found pages to process: {page_numbers}\n")

    # --- 3. Run the Full Pipeline ---
    pipeline_results = run_pipeline(pdf, page_numbers, model, reader, supabase, bucket_name, document_id)

    # --- 4. Build the Match Dictionary ---
    print("\nBuilding match dictionary from results...")
    match_dict = {
        (item['page'], item['type'], item['number']): item['url']
        for item in pipeline_results
    }
    print(f"Match dictionary created with {len(match_dict)} entries.")

    # --- 5. Merge URLs into the copied JSON Data ---
    print("Merging URLs back into the JSON structure...")
    merge_urls_into_json(json_with_urls, match_dict)
    
    print("Merging complete.")
    # Return the newly modified copy
    return json_with_urls