import sys
import os
import time
from dotenv import load_dotenv
import mysql.connector
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QTextEdit, QScrollArea,
    QLineEdit, QRadioButton, QSpinBox, QDialog, QFrame, QFileDialog,
    QGroupBox, QCheckBox, QProgressBar
)
from PyQt6.QtCore import Qt, QUrl, QThread, pyqtSignal
from PyQt6.QtGui import QDesktopServices

from utils.pdf_processor import PDFProcessor
from algorithms.boyer_moore import boyer_moore_search
from algorithms.kmp import kmp_search
from algorithms.aho_corasick import aho_corasick_search
from algorithms.levenshtein import find_most_similar , calculate_dynamic_threshold
from algorithms.regex_search import (
    extract_email_addresses, extract_phone_numbers,
    extract_education_info, extract_skills_keywords
)
from PyQt6.QtCore import pyqtSignal
from utils.flow_layout import FlowLayout

load_dotenv()

class SearchWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list, float, float, int)
    error = pyqtSignal(str)
    
    def __init__(self, keywords, all_cv_sources, top_n, is_ac_selected, is_kmp_selected, use_fuzzy, keyword_map):
        super().__init__()
        self.keywords = keywords
        self.all_cv_sources = all_cv_sources
        self.top_n = top_n
        self.is_ac_selected = is_ac_selected
        self.is_kmp_selected = is_kmp_selected
        self.use_fuzzy = use_fuzzy
        self.keyword_map = keyword_map
        self._is_cancelled = False
    
    def cancel(self):
        """Method untuk membatalkan pencarian"""
        self._is_cancelled = True
    
    def run(self):
        """Method utama yang dijalankan di thread terpisah"""
        try:
            self.progress.emit(0, "Memulai pencarian...")
            
            search_algo = None
            if not self.is_ac_selected:
                search_algo = kmp_search if self.is_kmp_selected else boyer_moore_search
            
            # ---- EXACT MATCHING ----
            self.progress.emit(10, "Melakukan exact matching...")
            start_time_exact = time.time()
            results = []
            unmatched_keywords = set(kw.lower() for kw in self.keywords)
            
            total_cvs = len(self.all_cv_sources)
            processed_cvs = 0
            
            for cv_source in self.all_cv_sources:
                if self._is_cancelled:
                    return
                
                applicant = cv_source["applicant"]
                cv_path = cv_source["cv_path"]
                
                # Update progress
                processed_cvs += 1
                progress_percent = int(20 + (processed_cvs / total_cvs) * 40)  # 20-60% untuk exact matching
                self.progress.emit(progress_percent, f"Memproses CV {processed_cvs}/{total_cvs}: {applicant['first_name']}")
                
                if not cv_path or not os.path.exists(cv_path):
                    continue
                
                cv_text = PDFProcessor.extract_text_dual_format(cv_path)['processed']
                if not cv_text:
                    continue
                
                matched_kw_freq = {}
                if self.is_ac_selected:
                    matches = aho_corasick_search(cv_text, self.keywords)
                    for match in matches:
                        lw_pattern = match['pattern']
                        original_pattern = self.keyword_map.get(lw_pattern)
                        if original_pattern:
                            matched_kw_freq[original_pattern] = matched_kw_freq.get(original_pattern, 0) + 1
                else:
                    for kw in self.keywords:
                        matches = search_algo(cv_text, kw)
                        if matches:
                            matched_kw_freq[kw] = len(matches)

                if matched_kw_freq:
                    found_patterns = {p.lower() for p in matched_kw_freq.keys()}
                    unmatched_keywords -= found_patterns

                if matched_kw_freq:
                    total_matches = sum(matched_kw_freq.values())
                    results.append({
                        "applicant": applicant,
                        "matches": matched_kw_freq,
                        "score": total_matches
                    })
            
            duration_exact = time.time() - start_time_exact
            
            # ---- FUZZY MATCHING ----
            duration_fuzzy = 0
            if self.use_fuzzy and unmatched_keywords and not self._is_cancelled:
                self.progress.emit(60, f"Melakukan fuzzy matching untuk {len(unmatched_keywords)} keyword...")
                start_time_fuzzy = time.time()
                
                processed_fuzzy = 0
                for cv_source in self.all_cv_sources:
                    if self._is_cancelled:
                        return
                    
                    applicant = cv_source["applicant"]
                    cv_path = cv_source["cv_path"]
                    
                    processed_fuzzy += 1
                    progress_percent = int(60 + (processed_fuzzy / total_cvs) * 30)  # 60-90% untuk fuzzy matching
                    self.progress.emit(progress_percent, f"Fuzzy matching {processed_fuzzy}/{total_cvs}: {applicant['first_name']}")

                    if not cv_path or not os.path.exists(cv_path):
                        continue

                    cv_text = PDFProcessor.extract_text_dual_format(cv_path)['processed']
                    if not cv_text:
                        continue
                    
                    fuzzy_matches_for_cv = {}
                    for keyword in unmatched_keywords:
                        threshold = calculate_dynamic_threshold(keyword)
                        if threshold == 0:
                            continue

                        similar_words = find_most_similar(keyword, cv_text, threshold=threshold)
                        if similar_words:
                            fuzzy_key = f"{keyword} (fuzzy)"
                            fuzzy_matches_for_cv[fuzzy_key] = len(similar_words)
                    
                    if fuzzy_matches_for_cv:
                        applicant_id = applicant["applicant_id"]
                        
                        existing_result = next((r for r in results if r["applicant"]["applicant_id"] == applicant_id), None)

                        if existing_result:
                            existing_result["matches"].update(fuzzy_matches_for_cv)
                            existing_result["score"] += sum(fuzzy_matches_for_cv.values())
                        else:
                            results.append({
                                "applicant": applicant,
                                "matches": fuzzy_matches_for_cv,
                                "score": sum(fuzzy_matches_for_cv.values())
                            })
                
                duration_fuzzy = time.time() - start_time_fuzzy
            
            if self._is_cancelled:
                return
            
            self.progress.emit(90, "Mengurutkan hasil...")
            sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
            top_results = sorted_results[:self.top_n]
            
            self.progress.emit(100, "Pencarian selesai!")
            
            # Emit hasil akhir
            self.finished.emit(top_results, duration_exact, duration_fuzzy, len(self.all_cv_sources))
            
        except Exception as e:
            self.error.emit(f"Error during search: {str(e)}")

