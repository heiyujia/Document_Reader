import os
import shutil
import logging
from datetime import datetime
from inotify_simple import INotify, flags
from TextExtractor import TextExtractor
from chatGPT import AIAssistant
from Database.DBHandler import DatabaseManager

class DocumentReader:
    def __init__(self, watch_directory, handled_directory, temp_file, key_path, db_path):
        self.watch_directory = watch_directory
        self.handled_directory = handled_directory
        self.inotify = INotify()
        self.watch_flags = flags.CLOSE_WRITE | flags.MOVED_TO
        self.temp = temp_file
        self.key_path = key_path
        self.dbManager = DatabaseManager(db_path)
        self.dbManager.connect()

        # Set up logging
        self.setup_logging()
        
    def get_env_var(self):
        self.watch_directory = os.getenv(WATCH_DIRECTORY)
        self.handled_directory = os.getenv(HANDLED_DIRECTORY)
        
        if self.watch_directory or self.handled_directory is None:
            raise RuntimeError(f"Error: Required environment variables are not set.")
        
        print(f"using CHECK_INTERVAL: ", self.check_interval)

    def setup_logging(self):
        # Define the log file path
        LOG_DIR = "./log/"
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        LOG_FILE = f"DocumentReader_{current_time}.log"

        # Ensure the log directory exists
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

        # Full path to the log file
        log_file_path = os.path.join(LOG_DIR, LOG_FILE)

        # Setup logging configuration
        logging.basicConfig(
            filename=log_file_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def check_directory(self):
        """Check the directory and process new files"""
        files_in_directory = os.listdir(self.watch_directory)
        extracted_text = None
        text = None

        # Check if the directory is empty
        if not files_in_directory:
            logging.info(f"The directory '{self.watch_directory}' is empty.")
            return

        # Process each file based on its extension
        for filename in files_in_directory:
            # Build the full file path
            file_path = os.path.join(self.watch_directory, filename)
            # Process the file based on its extension
            if filename.lower().endswith('.pdf'):
                text_extractor = TextExtractor(file_path, self.temp)
                extracted_text = text_extractor.extract_text_from_pdf()
                logging.info(f"text has been extracted from pdf")
            elif filename.lower().endswith('.txt'):
                text_extractor = TextExtractor(file_path, self.temp)
                extracted_text = text_extractor.extract_text_from_txt()
                logging.info(f"text has been extracted from txt file")
            elif filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                text_extractor = TextExtractor(file_path, self.temp)
                extracted_text = text_extractor.extract_text_from_image()
                logging.info(f"text has been extracted from image")
            else:
                logging.info(f"unknow format document")
                
            ai_assistant = AIAssistant(KEY_PATH)
            if not extracted_text:
                logging.info(f"nothing in extracted_text")
                return
            else:
                text = ai_assistant.JsonFormatSummary(extracted_text)
                logging.info(f"get json format summary")
            
            text = text.replace("'", '"') # repair the problem caused by fine-tuning
            text = text.replace("None", '"N/A"')
            extension = os.path.splitext(filename)[1][1:].upper()  # Get extension and remove the dot
            extension_dir = os.path.join(self.handled_directory, extension)
            if not os.path.exists(extension_dir):
                os.makedirs(extension_dir)
            
            try:
                self.dbManager.insert_new_element(json_str=text, link=os.path.join(extension_dir, filename))
            except Exception as e:
                logging.error("insert_new_element error: %s", e)
            
            shutil.move(file_path, os.path.join(extension_dir, filename))
            logging.info(f"Moved file: {filename} to {extension_dir}")

    def run(self):
        """Run the document reader service"""
        
        try:    
            self.inotify.add_watch(self.watch_directory, self.watch_flags)    
            logging.info("Starting directory watch service...")

            while True:
                for event in self.inotify.read():
                    for flag in flags.from_mask(event.mask):
                        if flag == flags.CLOSE_WRITE or flags.MOVED_TO:
                            self.check_directory()
                            
        except KeyboardInterrupt:
            logging.info("Exiting the document reader service...")
            print(f"Exiting the document reader service...")
            self.dbManager.close()
            exit(0) 

if __name__ == '__main__':
    # Define the directories to monitor
    WATCH_DIRECTORY = "/home/heiyujia/Python_Services/DocumentReader/Processing"
    HANDLED_DIRECTORY = "/home/heiyujia/Python_Services/DocumentReader/Processed"
    TEMP_PATH = "/home/heiyujia/Python_Services/DocumentReader/temp"
    KEY_PATH = "/home/heiyujia/Python_Services/DocumentReader/OpenAIKey/key.txt"
    DB_PATH = "/home/heiyujia/Python_Services/DocumentReader/Database"
    
    # Create an instance of DocumentReader
    reader = DocumentReader(WATCH_DIRECTORY, HANDLED_DIRECTORY, TEMP_PATH, KEY_PATH, DB_PATH)

    # Run the document reader service
    reader.run()

