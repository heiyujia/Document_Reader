import PyPDF2
import easyocr
import fitz  
import tempfile
import langdetect

class TextExtractor:
    
    def __init__(self, file_path, temp_file_path):
        self.file_path = file_path
        self.temp = temp_file_path
        self.language = self.detect_language()
        self.OCR_reader = easyocr.Reader([self.language])
        
    def detect_language(self):
        """detect document language to initialize ocr reader"""
        try:
            with open(self.file_path, 'rb') as file:
                sample_text = file.read(1024)  # read the first 1kB content to detect language
            detected_lang = langdetect.detect(sample_text.decode('utf-8', errors='ignore'))
            
            if detected_lang == 'zh-cn' or detected_lang == 'zh-tw':
                return 'ch'  
            elif detected_lang in ['en', 'de']:
                return detected_lang
            else:
                return 'de'
            
        except:
            return 'de'  
    
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
    
    def extract_text_from_image(self):
        ocr_result = self.OCR_reader.readtext(self.file_path, detail=0)
        text = " ".join(ocr_result)
        return text.strip()
    
    def extract_text_from_txt(self):
        """read text from txt file"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return text.strip()
        except:
            return ""