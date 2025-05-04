# 📚  GrizlyUDVacator - Attorney Decision Aid 

**GrizlyUDVacator** automates case intake, case triage  through motion practice under California law for tenants seeking  seeting aside default judgments in unlawful detainer (eviction) actions. This document catalogs the California statutes, case law, and judicial forms embedded in the project’s rule engine and document generator.

---

## 📜 California Statutes

| Code Section       | Summary |
|--------------------|---------|
| **CCP § 473(b)**    | Motion to set aside for excusable neglect, inadvertence, mistake, or surprise. Must be filed within 6 months of judgment. |
| **CCP § 473.5**     | Motion to set aside judgment due to lack of actual notice. Must be filed within 2 years of judgment or 180 days after notice was discovered. |
| **CCP § 473(d)**    | Motion to set aside a void judgment. No strict deadline — must be brought within a “reasonable time.” |
| **CCP § 918**       | Motion to stay enforcement of a judgment while a set-aside motion is pending. |
| **CCP § 1005**      | Governs service timing for motions. Requires at least 16 court days notice before hearing (+5 calendar days if served by mail). |

---

## 📚 California Case Law

| Case Name and Citation | Legal Significance |
|------------------------|--------------------|
| **Rappleyea v. Campbell** (1994) 8 Cal.4th 975 | Strong presumption in favor of trial on the merits; procedural defaults should be relieved if possible. |
| **Elston v. City of Turlock** (1985) 38 Cal.3d 227 | Courts must liberally apply § 473 to promote justice; especially where neglect is excusable. |
| **Goya v. P.E.R.U. Enterprises** (1978) 87 Cal.App.3d 886 | Leading case on § 473.5; clarifies that lack of notice is grounds for relief even with valid service. |
| **Rogers v. Silverman** (1989) 216 Cal.App.3d 1114 | Motion under § 473(d) must be brought in “reasonable time” — not tied to hard deadline. |
| **Nagel v. P & M Distributors** (1969) 273 Cal.App.2d 176 | If a judgment is void on its face, there is no deadline to set it aside. |
| **Stebley v. Litton Loan Servicing** (2011) 202 Cal.App.4th 522 | Minor procedural defects in a declaration should not bar meritorious relief. |
| **Weitz v. Yankosky** (1966) 63 Cal.2d 849 | Defines “void” vs. “voidable” judgments — critical for asserting § 473(d) relief. |

---

## 🧾 Judicial Council Forms and Procedural Filings

| Form / Document       | Use |
|-----------------------|-----|
| **UD-105**            | Judicial Council form for filing an Answer in an Unlawful Detainer case |
| **UD-150**            | Used to request a trial date once a motion is filed or an Answer is submitted |
| **MC-040**            | General-purpose Declaration form, attached to support motion facts |
| **POS-040**           | Proof of Service by Mail — required when serving motion documents |
| **[Proposed Order]**  | Custom form submitted with the motion to assist the judge in ruling |
| **FW-001 / FW-003**   | Request for Fee Waiver and proposed order — used if the tenant cannot afford the motion filing fee |

---

## 🧠 How These Are Used

The above authorities are embedded in the following modules:

- `cli/prompts/vacate_default.yaml` — Interview flow maps user responses to these statutes
- `backend/rules/` — Each rule engine file implements conditions and triggers from one or more statutes
- `backend/generator/doc_filler.py` — Uses legal context to generate appropriate paragraphs and attach required forms
- `docs/INTERVIEW_DESIGN.md` — Explains which responses activate specific statutes and legal theories

---

## 🔍 Citation Transparency

GrizlyUDVacator prioritizes transparency by explicitly referencing legal authorities in all generated documents:
- Motions include named statutes in headings (e.g., "Motion to Set Aside Default Judgment Under CCP § 473(b)")
- Supporting declarations cite relevant case law to reinforce equitable arguments
- All logic branches are traceable in code and documentation

---

## 🤝 Contributions Welcome

To improve this list, propose additions in GitHub discussions or open a pull request. We're especially looking for:
- Case law summaries
- County-specific local rule references
- Annotated examples of procedural variations

---

*This page is maintained by the GrizlyUDVacator project team. Updated May 2025.*

