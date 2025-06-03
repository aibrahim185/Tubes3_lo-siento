import fitz  # PyMuPDF
import re
from typing import Optional, Dict

class PDFProcessor:
    """Class to handle PDF text extraction using PyMuPDF"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF file
        Returns extracted text or None if extraction fails
        """
        try:
            doc = fitz.open(pdf_path)
            all_text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                all_text += text + "\n"
            
            doc.close()
            return all_text.strip()
            
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None
    
    @staticmethod
    def extract_text_dual_format(pdf_path: str) -> Dict[str, str]:
        """
        Extract text in two formats:
        1. Normal format with line breaks
        2. Single string format (lowercase, no line breaks)
        """
        try:
            doc = fitz.open(pdf_path)
            all_text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                all_text += text
            
            doc.close()
            
            # Format 1: Normal text with line breaks
            normal_text = all_text
            
            # Format 2: Single string, lowercase
            # Remove all line breaks and combine with spaces
            single_string = all_text.replace('\n', ' ').replace('\r', ' ')
            
            # Remove multiple spaces
            single_string = re.sub(r'\s+', ' ', single_string)
            
            # Convert to lowercase
            single_string = single_string.lower()
            
            # Remove leading and trailing spaces
            single_string = single_string.strip()
            
            return {
                'normal': normal_text,
                'processed': single_string
            }
            
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return {'normal': '', 'processed': ''}
    
    @staticmethod
    def save_extracted_text(text_data: Dict[str, str], base_filename: str):
        """
        Save extracted text to files
        """
        try:
            # Save normal format
            with open(f'{base_filename}_normal.txt', 'w', encoding='utf-8') as f:
                f.write(text_data['normal'])
            
            # Save processed format
            with open(f'{base_filename}_processed.txt', 'w', encoding='utf-8') as f:
                f.write(text_data['processed'])
                
            return True
            
        except Exception as e:
            print(f"Error saving text files: {e}")
            return False