class KeywordTag(QFrame):
    removed = pyqtSignal(str)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.keyword_text = text
        self.setObjectName("KeywordTag")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 2, 2)
        layout.setSpacing(5)

        label = QLabel(text)
        delete_button = QPushButton("x")
        delete_button.setObjectName("DeleteButton")
        delete_button.setFixedSize(18, 18)
        delete_button.clicked.connect(self.emit_removed_signal)

        layout.addWidget(label)
        layout.addWidget(delete_button)

    def emit_removed_signal(self):
        self.removed.emit(self.keyword_text)

class SummaryDialog(QDialog):
    def __init__(self, applicant_data, cv_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"CV Summary - {applicant_data['first_name']} {applicant_data['last_name']}")
        self.setGeometry(150, 150, 600, 500)

        layout = QVBoxLayout(self)
        
        if applicant_data.get('date_of_birth') == 'N/A' or applicant_data.get('address') == 'N/A':
            if applicant_data.get('address') == 'Database Entry':
                info_db = (f"File: {applicant_data['first_name']}.pdf\n"
                           f"Sumber: Database CV\n"
                           f"Upload Date: {applicant_data.get('date_of_birth', 'N/A')}")
            else:
                info_db = f"File: {applicant_data['first_name']}.pdf\nSumber: File yang diupload"
            layout.addWidget(QLabel("<b>Informasi File</b>"))
        else:
            info_db = (
                f"Nama: {applicant_data['first_name']} {applicant_data['last_name']}\n"
                f"Tanggal Lahir: {applicant_data['date_of_birth']}\n"
                f"Alamat: {applicant_data['address']}\n"
                f"Nomor Telepon: {applicant_data['phone_number']}"
            )
            layout.addWidget(QLabel("<b>Informasi Pribadi (dari Database)</b>"))
        
        layout.addWidget(QLabel(info_db))

        layout.addWidget(self.create_separator())
        layout.addWidget(QLabel("<b>Informasi Tambahan (Ekstraksi dari CV)</b>"))
        
        emails = extract_email_addresses(cv_text)
        phones = extract_phone_numbers(cv_text)
        layout.addWidget(QLabel(f"<b>Email di CV:</b> {', '.join(emails) if emails else 'Tidak ditemukan'}"))
        layout.addWidget(QLabel(f"<b>Telepon di CV:</b> {', '.join(phones) if phones else 'Tidak ditemukan'}"))

        skills_list = ["Python", "Java", "React", "SQL", "HTML", "CSS", "JavaScript", "Project Management", "Data Analysis"]
        found_skills = extract_skills_keywords(cv_text, skills_list)
        layout.addWidget(QLabel(f"<b>Keahlian Terdeteksi:</b> {', '.join(found_skills) if found_skills else 'Tidak ditemukan'}"))
        
        education = extract_education_info(cv_text)
        layout.addWidget(QLabel("<b>Riwayat Pendidikan:</b>"))
        education_text = "\n".join(f"- {info.strip()}" for info in education) if education else "Tidak ditemukan"
        edu_display = QTextEdit(education_text)
        edu_display.setReadOnly(True)
        layout.addWidget(edu_display)
        
        close_button = QPushButton("Tutup")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

    def create_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator

