"""Centralized configuration for the BTB extraction pipeline.

All paths are resolved relative to the project root (parent of src/).
Database credentials are read from environment variables or a .env file.
"""

import os
from pathlib import Path

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


# -- Project root -------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# -- Data directories ----------------------------------------------------------
DATA_DIR = PROJECT_ROOT / "data"
EXTRACT_ALL_DIR = DATA_DIR / "extract_all"
EXTRACT_FILTERED_BTB_DIR = DATA_DIR / "extract_filter_btb"
EXTRACT_BTB_TXT_DIR = DATA_DIR / "extract_btb_txt"
EXTRACT_ARCHEMED_DIR = DATA_DIR / "EDS_archemed_extract"
EXTRACT_FILTERED_BTB_DIR_ARCHEMED = DATA_DIR / "extract_filtrer_btb_archemed"

# -- Output directory ----------------------------------------------------------
OUTPUT_DIR = PROJECT_ROOT / "src" / "output"

# -- Reference data ------------------------------------------------------------
TRANSPLANTS_CSV = PROJECT_ROOT / "src" / "extraction" / "transplants.csv"

# -- Java / JAR ----------------------------------------------------------------
JAR_PATH = PROJECT_ROOT / "src" / "extraction" / "pdftotext-jar-with-dependencies.jar"
JAVA_PATH = _env("JAVA_PATH", r"C:\Program Files\Java\jdk-21.0.5\bin\java.exe")

# -- Database credentials (from environment) -----------------------------------
EASILY_DB = {
    "server": _env("EASILY_SERVER", "srvapp600"),
    "database": _env("EASILY_DATABASE", "master"),
    "username": _env("EASILY_USERNAME"),
    "password": _env("EASILY_PASSWORD"),
}

ORACLE_DB = {
    "database": _env("ORACLE_DATABASE", "dwh"),
    "username": _env("ORACLE_USERNAME"),
    "password": _env("ORACLE_PASSWORD"),
    "hostname": _env("ORACLE_HOSTNAME", "srvapp522"),
    "port": _env("ORACLE_PORT", "1521"),
    "service_name": _env("ORACLE_SERVICE_NAME", "dwh"),
}

PG_DB = {
    "host": _env("PG_HOSTNAME", "192.168.2.52"),
    "port": _env("PG_PORT", "5432"),
    "database": _env("PG_DATABASE", "dwh_care"),
    "user": _env("PG_USERNAME"),
    "password": _env("PG_PASSWORD"),
}
