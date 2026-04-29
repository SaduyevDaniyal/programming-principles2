from configparser import ConfigParser
from pathlib import Path


def config(filename="database.ini", section="postgresql"):
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename

    parser = ConfigParser()
    parser.read(file_path)

    if not parser.has_section(section):
        raise Exception(f"Section {section} not found in {file_path}")

    return dict(parser.items(section))
