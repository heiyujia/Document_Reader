import sqlite3
import os
import json

class DatabaseManager:
    
    def __init__(self, db_path):
        """
        Initialize the DatabaseManager class, setting up the database connection 
        and executing the table structure script.
        :param db_path: Path to the database file
        :param schema_path: Path to the SQL file containing the table structure
        """
        self.db_path = os.path.join(db_path, "Documents.db")
        current_dir = os.path.dirname(__file__)
        self.schema_path = os.path.join(current_dir,"sceleton.sql")
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """
        Connect to the database and read the table structure from the SQL file.
        """
        
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        with open(self.schema_path, 'r') as file:
            schema_sql = file.read()
        self.cursor.executescript(schema_sql)
        
    def close(self):
        """
        Close the database connection.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            
    def insert_document(self, title, summary, reference_number, language, timestamp, link_original, json_str):
        """
        Insert data into the documents table.
        :param title: Document title
        :param summary: Document summary
        :param reference_number: Reference number
        :param language: Language
        :param timestamp: Timestamp
        :param link_original: the link to the scanned doc
        :param json_str: the return str from ai assistant
        :return: The document_id of the inserted record
        """
        document_sql = """
        INSERT INTO documents (title, summary, reference_number, language, timestamp, link_original, json_str)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        document_values = (title, summary, reference_number, language, timestamp, link_original, json_str)
        self.cursor.execute(document_sql, document_values)
        self.connection.commit()
        return self.cursor.lastrowid
    
    def insert_bank_info(self, bank_name, account_number, account_holder, transfer_deadline, document_id):
        """
        Insert data into the bank_info table.
        :param bank_name: Bank name
        :param account_number: Account number
        :param account_holder: Account holder
        :param transfer_deadline: Transfer deadline
        :param document_id: Associated document_id
        """
        bank_info_sql = """
        INSERT INTO bank_info (bank_name, account_number, account_holder, transfer_deadline, document_id)
        VALUES (?, ?, ?, ?, ?);
        """
        bank_info_values = (bank_name, account_number, account_holder, transfer_deadline, document_id)
        self.cursor.execute(bank_info_sql, bank_info_values)
        self.connection.commit()
        return self.cursor.lastrowid
    
    def insert_amount(self, currency, value, bank_info_id):
        """
        Insert data into the amount table.
        :param currency: Currency type
        :param value: Amount
        :param bank_info_id: Associated bank_info_id
        """
        amount_sql = """
        INSERT INTO amount (currency, value, bank_info_id)
        VALUES (?, ?, ?);
        """
        amount_values = (currency, value, bank_info_id)
        self.cursor.execute(amount_sql, amount_values)
        self.connection.commit()
        
    def insert_related_info(self, name, company, position, phone, email, document_id):
        """
        Insert data into the related_people table.
        :param name: Person's name
        :param company: Company name
        :param position: Position
        :param phone: Phone number
        :param email: Email
        :param document_id: Associated document_id
        :return: The related_info_id of the inserted record
        """
        related_info_sql = """
        INSERT INTO related_info (name, company, position, phone, email, document_id)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        related_info_values = (name, company, position, phone, email, document_id)
        self.cursor.execute(related_info_sql, related_info_values)
        self.connection.commit()
        return self.cursor.lastrowid
    
    def insert_address(self, street, city, postal_code, country, related_info_id):
        """
        Insert data into the address table.
        :param street: Street
        :param city: City
        :param postal_code: Postal code
        :param country: Country
        :param related_info_id: Associated related_info_id
        """
        address_sql = """
        INSERT INTO address (street, city, postal_code, country, related_info_id)
        VALUES (?, ?, ?, ?, ?);
        """
        address_values = (street, city, postal_code, country, related_info_id)
        self.cursor.execute(address_sql, address_values)
        self.connection.commit()
        
    def insert_recipient(self, name, email, document_id):
        """
        Insert data into the recipients table.
        :param name: Recipient's name
        :param email: Recipient's email
        :param document_id: Associated document_id
        """
        recipients_sql = """
        INSERT INTO recipients (name, email, document_id)
        VALUES (?, ?, ?);
        """
        recipients_values = (name, email, document_id)
        self.cursor.execute(recipients_sql, recipients_values)
        self.connection.commit()
        
    def insert_new_element(self, json_str, link):
        data = json.loads(json_str)
        
        title = data.get('title', 'N/A')  # Default to 'N/A' if not found
        summary = data.get('summary', 'N/A')
        reference_number = data.get('reference_number', 'N/A')
        language = data.get('language', 'N/A')
        timestamp = data.get('timestamp', 'N/A')
        
        document_id = self.insert_document(title=title, summary=summary, reference_number=reference_number, language=language, timestamp=timestamp, link_original=link, json_str=json_str)
        
        # Accessing bank_info sub-layer data
        bank_info = data.get('bank_info', {})
        bank_name = bank_info.get('bank_name', 'N/A')
        account_number = bank_info.get('account_number', 'N/A')
        account_holder = bank_info.get('account_holder', 'N/A')
        transfer_deadline = bank_info.get('transfer_deadline', 'N/A')
        
        bank_info_id = self.insert_bank_info(bank_name=bank_name, account_number=account_number, account_holder=account_holder, transfer_deadline=transfer_deadline, document_id=document_id)
        
        # Accessing amount sub-layer data within bank_info
        amount_info = bank_info.get('amount', {})
        currency = amount_info.get('currency', 'N/A')
        value = amount_info.get('value', 'N/A')
        
        self.insert_amount(currency=currency, value=value, bank_info_id=bank_info_id)
        
        related_info = data.get('related_companies_or_people', [])
        
        # Check if related_people_list is empty
        if not related_info:
            related_info_id = self.insert_related_info(name="N/A", company="N/A", position="N/A", phone="N/A", email="N/A", document_id=document_id)
            self.insert_address(street="N/A", city="N/A", postal_code="N/A", country="N/A", related_info_id=related_info_id)
        else:
            if isinstance(related_info, dict):
                name = related_info.get('name', 'N/A')
                company = related_info.get('company', 'N/A')
                position = related_info.get('position', 'N/A')
                contact_info = related_info.get('contact_info', {})

                # Extracting contact details
                phone = contact_info.get('phone', 'N/A')
                email = contact_info.get('email', 'N/A')
                
                related_info_id = self.insert_related_info(name=name, company=company, position=position, phone=phone, email=email, document_id=document_id)
                
                address = contact_info.get('address', {})
                # Extracting address details
                street = address.get('street', 'N/A')
                city = address.get('city', 'N/A')
                postal_code = address.get('postal_code', 'N/A')
                country = address.get('country', 'N/A')
                
                self.insert_address(street=street, city=city, postal_code=postal_code, country=country, related_info_id=related_info_id)
                
            elif isinstance(related_info, list):
                for info in related_info:
                    name = info.get('name', 'N/A')
                    company = info.get('company', 'N/A')
                    position = info.get('position', 'N/A')
                    contact_info = info.get('contact_info', {})

                    # Extracting contact details
                    phone = contact_info.get('phone', 'N/A')
                    email = contact_info.get('email', 'N/A')
                    
                    related_info_id = self.insert_related_info(name=name, company=company, position=position, phone=phone, email=email, document_id=document_id)
                    
                    address = contact_info.get('address', {})
                    # Extracting address details
                    street = address.get('street', 'N/A')
                    city = address.get('city', 'N/A')
                    postal_code = address.get('postal_code', 'N/A')
                    country = address.get('country', 'N/A')
                    
                    self.insert_address(street=street, city=city, postal_code=postal_code, country=country, related_info_id=related_info_id)
            else:
                raise TypeError("not allowed format")
                
        recipients = data.get('recipients', {})
        if not recipients:
            self.insert_recipient(name="N/A", email="N/A", document_id=document_id)
        else:
            if isinstance(recipients, dict):
                name_recipients = recipients.get('name', 'N/A')
                email_recipients = recipients.get('email', 'N/A')
                self.insert_recipient(name=name_recipients, email=email_recipients, document_id=document_id)
            elif isinstance(recipients, list):
                for person in recipients:
                    name_recipients = person.get('name', 'N/A')
                    email_recipients = person.get('email', 'N/A')
                    self.insert_recipient(name=name_recipients, email=email_recipients, document_id=document_id)
            else:
                raise TypeError("not allowed format")
        
        

                
                
        