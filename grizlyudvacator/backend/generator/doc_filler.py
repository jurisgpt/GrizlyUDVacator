# backend/generator/doc_filler.py

from datetime import datetime
from pathlib import Path

from docxtpl import DocxTemplate


def generate_motion(answers, result):
    template_path = Path(__file__).parent / "templates" / "motion_template.docx"
    output_path = (
        Path("output")
        / "documents"
        / f"motion_to_vacate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    )

    try:
        # Load template and create output paths
        doc = DocxTemplate(template_path)

        # Prepare context for template rendering
        context = {
            "statute_list": ", ".join(result["statutes"]),
            "justification": result["justification"],
            "facts": "\n".join(f"{k}: {v}" for k, v in answers.items()),
        }

        # Render and save document
        doc.render(context)
        doc.save(output_path)

        # Generate summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_path = Path("output") / "documents" / f"motion_summary_{timestamp}.md"

        with open(summary_path, "w") as f:
            f.write("# 📄 Motion to Vacate Summary\n\n")
            f.write(
                f"## 📅 Date Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
            f.write("## 📋 Statutes\n")
            for statute in result["statutes"]:
                f.write(f"- {statute}\n")
            f.write("\n## 📝 Justification\n")
            f.write(f"{result['justification']}\n\n")
            f.write("## 📋 Facts\n")
            for k, v in answers.items():
                f.write(f"- **{k}**: {v}\n")

        print(f"✅ Motion saved to: {output_path}")
        return str(output_path)
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
    summary_path = Path("output") / "documents" / f"motion_summary_{timestamp}.md"

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
