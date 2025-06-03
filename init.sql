USE ats_cv_analyzer;

CREATE TABLE IF NOT EXISTS ApplicantProfile (
    applicant_id INT NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(50) DEFAULT NULL,
    last_name VARCHAR(50) DEFAULT NULL,
    date_of_birth DATE DEFAULT NULL,
    address VARCHAR(255) DEFAULT NULL,
    phone_number VARCHAR(20) DEFAULT NULL,
    PRIMARY KEY (applicant_id)
);

CREATE TABLE IF NOT EXISTS ApplicationDetail (
    detail_id INT NOT NULL AUTO_INCREMENT,
    applicant_id INT NOT NULL,
    application_role VARCHAR(100) DEFAULT NULL,
    cv_path TEXT,
    filename VARCHAR(255),
    extracted_text LONGTEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_date TIMESTAMP NULL,
    status ENUM('uploaded', 'processing', 'processed', 'error') DEFAULT 'uploaded',
    PRIMARY KEY (detail_id),
    FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id) ON DELETE CASCADE,
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_filename (filename),
    INDEX idx_status (status),
    INDEX idx_upload_date (upload_date)
);

CREATE TABLE IF NOT EXISTS search_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    detail_id INT,
    search_query VARCHAR(255),
    algorithm_used VARCHAR(50),
    matches_found INT DEFAULT 0,
    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (detail_id) REFERENCES ApplicationDetail(detail_id) ON DELETE CASCADE,
    INDEX idx_detail_id (detail_id),
    INDEX idx_algorithm (algorithm_used),
    INDEX idx_search_date (search_date)
);
