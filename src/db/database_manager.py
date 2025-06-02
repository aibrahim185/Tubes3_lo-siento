import mysql.connector
from mysql.connector import Error
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self, host=None, database=None, user=None, password=None, port=None):
        """Initialize database connection with environment variables"""
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.database = database or os.getenv('DB_NAME', 'ats_cv_analyzer')
        self.user = user or os.getenv('DB_USER', 'root')
        self.password = password or os.getenv('DB_PASSWORD', '')
        self.port = int(port or os.getenv('DB_PORT', 3306))
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                logging.info("Successfully connected to MySQL database")
                self.create_tables()
                return True
        except Error as e:
            logging.error(f"Error connecting to MySQL: {e}")
            return False
            
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("MySQL connection closed")
            
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Create CVs table
            create_cvs_table = """
            CREATE TABLE IF NOT EXISTS cvs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(500),
                extracted_text LONGTEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_date TIMESTAMP NULL,
                status ENUM('uploaded', 'processing', 'processed', 'error') DEFAULT 'uploaded'
            )
            """
            
            # Create search_results table
            create_search_table = """
            CREATE TABLE IF NOT EXISTS search_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cv_id INT,
                search_query VARCHAR(255),
                algorithm_used VARCHAR(50),
                matches_found INT DEFAULT 0,
                search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cv_id) REFERENCES cvs(id) ON DELETE CASCADE
            )
            """
            
            cursor.execute(create_cvs_table)
            cursor.execute(create_search_table)
            self.connection.commit()
            logging.info("Tables created successfully")
            
        except Error as e:
            logging.error(f"Error creating tables: {e}")
            
    def save_cv(self, filename: str, file_path: str, extracted_text: str = "") -> int:
        """Save CV information to database"""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO cvs (filename, file_path, extracted_text, status)
            VALUES (%s, %s, %s, %s)
            """
            values = (filename, file_path, extracted_text, 'uploaded')
            cursor.execute(query, values)
            self.connection.commit()
            
            cv_id = cursor.lastrowid
            logging.info(f"CV saved successfully with ID: {cv_id}")
            return cv_id
            
        except Error as e:
            logging.error(f"Error saving CV: {e}")
            return -1
            
    def update_cv_text(self, cv_id: int, extracted_text: str):
        """Update extracted text for a CV"""
        try:
            cursor = self.connection.cursor()
            query = """
            UPDATE cvs 
            SET extracted_text = %s, processed_date = %s, status = 'processed'
            WHERE id = %s
            """
            values = (extracted_text, datetime.now(), cv_id)
            cursor.execute(query, values)
            self.connection.commit()
            logging.info(f"CV text updated for ID: {cv_id}")
            
        except Error as e:
            logging.error(f"Error updating CV text: {e}")
            
    def get_all_cvs(self) -> List[Dict]:
        """Retrieve all CVs from database"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM cvs ORDER BY upload_date DESC"
            cursor.execute(query)
            results = cursor.fetchall()
            return results
            
        except Error as e:
            logging.error(f"Error retrieving CVs: {e}")
            return []
            
    def get_cv_by_id(self, cv_id: int) -> Optional[Dict]:
        """Get specific CV by ID"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM cvs WHERE id = %s"
            cursor.execute(query, (cv_id,))
            result = cursor.fetchone()
            return result
            
        except Error as e:
            logging.error(f"Error retrieving CV: {e}")
            return None
            
    def save_search_result(self, cv_id: int, search_query: str, algorithm: str, matches_found: int):
        """Save search result to database"""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO search_results (cv_id, search_query, algorithm_used, matches_found)
            VALUES (%s, %s, %s, %s)
            """
            values = (cv_id, search_query, algorithm, matches_found)
            cursor.execute(query, values)
            self.connection.commit()
            logging.info("Search result saved successfully")
            
        except Error as e:
            logging.error(f"Error saving search result: {e}")
            
    def clear_database(self):
        """Clear all data from database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM search_results")
            cursor.execute("DELETE FROM cvs")
            self.connection.commit()
            logging.info("Database cleared successfully")
            
        except Error as e:
            logging.error(f"Error clearing database: {e}")

# Global database instance
db_manager = DatabaseManager()