import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTextEdit, QFileDialog, 
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QLineEdit, QComboBox, QMessageBox, QGroupBox,
                             QGridLayout, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

# Import our modules
from utils.pdf_processor import PDFProcessor
from algorithms.kmp import kmp_search_with_context
from algorithms.boyer_moore import boyer_moore_search_with_context
from algorithms.regex_search import regex_search
from db.database_manager import db_manager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATS CV Analyzer - LO-SIENTO")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize variables
        self.current_file_path = None
        self.extracted_text = ""
        self.current_cv_id = None
        
        # Connect to database
        self.init_database()
        
        # Set up the central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create title
        title_label = QLabel("ATS CV Analyzer")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_upload_tab()
        self.create_search_tab()
        self.create_database_tab()
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def init_database(self):
        """Initialize database connection"""
        try:
            if db_manager.connect():
                self.statusBar().showMessage("Database connected successfully")
            else:
                self.statusBar().showMessage("Warning: Database connection failed")
        except Exception as e:
            QMessageBox.warning(self, "Database Warning", f"Could not connect to database: {str(e)}")
            
    def closeEvent(self, event):
        """Handle application close event"""
        db_manager.disconnect()
        event.accept()
        
    def create_upload_tab(self):
        """Create the CV upload and processing tab"""
        upload_widget = QWidget()
        upload_layout = QVBoxLayout()
        upload_widget.setLayout(upload_layout)
        
        # File upload section
        file_group = QGroupBox("Upload CV")
        file_layout = QGridLayout()
        file_group.setLayout(file_layout)
        
        self.file_path_label = QLabel("No file selected")
        self.browse_button = QPushButton("Browse CV File")
        self.browse_button.clicked.connect(self.browse_file)
        
        file_layout.addWidget(QLabel("Selected File:"), 0, 0)
        file_layout.addWidget(self.file_path_label, 0, 1)
        file_layout.addWidget(self.browse_button, 1, 0, 1, 2)
        
        upload_layout.addWidget(file_group)
        
        # Processing section
        process_group = QGroupBox("Process CV")
        process_layout = QVBoxLayout()
        process_group.setLayout(process_layout)
        
        self.process_button = QPushButton("Extract Text from CV")
        self.process_button.clicked.connect(self.process_cv)
        self.process_button.setEnabled(False)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        process_layout.addWidget(self.process_button)
        process_layout.addWidget(self.progress_bar)
        
        upload_layout.addWidget(process_group)
        
        # Text display section
        text_group = QGroupBox("Extracted Text")
        text_layout = QVBoxLayout()
        text_group.setLayout(text_layout)
        
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        text_layout.addWidget(self.text_display)
        
        upload_layout.addWidget(text_group)
        
        self.tab_widget.addTab(upload_widget, "Upload CV")
        
    def create_search_tab(self):
        """Create the keyword search tab"""
        search_widget = QWidget()
        search_layout = QVBoxLayout()
        search_widget.setLayout(search_layout)
        
        # Search input section
        search_group = QGroupBox("Search Parameters")
        search_grid = QGridLayout()
        search_group.setLayout(search_grid)
        
        search_grid.addWidget(QLabel("Search Query:"), 0, 0)
        self.search_input = QLineEdit()
        search_grid.addWidget(self.search_input, 0, 1)
        
        search_grid.addWidget(QLabel("Algorithm:"), 1, 0)
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["KMP", "Boyer-Moore", "Regex"])
        search_grid.addWidget(self.algorithm_combo, 1, 1)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        self.search_button.setEnabled(False)
        search_grid.addWidget(self.search_button, 2, 0, 1, 2)
        
        search_layout.addWidget(search_group)
        
        # Results section
        results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout()
        results_group.setLayout(results_layout)
        
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        results_layout.addWidget(self.results_display)
        
        search_layout.addWidget(results_group)
        
        self.tab_widget.addTab(search_widget, "Search")
        
    def create_database_tab(self):
        """Create the database management tab"""
        db_widget = QWidget()
        db_layout = QVBoxLayout()
        db_widget.setLayout(db_layout)
        
        # Database controls
        db_controls_group = QGroupBox("Database Operations")
        db_controls_layout = QHBoxLayout()
        db_controls_group.setLayout(db_controls_layout)
        
        self.save_to_db_button = QPushButton("Save CV to Database")
        self.save_to_db_button.clicked.connect(self.save_to_database)
        
        self.view_db_button = QPushButton("View Database")
        self.view_db_button.clicked.connect(self.view_database)
        
        self.clear_db_button = QPushButton("Clear Database")
        self.clear_db_button.clicked.connect(self.clear_database)
        
        db_controls_layout.addWidget(self.save_to_db_button)
        db_controls_layout.addWidget(self.view_db_button)
        db_controls_layout.addWidget(self.clear_db_button)
        
        db_layout.addWidget(db_controls_group)
        
        # Database table
        self.db_table = QTableWidget()
        self.db_table.setColumnCount(4)
        self.db_table.setHorizontalHeaderLabels(["ID", "Filename", "Upload Date", "Status"])
        db_layout.addWidget(self.db_table)
        
        self.tab_widget.addTab(db_widget, "Database")
        
    def browse_file(self):
        """Open file dialog to select CV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select CV File", 
            "", 
            "PDF files (*.pdf);;All files (*.*)"
        )
        
        if file_path:
            self.file_path_label.setText(file_path)
            self.process_button.setEnabled(True)
            self.current_file_path = file_path
            
    def process_cv(self):
        """Process the selected CV file"""
        if not hasattr(self, 'current_file_path') or not self.current_file_path:
            QMessageBox.warning(self, "Warning", "Please select a CV file first.")
            return
            
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.statusBar().showMessage("Processing CV...")
            
            # Extract text from PDF
            text_data = PDFProcessor.extract_text_dual_format(self.current_file_path)
            
            if text_data['normal']:
                self.extracted_text = text_data['normal']
                self.text_display.setText(self.extracted_text)
                
                # Save to database
                filename = os.path.basename(self.current_file_path)
                self.current_cv_id = db_manager.save_cv(filename, self.current_file_path, self.extracted_text)
                
                self.progress_bar.setValue(100)
                self.statusBar().showMessage("CV processed successfully")
                
                # Enable search functionality
                self.search_button.setEnabled(True)
                
            else:
                QMessageBox.warning(self, "Warning", "Could not extract text from PDF.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process CV: {str(e)}")
            self.statusBar().showMessage("Error processing CV")
        finally:
            self.progress_bar.setVisible(False)
            
    def perform_search(self):
        """Perform keyword search"""
        query = self.search_input.text().strip()
        algorithm = self.algorithm_combo.currentText()
        
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a search query.")
            return
            
        if not self.extracted_text:
            QMessageBox.warning(self, "Warning", "Please process a CV first.")
            return
            
        try:
            results = []
            
            if algorithm == "KMP":
                results = kmp_search_with_context(self.extracted_text, query)
            elif algorithm == "Boyer-Moore":
                results = boyer_moore_search_with_context(self.extracted_text, query)
            elif algorithm == "Regex":
                results = regex_search(self.extracted_text, query)
                
            # Display results
            if results:
                result_text = f"Found {len(results)} matches for '{query}' using {algorithm}:\\n\\n"
                for i, result in enumerate(results[:10]):  # Show first 10 results
                    result_text += f"Match {i+1} at position {result['position']}:\\n"
                    result_text += f"Context: ...{result['context']}...\\n\\n"
                    
                # Save search result to database
                if self.current_cv_id:
                    db_manager.save_search_result(self.current_cv_id, query, algorithm, len(results))
            else:
                result_text = f"No matches found for '{query}' using {algorithm} algorithm."
                
            self.results_display.setText(result_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")
        
    def save_to_database(self):
        """Save CV data to database"""
        if not self.current_cv_id:
            QMessageBox.warning(self, "Warning", "No CV data to save. Please process a CV first.")
            return
            
        QMessageBox.information(self, "Info", f"CV data already saved to database with ID: {self.current_cv_id}")
        
    def view_database(self):
        """View database contents"""
        try:
            cvs = db_manager.get_all_cvs()
            self.db_table.setRowCount(len(cvs))
            
            for row, cv in enumerate(cvs):
                self.db_table.setItem(row, 0, QTableWidgetItem(str(cv['id'])))
                self.db_table.setItem(row, 1, QTableWidgetItem(cv['filename']))
                self.db_table.setItem(row, 2, QTableWidgetItem(str(cv['upload_date'])))
                self.db_table.setItem(row, 3, QTableWidgetItem(cv['status']))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load database: {str(e)}")
        
    def clear_database(self):
        """Clear database"""
        reply = QMessageBox.question(
            self, 
            "Confirm", 
            "Are you sure you want to clear the database?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                db_manager.clear_database()
                self.db_table.setRowCount(0)
                QMessageBox.information(self, "Info", "Database cleared.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear database: {str(e)}")
