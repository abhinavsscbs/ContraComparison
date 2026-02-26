import json
import re
from datetime import datetime
from io import BytesIO
import pandas as pd

from cohere_client import CohereClient


class TaxService:
    def __init__(self):
        self.ai = CohereClient()

    def _extract_json(self, raw, default):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r"\[[\s\S]*\]", raw)
            if m:
                try:
                    return json.loads(m.group(0))
                except json.JSONDecodeError:
                    return default
            return default

    def extract_clauses_ai(self, text, max_clauses=30):
        prompt = f"""
Identify distinct clauses from this contract and return JSON array only:
[
  {{"title":"...","full_text":"...","category":"...","summary":"..."}}
]
Rules:
- Keep exact clause text in full_text.
- Do not emit markdown.
- Max {max_clauses} clauses.

TEXT:
{text[:24000]}
"""
        raw = self.ai.chat(
            "You are a legal analyst. Return valid JSON only.",
            prompt,
            temperature=0.1,
        )
        clauses = self._extract_json(raw, [])
        cleaned = []
        for c in clauses:
            if not isinstance(c, dict):
                continue
            if len(c.get("full_text", "").strip()) < 30:
                continue
            cleaned.append(
                {
                    "title": c.get("title", "Clause"),
                    "full_text": c.get("full_text", ""),
                    "category": c.get("category", "General"),
                    "summary": c.get("summary", "Contract provision"),
                }
            )
            if len(cleaned) >= max_clauses:
                break
        return cleaned

    def extract_clauses_fallback(self, text, max_clauses=30):
        chunks = re.split(r"\n\s*(?=\d+\.|Article|Section|Clause)", text, flags=re.IGNORECASE)
        out = []
        for idx, chunk in enumerate(chunks, start=1):
            item = re.sub(r"\s+", " ", chunk).strip()
            if len(item) < 50:
                continue
            out.append(
                {
                    "title": f"Clause {idx}",
                    "full_text": item,
                    "category": "Contract Provision",
                    "summary": "Extracted by fallback parser",
                }
            )
            if len(out) >= max_clauses:
                break
        return out

    def executive_summary(self, text):
        prompt = f"Provide a concise executive summary of this contract in 3-4 short paragraphs.\n\n{text[:16000]}"
        return self.ai.chat(
            "You are a legal contract analyst writing concise executive summaries.",
            prompt,
            temperature=0.2,
        )

    def detailed_analysis(self, text):
        prompt = f"""
Provide pointwise contract analysis sections for:
1) Structure 2) Parties 3) Scope 4) Financial terms 5) Timeline
6) Risk 7) Compliance 8) Termination 9) IP 10) Dispute resolution.
Use concise bullets.

{text[:20000]}
"""
        return self.ai.chat(
            "You are a legal contract analyst writing structured bullet analysis.",
            prompt,
            temperature=0.2,
        )

    def clause_tax_analysis(self, clause):
        prompt = f"""
Analyze tax implications for this clause with sections:
- Clause Summary
- Primary Tax Implications
- Applicable Tax Treatments
- Risk Assessment (High/Medium/Low)
- Recommendations

Title: {clause['title']}
Category: {clause['category']}
Text: {clause['full_text']}
"""
        return self.ai.chat(
            "You are a senior tax specialist. Give practical, actionable analysis.",
            prompt,
            temperature=0.2,
        )

    def analyze_contract(self, full_text, file_name="uploaded"):
        clauses = self.extract_clauses_ai(full_text)
        if not clauses:
            clauses = self.extract_clauses_fallback(full_text)

        exec_summary = self.executive_summary(full_text)
        detailed = self.detailed_analysis(full_text)

        results = []
        for clause in clauses:
            tax_text = self.clause_tax_analysis(clause)
            risk = "Medium"
            low = tax_text.lower()
            if any(k in low for k in ["high risk", "critical", "significant risk"]):
                risk = "High"
            elif any(k in low for k in ["low risk", "minimal risk"]):
                risk = "Low"
            results.append(
                {
                    "clause_data": clause,
                    "tax_analysis": tax_text,
                    "risk_level": risk,
                    "sources_used": 0,
                    "best_match_score": 0,
                    "tax_info": {"source_chunks": []},
                }
            )

        return {
            "file_name": file_name,
            "timestamp": datetime.now().isoformat(),
            "analysis_method": "Cohere AI-powered",
            "executive_summary": exec_summary,
            "detailed_analysis": detailed,
            "analysis_results": results,
            "total_clauses": len(results),
        }

    def export_excel(self, results):
        out = BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            pd.DataFrame(
                {
                    "Analysis Type": [
                        "Executive Summary",
                        "Detailed Analysis",
                        "Analysis Method",
                        "Total Clauses",
                        "Analysis Date",
                        "File Name",
                    ],
                    "Content": [
                        results.get("executive_summary", ""),
                        results.get("detailed_analysis", ""),
                        results.get("analysis_method", ""),
                        str(results.get("total_clauses", 0)),
                        results.get("timestamp", ""),
                        results.get("file_name", ""),
                    ],
                }
            ).to_excel(writer, sheet_name="Summary", index=False)

            detail_rows = []
            risk_rows = []
            for idx, row in enumerate(results.get("analysis_results", []), start=1):
                clause = row.get("clause_data", {})
                detail_rows.append(
                    {
                        "Clause_Number": idx,
                        "Clause_Title": clause.get("title", ""),
                        "Clause_Category": clause.get("category", ""),
                        "Clause_Summary": clause.get("summary", ""),
                        "Original_Clause_Text": clause.get("full_text", ""),
                        "Tax_Analysis": row.get("tax_analysis", ""),
                        "Risk_Level": row.get("risk_level", ""),
                    }
                )
                risk_rows.append(
                    {
                        "Clause_Number": idx,
                        "Clause_Title": clause.get("title", ""),
                        "Risk_Level": row.get("risk_level", ""),
                        "Category": clause.get("category", ""),
                    }
                )

            pd.DataFrame(detail_rows).to_excel(writer, sheet_name="Detailed_Analysis", index=False)
            pd.DataFrame(risk_rows).to_excel(writer, sheet_name="Risk_Assessment", index=False)

        out.seek(0)
        return out.getvalue()
