"""Convert PDF files to TXT using an external Java JAR tool.

Usage:
    python -m src.extraction.pdf_to_text
"""

import logging
import os
import shutil
import subprocess

from tqdm import tqdm

from src.config import (
    JAVA_PATH,
    JAR_PATH,
    EXTRACT_FILTERED_BTB_DIR,
    EXTRACT_BTB_TXT_DIR,
)

log = logging.getLogger(__name__)


def main(
    source_dir: str | None = None,
    output_dir: str | None = None,
):
    """Convert all PDFs in source_dir to TXT files in output_dir."""
    source = source_dir or str(EXTRACT_FILTERED_BTB_DIR)
    output = output_dir or str(EXTRACT_BTB_TXT_DIR)

    os.makedirs(source, exist_ok=True)
    if not JAR_PATH.exists():
        raise FileNotFoundError(f"JAR file not found: {JAR_PATH}")

    os.makedirs(output, exist_ok=True)

    pdf_files = [f for f in os.listdir(source) if f.endswith(".pdf")]
    log.info("Found %d PDF files in %s", len(pdf_files), source)

    # Skip already converted files
    existing_txt = set(
        os.path.splitext(f)[0] for f in os.listdir(output) if f.endswith(".txt")
    )
    to_process = [f for f in pdf_files if os.path.splitext(f)[0] not in existing_txt]
    log.info(
        "Already converted: %d, remaining: %d",
        len(pdf_files) - len(to_process),
        len(to_process),
    )

    converted = 0
    for file_name in tqdm(to_process, desc="PDF -> TXT"):
        file_path = os.path.join(source, file_name)
        try:
            command = [JAVA_PATH, "-jar", str(JAR_PATH), file_path]
            result = subprocess.run(command, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                txt_file_name = os.path.splitext(file_name)[0] + ".txt"
                source_txt_path = os.path.join(".", txt_file_name)
                dest_txt_path = os.path.join(output, txt_file_name)

                if os.path.exists(source_txt_path):
                    shutil.move(source_txt_path, dest_txt_path)
                    converted += 1
                else:
                    log.warning("No output file for: %s", file_name)
            else:
                log.error("Conversion failed for %s: %s", file_name, result.stderr)

        except subprocess.TimeoutExpired:
            log.warning("Timeout processing %s", file_name)
        except Exception as e:
            log.error("Error processing %s: %s", file_name, e)

    log.info(
        "Conversion done: %d/%d new files converted to %s",
        converted,
        len(to_process),
        output,
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    main()
