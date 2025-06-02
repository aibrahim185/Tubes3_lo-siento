# ATS CV Analyzer

Aplikasi Applicant Tracking System (ATS) untuk parsing CV dan pencarian kata kunci menggunakan algoritma pattern matching (KMP & Boyer-Moore) dan Regex.

## Algoritma yang Digunakan

- **KMP (Knuth-Morris-Pratt)**: Pencarian string dengan preprocessing LPS array untuk kompleksitas linear
- **Boyer-Moore**: Pencarian string dengan heuristik "bad character" dan "good suffix" untuk performa optimal
- **Regex**: Ekstraksi informasi terstruktur dari CV dan pattern matching fleksibel

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

### Install uv (jika belum ada)

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- [uv package manager](https://astral.sh/uv) - untuk dependency management

### Installation

```powershell
git clone https://github.com/aibrahim15/Tubes3_lo-siento.git
cd Tubes3_lo-siento

# Install dependencies dengan uv
uv sync

# Create .env file (copy from .env.example)
Copy-Item .env.example .env
# Update database configuration if needed
```

## Dependencies

Aplikasi ini menggunakan dependencies berikut:

- **PyQt6** - GUI framework
- **PyMuPDF** - PDF processing dan text extraction
- **mysql-connector-python** - Database connectivity dengan MySQL
- **python-dotenv** - Environment variables management

## Features

- Upload dan parsing PDF CV (PyMuPDF)
- Pencarian kata kunci dengan algoritma KMP dan Boyer-Moore
- Ekstraksi informasi dengan Regex
- Database management dengan MySQL
- GUI application dengan PyQt6
- Web interface untuk database (phpMyAdmin)
- Environment configuration dengan .env file

## Project Structure

```
Tubes3_lo-siento/
├── src/
│   ├── main.py              # Entry point aplikasi
│   ├── algorithms/          # Implementasi algoritma
│   │   ├── kmp.py          # Knuth-Morris-Pratt algorithm
│   │   ├── boyer_moore.py  # Boyer-Moore algorithm
│   │   └── regex_search.py # Regex-based search
│   ├── db/                 # Database management
│   │   └── database_manager.py
│   ├── gui/                # GUI PyQt6
│   │   └── main_window.py
│   └── utils/              # Utilities
│       └── pdf_processor.py
├── docker-compose.yml      # Docker services configuration
├── pyproject.toml          # Project dependencies (uv)
├── requirements.txt        # Legacy requirements file
├── .env.example           # Environment variables template
└── init.sql               # Database initialization script
```

## Authors

- Raudhah Yahya Kuddah - 13122003
- Felix Chandra - 13523012
- Ahmad Ibrahim - 13523089
