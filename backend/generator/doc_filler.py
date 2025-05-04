# backend/generator/doc_filler.py

from docxtpl import DocxTemplate
import os
from datetime import datetime

def generate_motion(answers, result):
    template_path = os.path.join(os.path.dirname(__file__), "templates", "motion_template.docx")
    output_path = os.path.join("cli", f"motion_to_vacate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx")

    try:
        # Load template and create output paths
        doc = DocxTemplate(template_path)
        
        # Prepare context for template rendering
        context = {
            "statute_list": ", ".join(result["statutes"]),
            "justification": result["justification"],
            "facts": "\n".join(f"{k}: {v}" for k, v in answers.items())
        }
        
        # Generate Word document
        doc.render(context)
        doc.save(output_path)
        
        # Generate markdown summary
        with open(os.path.join("cli", f"motion_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"), "w") as f:
            f.write("# 📝 Motion to Vacate Summary\n\n")
            f.write(f"## 📅 Date Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
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
        return output_path
    except FileNotFoundError:
        raise FileNotFoundError(f"Template file not found at {template_path}")
    except Exception as e:
        print(f"❌ Error occurred while saving motion: {str(e)}")
        return None

def generate_summary_md(answers, result):
    if not answers or not isinstance(answers, dict):
        print("⚠️ Invalid answers data provided")
        return None

    if not result or not isinstance(result, dict):
        print("⚠️ Invalid result data provided")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"summary_{timestamp}.md"
    output_path = os.path.join("cli", filename)

    # Create cli directory if it doesn't exist
    os.makedirs("cli", exist_ok=True)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# 🧾 Motion to Vacate: Interview Summary\n\n")

            # Handle case with no statutes
            if not result["statutes"]:
                f.write("## 📜 No Applicable Statutes Found\n")
                f.write("No potential statutes found based on the provided answers.\n")
            else:
                f.write("## 📜 Recommended Statutes\n")
                for statute in result["statutes"]:
                    f.write(f"- **{statute}**\n")
                    for reason in result["justification"][statute]:
                        f.write(f"  - Reason: {reason}\n")
                f.write("\n")

            f.write("## 👤 Interview Answers\n")
            if not answers:
                f.write("No interview answers recorded.\n")
            else:
                for question, answer in answers.items():
                    # Format multi-select answers nicely
                    if isinstance(answer, list):
                        f.write(f"- **{question}:**\n")
                        for item in answer:
                            f.write(f"  - {item}\n")
                    else:
                        f.write(f"- **{question}**: {answer}\n")

        print(f"✅ Markdown summary saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"⚠️ Error writing summary: {str(e)}")
        return None
