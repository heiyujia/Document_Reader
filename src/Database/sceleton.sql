-- main table：documents
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255),
    summary TEXT,
    reference_number VARCHAR(50),
    language VARCHAR(50),
    timestamp DATE,
    link_original VARCHAR(255),
    json_str TEXT
);

-- sub table：bank_info
CREATE TABLE IF NOT EXISTS bank_info (
    id INTEGER PRIMARY KEY,
    bank_name VARCHAR(255),
    account_number VARCHAR(255),
    account_holder VARCHAR(255),
    transfer_deadline VARCHAR(255),
    document_id INT,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);

-- sub table：amount
CREATE TABLE IF NOT EXISTS amount (
    id INTEGER PRIMARY KEY,
    currency VARCHAR(10),
    value VARCHAR(50),
    bank_info_id INT,
    FOREIGN KEY (bank_info_id) REFERENCES bank_info(id)
);

-- sub table：related_info
CREATE TABLE IF NOT EXISTS related_info (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    company VARCHAR(255),
    position VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    document_id INT,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);

-- sub table：address
CREATE TABLE IF NOT EXISTS address (
    id INTEGER PRIMARY KEY,
    street VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    related_info_id INT,
    FOREIGN KEY (related_info_id) REFERENCES related_info(id)
);

-- sub table：recipients
CREATE TABLE IF NOT EXISTS recipients (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    document_id INT,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
