"""Point d'entree unique pour le pipeline BTB extraction.

Usage:
    python run_pipeline.py --all                              # tout le pipeline
    python run_pipeline.py --steps filter extract_btb clean    # etapes choisies
    python run_pipeline.py --list                              # lister les etapes
"""

import argparse
import importlib
import logging
import sys

log = logging.getLogger(__name__)

# Steps included in --all (standard pipeline)
STEPS = {
    "extract_easily": ("Extraction BDD Easily", "src.extraction.db_easily", "main"),
    "filter": ("Filtrage documents BTB", "src.extraction.filter_btb", "main"),
    "pdf_to_text": ("Conversion PDF -> TXT", "src.extraction.pdf_to_text", "main"),
    "extract_btb": ("Extraction champs BTB", "src.structuration.extract_btb", "main"),
    "clean": ("Nettoyage BTB", "src.structuration.clean_btb", "main"),
}

# Steps that must be explicitly requested (one-shot DB extraction)
EXTRA_STEPS = {
    "extract_archemed": (
        "Extraction BDD ARCHEMED",
        "src.extraction.db_archemed",
        "main",
    ),
    "clean_lba": ("Nettoyage LBA", "src.structuration.clean_lba", "main"),
}

ALL_STEPS = {**EXTRA_STEPS, **STEPS}


def run_step(name: str) -> bool:
    """Run a single pipeline step. Returns True on success, False on failure."""
    label, module_path, func_name = ALL_STEPS[name]
    log.info("=== %s ===", label)
    try:
        module = importlib.import_module(module_path)
        getattr(module, func_name)()
        log.info("=== %s termine ===", label)
        return True
    except Exception as e:
        log.error("=== %s ECHEC: %s ===", label, e)
        return False


def main():
    parser = argparse.ArgumentParser(description="Pipeline BTB extraction")
    parser.add_argument("--all", action="store_true", help="Lancer tout le pipeline")
    parser.add_argument(
        "--steps",
        nargs="+",
        choices=ALL_STEPS.keys(),
        help="Etapes a lancer (inclut extract_db si besoin)",
    )
    parser.add_argument("--list", action="store_true", help="Lister les etapes")
    args = parser.parse_args()

    if args.list:
        print("\nEtapes --all (pipeline standard):")
        for name, (label, _, _) in STEPS.items():
            print(f"  {name:15s} - {label}")
        print("\nEtapes supplementaires (--steps extract_db ...):")
        for name, (label, _, _) in EXTRA_STEPS.items():
            print(f"  {name:15s} - {label}")
        print()
        return

    steps_to_run = list(STEPS.keys()) if args.all else (args.steps or [])

    if not steps_to_run:
        parser.print_help()
        sys.exit(1)

    log.info("Pipeline: %d etapes a lancer", len(steps_to_run))
    failed = []
    for step in steps_to_run:
        if not run_step(step):
            failed.append(step)

    if failed:
        log.warning(
            "Pipeline termine avec %d echec(s): %s", len(failed), ", ".join(failed)
        )
        sys.exit(1)
    else:
        log.info("Pipeline termine avec succes")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    main()