class CVCard(QFrame):
    def __init__(self, applicant_data, matched_keywords, parent=None):
        super().__init__(parent)
        self.applicant_data = applicant_data
        
        layout = QVBoxLayout(self)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)

        name = f"{applicant_data['first_name']} {applicant_data['last_name']}"
        match_count = len(matched_keywords)
        header_label = QLabel(f"<b>{name}</b><br>{match_count} keyword cocok")
        layout.addWidget(header_label)

        keywords_str = ""
        for kw, freq in matched_keywords.items():
            keywords_str += f"- {kw}: {freq} kemunculan\n"
        
        keywords_display = QTextEdit(keywords_str.strip())
        keywords_display.setReadOnly(True)
        keywords_display.setMaximumHeight(80)
        layout.addWidget(keywords_display)
        
        button_layout = QHBoxLayout()
        summary_btn = QPushButton("Summary")
        view_cv_btn = QPushButton("View CV")
        
        summary_btn.clicked.connect(self.show_summary)
        view_cv_btn.clicked.connect(self.view_cv)

        button_layout.addWidget(summary_btn)
        button_layout.addWidget(view_cv_btn)
        layout.addLayout(button_layout)
        
    def show_summary(self):
        cv_path = self.applicant_data.get("cv_path")
        if not cv_path or not os.path.exists(cv_path):
            QMessageBox.warning(self, "Error", f"File CV tidak ditemukan di path: {cv_path}")
            return
            
        extracted_text = PDFProcessor.extract_text_dual_format(cv_path)['normal']
        if not extracted_text:
            QMessageBox.warning(self, "Error", f"Gagal mengekstrak teks dari {os.path.basename(cv_path)}.")
            return

        dialog = SummaryDialog(self.applicant_data, extracted_text, self)
        dialog.exec()

    def view_cv(self):
        cv_path = self.applicant_data.get("cv_path")
        if cv_path and os.path.exists(cv_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(cv_path)))
        else:
            QMessageBox.warning(self, "Error", f"File CV tidak ditemukan di path: {cv_path}")

