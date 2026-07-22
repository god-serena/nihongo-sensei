import os
import re
import sys
import gzip
import urllib.request
import tempfile
import xml.etree.ElementTree as ET
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models import DictionaryEntry

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/kotosensei")
JMDICT_URL = "https://ftp.edrdg.org/pub/Nihongo/JMdict_e.gz"
BATCH_SIZE = 1000


def download_jmdict(dest_path: str):
    print(f"Downloading JMdict from {JMDICT_URL}...")
    urllib.request.urlretrieve(JMDICT_URL, dest_path)
    print("Download complete.")


def pre_process_xml(input_path: str, output_file):
    print("Preprocessing XML to handle custom entities...")
    # Open input file (handling gzip if necessary)
    if input_path.endswith(".gz"):
        infile = gzip.open(input_path, "rt", encoding="utf-8", errors="ignore")
    else:
        infile = open(input_path, "r", encoding="utf-8", errors="ignore")

    # Regular expression to escape XML entities that are not the standard 5
    # (amp, lt, gt, quot, apos).
    entity_re = re.compile(r"&(?!(amp|lt|gt|quot|apos);)")

    try:
        for line in infile:
            # Escape custom entities
            processed_line = entity_re.sub("&amp;", line)
            output_file.write(processed_line.encode("utf-8"))
    finally:
        infile.close()

    output_file.flush()
    output_file.seek(0)
    print("Preprocessing complete.")


def clean_pos(pos_text: str) -> str:
    # Remove leading/trailing & and ; from processed entities
    if pos_text.startswith("&") and pos_text.endswith(";"):
        return pos_text[1:-1]
    return pos_text


def ingest(file_path: str):
    # Setup DB
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    # Preprocess file
    with tempfile.NamedTemporaryFile(suffix=".xml") as temp_xml:
        pre_process_xml(file_path, temp_xml)

        print("Parsing XML and inserting into DB...")
        context = ET.iterparse(temp_xml.name, events=("start", "end"))
        context = iter(context)
        event, root = next(context)  # get root element

        batch = []
        count = 0

        for event, elem in context:
            if event == "end" and elem.tag == "entry":
                # Parse entry
                seq = elem.findtext("ent_seq")

                kanji_list = [k.text for k in elem.findall(".//k_ele/keb") if k.text]
                reading_list = [r.text for r in elem.findall(".//r_ele/reb") if r.text]

                senses = []
                for sense_elem in elem.findall("sense"):
                    glosses = [g.text for g in sense_elem.findall("gloss") if g.text]
                    pos_list = [clean_pos(p.text) for p in sense_elem.findall("pos") if p.text]
                    senses.append({
                        "glosses": glosses,
                        "parts_of_speech": pos_list
                    })

                entry = DictionaryEntry(
                    sequence_number=seq,
                    kanji=kanji_list,
                    reading=reading_list,
                    senses=senses
                )
                batch.append(entry)

                if len(batch) >= BATCH_SIZE:
                    db.bulk_save_objects(batch)
                    db.commit()
                    count += len(batch)
                    print(f"Ingested {count} entries...")
                    batch = []

                # Clear elements to save memory
                elem.clear()
                root.clear()

        if batch:
            db.bulk_save_objects(batch)
            db.commit()
            count += len(batch)
            print(f"Ingested {count} entries...")

    db.close()
    print(f"Finished ingesting {count} entries successfully.")


if __name__ == "__main__":
    target_path = None
    if len(sys.argv) > 1:
        target_path = sys.argv[1]

    if not target_path:
        # If no path specified, check for local file first, otherwise download
        local_gz = "JMdict_e.gz"
        if not os.path.exists(local_gz):
            download_jmdict(local_gz)
            target_path = local_gz
        else:
            print(f"Found local file: {local_gz}")
            target_path = local_gz

    ingest(target_path)
