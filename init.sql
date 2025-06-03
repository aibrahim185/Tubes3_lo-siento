USE ats_cv_analyzer;

CREATE TABLE IF NOT EXISTS cvs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    extracted_text LONGTEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_date TIMESTAMP NULL,
    status ENUM('uploaded', 'processing', 'processed', 'error') DEFAULT 'uploaded',
    INDEX idx_filename (filename),
    INDEX idx_status (status),
    INDEX idx_upload_date (upload_date)
);

CREATE TABLE IF NOT EXISTS search_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cv_id INT,
    search_query VARCHAR(255),
    algorithm_used VARCHAR(50),
    matches_found INT DEFAULT 0,
    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cv_id) REFERENCES cvs(id) ON DELETE CASCADE,
    INDEX idx_cv_id (cv_id),
    INDEX idx_algorithm (algorithm_used),
    INDEX idx_search_date (search_date)
);
