import os
import json
import PyPDF2
import easyocr
import fitz  
import tempfile

class TextExtractor:
    
    def __init__(self, file_path, temp_file_path):
        self.file_path = file_path
        self.temp = temp_file_path
        self.OCR_reader = easyocr.Reader(['en', 'de']) ## tpdo: use langdetect to detect language initializing easyOCR
    
    def extract_text_from_pdf(self):
        """extract text from pdf"""
        text = ""
        with open(self.file_path, 'rb') as file:
            # get the page num
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
        
            # process every page
            for page_num in range(num_pages):
                # extract every page
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()

                # if not sucess with PyPDF2
                if not page_text.strip():
                    
                    # transfer page to image using OCR
                    pdf_document = fitz.open(self.file_path)
                    page_image = pdf_document[page_num].get_pixmap()  # get image
                    
                    # use tempfile create temp file
                    with tempfile.NamedTemporaryFile(delete=True, suffix='.png', dir=self.temp) as temp_img:
                        img_path = temp_img.name  # get the temp path
                        page_image.save(img_path)  # save image in temp file
                        # use easyOCR to read
                        ocr_result = self.OCR_reader.readtext(img_path, detail=0)
                        page_text = " ".join(ocr_result)
                
                        text += page_text + "\n"
        
        return text.strip()
