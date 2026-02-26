import json
import os
from pathlib import Path
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from io import BytesIO

from config import Config
from services.comparison_service import ComparisonService
from services.dictionary_service import DictionaryService
from services.document_service import DocumentService
from services.tax_service import TaxService

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = Config.MAX_UPLOAD_MB * 1024 * 1024

comparison_service = ComparisonService()
dictionary_service = DictionaryService()
tax_service = TaxService()


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "contract-comparison-api"})


@app.post("/api/comparisons/scan")
def scan_folder():
    body = request.get_json(force=True)
    folder = body.get("input_folder", "")
    if not folder or not os.path.exists(folder):
        return jsonify({"error": "Input folder does not exist"}), 400

    valid_ext = {".pdf", ".docx", ".doc"}
    out = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if os.path.isfile(path) and Path(path).suffix.lower() in valid_ext:
            out.append(
                {
                    "name": name,
                    "path": path,
                    "type": Path(path).suffix.lower(),
                    "size": os.path.getsize(path),
                }
            )
    return jsonify({"files": out})


@app.post("/api/comparisons/run")
def run_comparisons():
    try:
        output_dir = request.form.get("output_folder") or str(Config.DEFAULT_OUTPUT_DIR)
        pairs_raw = request.form.get("pairs", "[]")
        pairs = json.loads(pairs_raw)

        files = request.files.getlist("files")
        file_map = {f.filename: f for f in files if f and f.filename}

        if not file_map:
            return jsonify({"error": "No files uploaded"}), 400

        results = comparison_service.run_batch(file_map, pairs, output_dir)
        return jsonify({"results": results})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.get("/api/dictionary")
def get_dictionary():
    return jsonify(dictionary_service.load())


@app.post("/api/dictionary")
def upsert_dictionary():
    body = request.get_json(force=True)
    key = body.get("word", "").strip()
    replacement = body.get("replacement", "").strip()
    case_sensitive = bool(body.get("case_sensitive", False))
    if not key or not replacement:
        return jsonify({"error": "Both word and replacement are required"}), 400

    updated = dictionary_service.upsert(key, replacement, case_sensitive=case_sensitive)
    return jsonify(updated)


@app.delete("/api/dictionary")
def clear_dictionary():
    return jsonify(dictionary_service.clear())


@app.delete("/api/dictionary/<key>")
def delete_dictionary_key(key):
    return jsonify(dictionary_service.delete(key))


@app.post("/api/dictionary/import")
def import_dictionary():
    mode = request.form.get("mode", "merge")
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "CSV file is required"}), 400

    updated = dictionary_service.import_csv(file, mode=mode)
    return jsonify(updated)


@app.get("/api/dictionary/export")
def export_dictionary():
    fmt = request.args.get("format", "json")
    if fmt == "csv":
        csv_content = dictionary_service.export_csv()
        return send_file(
            BytesIO(csv_content.encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name="replacement_dictionary.csv",
        )

    data = json.dumps(dictionary_service.load(), ensure_ascii=False, indent=2)
    return send_file(
        BytesIO(data.encode("utf-8")),
        mimetype="application/json",
        as_attachment=True,
        download_name="replacement_dictionary.json",
    )


@app.post("/api/tax/analyze")
def analyze_tax():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "Contract file is required"}), 400

        temp_path = DocumentService.save_temp_file(file)
        try:
            text = DocumentService.extract_text(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        if not text.strip():
            return jsonify({"error": "No text extracted from file"}), 400

        results = tax_service.analyze_contract(text, file_name=secure_filename(file.filename))
        return jsonify(results)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.post("/api/tax/export/excel")
def export_tax_excel():
    body = request.get_json(force=True)
    excel_bytes = tax_service.export_excel(body)
    return send_file(
        BytesIO(excel_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="enhanced_tax_analysis.xlsx",
    )


@app.post("/api/tax/export/json")
def export_tax_json():
    body = request.get_json(force=True)
    data = json.dumps(body, ensure_ascii=False, indent=2)
    return send_file(
        BytesIO(data.encode("utf-8")),
        mimetype="application/json",
        as_attachment=True,
        download_name="enhanced_tax_analysis.json",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
