"""Comandos locais de importação."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from rastro.store import import_zip


def main() -> None:
    parser = argparse.ArgumentParser(prog="rastro")
    commands = parser.add_subparsers(dest="command", required=True)
    importer = commands.add_parser("import", help="Importa o ZIP de emendas da CGU")
    importer.add_argument("--db", type=Path, required=True)
    importer.add_argument("--zip", dest="zip_path", type=Path, required=True)
    args = parser.parse_args()

    result = import_zip(args.db, args.zip_path)
    print(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