class MainWindow(QMainWindow):
    """Kelas utama untuk aplikasi GUI ATS."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem ATS Berbasis Pattern Matching - Tugas Besar 3 Stima")
        self.setGeometry(100, 100, 800, 700)
        
        self.db_connection = None
        self.uploaded_pdf_files = []
        self.connect_to_database()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.current_keywords = []
        self.search_worker = None
        
        # input
        input_groupbox = QGroupBox("Kata Kunci")
        input_groupbox_layout = QVBoxLayout(input_groupbox)
        add_keyword_layout = QHBoxLayout()
        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText(" Ketik keyword lalu tekan tombol + atau Enter")
        self.keywords_input.setFixedHeight(30)
        self.add_keyword_button = QPushButton("+")
        self.add_keyword_button.setFixedSize(35, 35)

        add_keyword_layout.addWidget(self.keywords_input)
        add_keyword_layout.addWidget(self.add_keyword_button)

        # Layout untuk menampung tag
        self.tags_layout = FlowLayout(spacing=5)
        tags_container = QWidget()
        tags_container.setLayout(self.tags_layout)
        tags_container.setMinimumHeight(40)

        input_groupbox_layout.addLayout(add_keyword_layout)
        input_groupbox_layout.addWidget(tags_container)

        # Hubungkan sinyal
        self.add_keyword_button.clicked.connect(self.add_keyword)
        self.keywords_input.returnPressed.connect(self.add_keyword)
        
        # upload PDF
        pdf_layout = QHBoxLayout()
        pdf_layout.addWidget(QLabel("<b>Upload File PDF CV:</b>"))
        self.upload_pdf_button = QPushButton("📁 Pilih File PDF")
        self.upload_pdf_button.setMinimumHeight(35)
        self.upload_pdf_button.clicked.connect(self.upload_pdf_files)
        self.clear_pdf_button = QPushButton("🗑️ Hapus Semua")
        self.clear_pdf_button.setMinimumHeight(35)
        self.clear_pdf_button.clicked.connect(self.clear_uploaded_files)
        pdf_layout.addWidget(self.upload_pdf_button)
        pdf_layout.addWidget(self.clear_pdf_button)
        
        # daftar file
        self.uploaded_files_label = QLabel("Belum ada file yang diupload")
        self.uploaded_files_display = QTextEdit()
        self.uploaded_files_display.setReadOnly(True)
        self.uploaded_files_display.setMaximumHeight(100)
        self.uploaded_files_display.setPlainText("Belum ada file yang diupload")
        
        # opsi
        options_layout = QHBoxLayout()
        
        # algoritma
        algo_layout = QVBoxLayout()
        algo_layout.addWidget(QLabel("<b>Algoritma Pencocokan String:</b>"))
        self.ac_radio = QRadioButton("Aho-Corasick") # New radio button
        self.kmp_radio = QRadioButton("KMP")
        self.bm_radio = QRadioButton("Boyer-Moore")
        self.ac_radio.setChecked(True) # Set Aho-Corasick as default
        algo_layout.addWidget(self.ac_radio)
        algo_layout.addWidget(self.kmp_radio)
        algo_layout.addWidget(self.bm_radio)

        # Pengaturan
        top_matches_layout = QVBoxLayout()
        top_matches_layout.addWidget(QLabel("<b>Pengaturan:</b>"))
        input_line_layout = QHBoxLayout()
        self.top_matches_input = QSpinBox()
        self.top_matches_input.setMinimumHeight(30)
        self.top_matches_input.setMinimum(1)
        self.top_matches_input.setValue(10)
        self.top_matches_input.setFixedWidth(70) 
        input_line_layout.addWidget(QLabel("Tampilkan Top"))
        input_line_layout.addWidget(self.top_matches_input)
        input_line_layout.addWidget(QLabel("Matches"))
        top_matches_layout.addLayout(input_line_layout)
        self.fuzzy_match_checkbox = QCheckBox("Gunakan Fuzzy Matching (Perbolehkan Typo)")
        self.fuzzy_match_checkbox.setChecked(True)
        top_matches_layout.addWidget(self.fuzzy_match_checkbox)
        
        options_layout.addLayout(algo_layout)
        options_layout.addLayout(top_matches_layout)

        # search
        search_layout = QHBoxLayout()
        self.search_button = QPushButton("🔍 Search")
        self.search_button.setMinimumHeight(40)
        self.search_button.clicked.connect(self.execute_search)
        
        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.clicked.connect(self.cancel_search)
        self.cancel_button.setEnabled(False)
        
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.cancel_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)

        # hasil
        self.summary_label = QLabel("Hasil Pencarian Akan Ditampilkan di Sini")
        self.results_area = QWidget()
        self.results_layout = QVBoxLayout(self.results_area)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.results_area)

        self.main_layout.addWidget(input_groupbox)
        self.main_layout.addLayout(pdf_layout)
        self.main_layout.addWidget(self.uploaded_files_display)
        self.main_layout.addLayout(options_layout)
        self.main_layout.addLayout(search_layout)
        self.main_layout.addWidget(self.progress_bar)
        self.main_layout.addWidget(self.progress_label)
        self.main_layout.addWidget(self.create_separator())
        self.main_layout.addWidget(self.summary_label)
        self.main_layout.addWidget(scroll)

    def add_keyword(self):
        keyword = self.keywords_input.text().strip()
        if keyword and keyword.lower() not in [kw.lower() for kw in self.current_keywords]:
            self.current_keywords.append(keyword)

            tag_widget = KeywordTag(keyword)
            tag_widget.removed.connect(self.remove_keyword) # Hubungkan sinyal remove
            self.tags_layout.addWidget(tag_widget)

            self.keywords_input.clear()

    def remove_keyword(self, keyword_to_remove):
        self.current_keywords = [kw for kw in self.current_keywords if kw.lower() != keyword_to_remove.lower()]
        
        for i in range(self.tags_layout.count() - 1, -1, -1):
            widget = self.tags_layout.itemAt(i).widget()
            
            if isinstance(widget, KeywordTag) and widget.keyword_text.lower() == keyword_to_remove.lower():
                layout_item = self.tags_layout.takeAt(i)
                if layout_item and layout_item.widget():
                    layout_item.widget().deleteLater()
                break

        self.tags_layout.update()

    def create_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator

    def connect_to_database(self):
        try:
            self.db_connection = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT")),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME"),
            )
            if self.db_connection.is_connected():
                print("✅ Berhasil tersambung ke database.")
        except (mysql.connector.Error, ValueError) as err:
            QMessageBox.critical(self, "Kesalahan Koneksi DB", f"Gagal tersambung: {err}")
            self.db_connection = None
    
    def fetch_cvs_from_db(self):
        if not self.db_connection or not self.db_connection.is_connected():
            self.connect_to_database()
            if not self.db_connection:
                return []

        cursor = self.db_connection.cursor(dictionary=True)
        query = """
            SELECT 
                ap.applicant_id,
                ap.first_name,
                ap.last_name,
                ap.date_of_birth,
                ap.address,
                ap.phone_number,
                ad.detail_id,
                ad.application_role,
                ad.cv_path
            FROM ApplicantProfile ap
            JOIN ApplicationDetail ad ON ap.applicant_id = ad.applicant_id
            ORDER BY ad.detail_id DESC
        """
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except mysql.connector.Error as err:
            QMessageBox.warning(self, "Query Error", f"Gagal mengambil data CV: {err}")
            return []
        finally:
            cursor.close()

    def save_uploaded_cv_to_db(self, file_path):
        if not self.db_connection or not self.db_connection.is_connected():
            self.connect_to_database()
            if not self.db_connection:
                return None

        cursor = self.db_connection.cursor()
        filename = os.path.basename(file_path)
        
        try:
            base_name = filename.replace(".pdf", "")
            name_parts = base_name.split(" ", 1)
            first_name = name_parts[0] if name_parts else "Unknown"
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            profile_query = """
                INSERT INTO ApplicantProfile (first_name, last_name)
                VALUES (%s, %s)
            """
            cursor.execute(profile_query, (first_name, last_name))
            applicant_id = cursor.lastrowid
            
            detail_query = """
                INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path)
                VALUES (%s, %s, %s)
            """
            
            cursor.execute(detail_query, (applicant_id, "CV Upload", file_path))
            detail_id = cursor.lastrowid
            
            self.db_connection.commit()
            return detail_id
            
        except mysql.connector.Error as err:
            self.db_connection.rollback()
            QMessageBox.warning(self, "Database Error", f"Gagal menyimpan CV ke database: {err}")
            return None
        finally:
            cursor.close()

    def save_search_results(self, detail_id, search_query, algorithm_used, matches_found):
        # Log search results instead of saving to database since search_results table doesn't exist
        print(f"Search performed - Detail ID: {detail_id}, Query: '{search_query}', Algorithm: {algorithm_used}, Matches: {matches_found}")

    def upload_pdf_files(self):
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(
            self,
            "Pilih File PDF CV",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_paths:
            successfully_added = 0
            for file_path in file_paths:
                if file_path not in self.uploaded_pdf_files:
                    self.uploaded_pdf_files.append(file_path)
                    
                    try:
                        detail_id = self.save_uploaded_cv_to_db(file_path)
                        if detail_id:
                            successfully_added += 1
                            print(f"✅ Berhasil menyimpan {os.path.basename(file_path)} ke database dengan Detail ID: {detail_id}")
                        else:
                            print(f"❌ Gagal menyimpan {os.path.basename(file_path)} ke database")
                    except Exception as e:
                        print(f"❌ Error processing {os.path.basename(file_path)}: {e}")
            
            self.update_uploaded_files_display()
            if successfully_added > 0:
                QMessageBox.information(
                    self, 
                    "Upload Berhasil", 
                    f"Berhasil menambahkan {successfully_added} file PDF ke database."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Upload Gagal",
                    "Tidak ada file yang berhasil disimpan ke database."
                )

    def clear_uploaded_files(self):
        if self.uploaded_pdf_files:
            self.uploaded_pdf_files.clear()
            self.update_uploaded_files_display()
            QMessageBox.information(self, "File Dihapus", "Semua file PDF telah dihapus.")
        else:
            QMessageBox.information(self, "Tidak Ada File", "Tidak ada file untuk dihapus.")

    def update_uploaded_files_display(self):
        if not self.uploaded_pdf_files:
            self.uploaded_files_label.setText("Belum ada file yang diupload")
            self.uploaded_files_display.setPlainText("Belum ada file yang diupload")
        else:
            self.uploaded_files_label.setText(f"File PDF yang diupload ({len(self.uploaded_pdf_files)} file):")
            file_list = []
            for i, file_path in enumerate(self.uploaded_pdf_files, 1):
                filename = os.path.basename(file_path)
                file_list.append(f"{i}. {filename}")
            self.uploaded_files_display.setPlainText("\n".join(file_list))

    def get_all_cv_sources(self):
        all_cvs = []
        
        db_cvs = self.fetch_cvs_from_db()
        for cv_data in db_cvs:
            cv_path = cv_data.get("cv_path")
            if cv_path and os.path.exists(cv_path):
                filename = os.path.basename(cv_path)
                applicant_data = {
                    "applicant_id": cv_data["applicant_id"],
                    "detail_id": cv_data["detail_id"],
                    "first_name": cv_data["first_name"] or filename.replace(".pdf", ""),
                    "last_name": cv_data["last_name"] or "",
                    "date_of_birth": cv_data["date_of_birth"].strftime("%Y-%m-%d") if cv_data["date_of_birth"] else "N/A",
                    "address": cv_data["address"] or "Database Entry",
                    "phone_number": cv_data["phone_number"] or "N/A",
                    "application_role": cv_data["application_role"] or "CV dari Database",
                    "cv_path": cv_path
                }
                all_cvs.append({
                    "source": "database",
                    "applicant": applicant_data,
                    "cv_path": cv_path
                })
        
        for i, file_path in enumerate(self.uploaded_pdf_files):
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                already_in_db = any(cv_data["cv_path"] == file_path for cv_data in db_cvs)
                
                if not already_in_db:
                    dummy_applicant = {
                        "applicant_id": f"upload_{i}",
                        "detail_id": f"upload_detail_{i}",
                        "first_name": filename.replace(".pdf", ""),
                        "last_name": "",
                        "date_of_birth": "N/A",
                        "address": "N/A", 
                        "phone_number": "N/A",
                        "application_role": "Uploaded CV",
                        "cv_path": file_path
                    }
                    all_cvs.append({
                        "source": "uploaded",
                        "applicant": dummy_applicant,
                        "cv_path": file_path
                    })
        
        return all_cvs

    def execute_search(self):
        if not self.current_keywords:
            QMessageBox.warning(self, "Input Kosong", "Silakan masukkan setidaknya satu kata kunci.")
            return

        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.cancel()
            self.search_worker.wait()

        keywords = self.current_keywords
        keyword_map = {kw.lower(): kw for kw in keywords}
        
        top_n = self.top_matches_input.value()
        
        is_ac_selected = self.ac_radio.isChecked()
        is_kmp_selected = self.kmp_radio.isChecked()
        use_fuzzy = self.fuzzy_match_checkbox.isChecked()
        
        all_cv_sources = self.get_all_cv_sources()
        if not all_cv_sources:
            QMessageBox.information(self, "Info", "Tidak ada CV yang tersedia untuk dicari (baik dari database maupun file yang diupload).")
            return

        self.search_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setVisible(True)
        self.progress_label.setText("Mempersiapkan pencarian...")
        
        for i in reversed(range(self.results_layout.count())):
            self.results_layout.itemAt(i).widget().setParent(None)
        
        self.summary_label.setText("Pencarian sedang berjalan...")

        self.search_worker = SearchWorker(
            keywords, all_cv_sources, top_n, is_ac_selected, 
            is_kmp_selected, use_fuzzy, keyword_map
        )
        
        self.search_worker.progress.connect(self.on_search_progress)
        self.search_worker.finished.connect(self.on_search_finished)
        self.search_worker.error.connect(self.on_search_error)
        
        self.search_worker.start()
    
    def cancel_search(self):
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.cancel()
            self.progress_label.setText("Membatalkan pencarian...")
            self.search_worker.wait()
            self.on_search_cancelled()
    
    def on_search_progress(self, percentage, message):
        """Callback untuk update progress"""
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(message)
    
    def on_search_finished(self, top_results, duration_exact, duration_fuzzy, total_scanned):
        self.search_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        self.display_results(top_results, duration_exact, duration_fuzzy, total_scanned)
        
        for result in top_results:
            applicant = result["applicant"]
            if applicant.get("detail_id") and str(applicant["detail_id"]).isdigit():
                algorithm_name = "Aho-Corasick" if self.ac_radio.isChecked() else ("KMP" if self.kmp_radio.isChecked() else "Boyer-Moore")
                search_query = ", ".join(self.current_keywords)
                self.save_search_results(applicant["detail_id"], search_query, algorithm_name, result["score"])
    
    def on_search_error(self, error_message):
        self.search_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        QMessageBox.critical(self, "Error Pencarian", f"Terjadi kesalahan saat pencarian:\n{error_message}")
        self.summary_label.setText("Pencarian gagal.")
    
    def on_search_cancelled(self):
        self.search_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        self.summary_label.setText("Pencarian dibatalkan.")
        
        for i in reversed(range(self.results_layout.count())):
            self.results_layout.itemAt(i).widget().setParent(None)
        
    def display_results(self, top_results, duration_exact, duration_fuzzy, total_scanned):
        for i in reversed(range(self.results_layout.count())):
            self.results_layout.itemAt(i).widget().setParent(None)
            
        db_count = len(self.fetch_cvs_from_db())
        uploaded_count = len(self.uploaded_pdf_files)
        
        summary_text = (
            f"<b>Hasil Pencarian ({len(top_results)} dari {total_scanned} CV ditemukan):</b><br>"
            f"• CV dari Database: {db_count}<br>"
            f"• CV dari File Upload: {uploaded_count}<br>"
            f"• Waktu Eksekusi Exact Match: {duration_exact:.4f} detik<br>"
        )
        if duration_fuzzy > 0:
            summary_text += f"• Waktu Eksekusi Fuzzy Match: {duration_fuzzy:.4f} detik"
        
        self.summary_label.setText(summary_text)

        if not top_results:
            self.results_layout.addWidget(QLabel("Tidak ada CV yang cocok dengan kata kunci yang diberikan."))
        else:
            for res in top_results:
                card = CVCard(res['applicant'], res['matches'])
                self.results_layout.addWidget(card)

    def closeEvent(self, event):
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.cancel()
            self.search_worker.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    stylesheet = """
        QGroupBox {
            font-weight: bold; 
            color: #e8eaed;
        }
        #KeywordTag {
            background-color: #141414;
            color: #e8eaed;
            border-radius: 14px; /* Pill shape */
            padding: 5px 8px 5px 12px;
        }
        #KeywordTag QLabel {
            color: #e8eaed;
            padding-right: 5px;
        }
        #DeleteButton {
            background-color: transparent;
            color: #bdc1c6;
            border-radius: 9px;
            font-weight: bold;
            font-size: 14px;
            padding: 0px 4px 2px 4px;
        }
        #DeleteButton:hover {
            background-color: #f28b82; /* Soft red on hover */
            color: #202124; /* Dark text for contrast */
        }
    """
    app.setStyleSheet(stylesheet)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())