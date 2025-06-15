# ATS CV Analyzer

An Applicant Tracking System (ATS) application for CV parsing and keyword searching using pattern matching algorithms (KMP & Boyer-Moore) and Regex.

## Algorithms Used

- **KMP (Knuth-Morris-Pratt)**: String searching with LPS array preprocessing
- **Boyer-Moore**: String searching with "bad character" and "good suffix" heuristics
- **Levenshtein Distance**: Algorithm for calculating similarity between two strings (fuzzy matching)
- **Regex**: Structured information extraction from CVs and flexible pattern matching

## Quick Start

### 1. Setup Database (Docker)

```powershell
docker-compose up -d
```

### 2. Run Application

```powershell
uv run src/main.py
```

### 3. Access phpMyAdmin

- URL: http://localhost:8081

## Setup Development

### Install uv

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- [uv package manager](https://astral.sh/uv)

### Installation

````powershell
git clone https://github.com/aibrahim15/Tubes3_lo-siento.git
cd Tubes3_lo-siento

### Install Dependencies

```powershell
# Install dependencies using uv
uv sync

# Create .env file (copy from .env.example)
Copy-Item .env.example .env
# Edit .env file according to your database configuration
````

## Dependencies

This application uses the following dependencies:

- **PyQt6** - GUI framework for user interface
- **PyMuPDF** - Library for PDF processing and text extraction
- **mysql-connector-python** - Database connectivity with MySQL
- **python-dotenv** - Environment variables management from .env file

## Features

- Upload and parse PDF CVs using PyMuPDF
- Exact match keyword searching with KMP and Boyer-Moore algorithms
- Fuzzy matching using Levenshtein Distance algorithm
- Automatic information extraction from CVs with Regex (email, phone, education, skills)
- Database management with MySQL for storing CV data and search results
- User-friendly GUI application with PyQt6
- Web interface for database management (phpMyAdmin)
- Environment configuration using .env file
- Docker containerization for easy deployment

## Project Structure

```
Tubes3_lo-siento/
├── src/
│   ├── main.py                 # Application entry point with PyQt6 GUI
│   ├── algorithms/             # Algorithm implementations
│   │   ├── __init__.py
│   │   ├── kmp.py              # Knuth-Morris-Pratt algorithm
│   │   ├── boyer_moore.py      # Boyer-Moore algorithm
│   │   ├── levenshtein.py      # Levenshtein Distance algorithm
│   │   └── regex_search.py     # Regex-based search and extraction
│   └── utils/                  # Utility modules
│       ├── __init__.py
│       └── pdf_processor.py    # PDF text extraction utilities
├── data/                       # Data storage directory
├── doc/                        # Documentation
├── logs/                       # Application logs
├── docker-compose.yml          # Docker services configuration
├── docker-entrypoint.sh        # Docker startup script
├── Dockerfile                  # Docker container configuration
├── pyproject.toml              # Project dependencies (uv)
├── requirements.txt            # Legacy requirements file
├── uv.lock                     # Dependency lock file
├── .env.example                # Environment variables template
└── README.md                   # Project documentation
```

## Authors

- Raudhah Yahya Kuddah - 13122003
- Felix Chandra - 13523012
- Ahmad Ibrahim - 13523089
