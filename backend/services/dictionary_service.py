import csv
import io
import json
from pathlib import Path
from config import Config


class DictionaryService:
    def __init__(self):
        self.path = Path(Config.DICTIONARY_FILE)

    def load(self):
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def upsert(self, key, value, case_sensitive=False):
        data = self.load()
        normalized_key = key if case_sensitive else key.lower()
        data[normalized_key] = value
        self.save(data)
        return data

    def delete(self, key):
        data = self.load()
        if key in data:
            del data[key]
            self.save(data)
        return data

    def clear(self):
        self.save({})
        return {}

    def import_csv(self, file_storage, mode="merge"):
        text = file_storage.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        incoming = {}
        for row in reader:
            if row.get("Word") and row.get("Replacement"):
                incoming[row["Word"]] = row["Replacement"]

        current = self.load()
        if mode == "replace":
            current = incoming
        else:
            current.update(incoming)

        self.save(current)
        return current

    def export_csv(self):
        data = self.load()
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["Word", "Replacement"])
        for k, v in data.items():
            writer.writerow([k, v])
        return out.getvalue()
