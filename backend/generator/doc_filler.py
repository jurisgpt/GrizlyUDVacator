# backend/generator/doc_filler.py

from docxtpl import DocxTemplate
import os
from datetime import datetime

gdef generate_motion(answers, result):
    template_path = os.path.join(os.path.dirname(__file__), "templates", "motion_template.docx")
    output_path = os.path.join("cli", f"motion_to_vacate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx")

    doc = DocxTemplate(template_path)

    context = {
        "statute_list": ", ".join(result["statutes"]),
        "justification": result["justification"],
        "facts": "\n".join(f"{k}: {v}" for k, v in answers.items())
    }

    doc.render(context)
    doc.save(output_path)
 

def generate_summary_md(answers, result):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"summary_{timestamp}.md"
    output_path = os.path.join("cli", filename)

    with open(output_path, "w") as f:
        f.write("# 🧾 Motion to Vacate: Interview Summary\n\n")

        f.write("## 📜 Recommended Statutes\n")
        for statute in result["statutes"]:
            f.write(f"- **{statute}**\n")
            for reason in result["justification"][statute]:
                f.write(f"  - Reason: {reason}\n")
        f.write("\n")

        f.write("## 👤 Interview Answers\n")
        for question, answer in answers.items():
            f.write(f"- **{question}**: {answer}\n")

   print(f"✅ Motion saved to: {output_path}")


