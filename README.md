# Tubes3_LO-SIENTO - ATS CV Analyzer

This project is an Applicant Tracking System (ATS) designed to parse CVs, search for keywords using pattern matching algorithms, and manage applicant data. It utilizes pattern matching techniques (KMP and Boyer-Moore) to efficiently find relevant information in digital CVs. The system also uses Levenshtein Distance for fuzzy matching and Regex for information extraction.

## Brief Algorithm Explanation

- **Knuth-Morris-Pratt (KMP)**: The KMP algorithm is an efficient string searching algorithm that preprocesses the pattern to create a Longest Proper Prefix (LPS) array. This array helps in skipping characters intelligently when a mismatch occurs, avoiding redundant comparisons and achieving linear time complexity in the length of the text.
- **Boyer-Moore (BM)**: The Boyer-Moore algorithm is another efficient string searching algorithm. It uses two heuristics: the "bad character" rule and the "good suffix" rule. It starts matching the pattern from the end of the pattern against the text. In case of a mismatch, it can make larger shifts than KMP in many cases, often leading to better average-case performance, especially with larger alphabets.

## Requirements

- **Python** (e.g., Python 3.9+)
- **`uv` Package Manager**: For environment and package management.
  - If not installed, follow instructions at [https://astral.sh/uv](https://astral.sh/uv) or:
    - macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
    - Windows (PowerShell): `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
- **MySQL Server**: For database storage.
- **Project Dependencies** (will be installed via `uv` from `requirements.txt`):
  - PyQt6
  - PyPDF2 (or other PDF library used)
  - mysql-connector-python

## Installation and Setup

1.  **Clone the Repository**:

    ```bash
    git clone https://github.com/aibrahim15/Tubes3_lo-siento.git
    cd Tubes3_lo-siento
    ```

2.  **Create and Activate Virtual Environment using `uv`**:

    ```bash
    uv venv
    ```

    Activate it:

    - macOS/Linux: `source .venv/bin/activate`
    - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
    - Windows (CMD): `.venv\Scripts\activate.bat`

3.  **Install Dependencies using `uv`**:
    Create a `requirements.txt` file in the root of your project with the following content:

    ```txt
    mysql-connector-python==9.3.0
    PyMuPDF==1.24.2
    pyqt6==6.9.0
    pyqt6-qt6==6.9.0
    pyqt6-sip==13.10.2
    ```

    Then run:

    ```bash
    uv pip install -r requirements.txt
    ```

4.  **Database Setup**:
    - Ensure your MySQL server is running.
    - Create a database for this application.
    - Update the database connection details in the application if necessary (e.g., in `src/db/database_manager.py`).
    - The application may require initial data seeding. Follow instructions provided by the application or run the seeding script if available (e.g., for initial `ApplicantProfile` and `ApplicationDetail` table creation and linking to CVs in the `data/` folder).

## How to Run the Program

1.  Ensure your virtual environment is activated.
2.  Navigate to the `src/` directory:
    ```bash
    cd src
    ```
3.  Run the main application file:
    ```bash
    uv run main.py
    ```

## Author(s)

- Raudhah Yahya Kuddah - 13122003
- Felix Chandra - 13523012
- Ahmad Ibrahim - 13523089

---
