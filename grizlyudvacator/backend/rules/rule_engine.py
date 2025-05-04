# backend/rules/rule_engine.py
from .ccp_473b import evaluate_ccp_473b


def evaluate_statutes(answers):
    """
    Given a list of flags, return applicable CCP statutes and the justification map.
    """
    # Evaluate CCP § 473(b) first
    ccp_473b_flags = evaluate_ccp_473b(answers)
    if ccp_473b_flags:
        return {
            "statutes": ["CCP § 473(b)"],
            "justification": "Excusable neglect, mistake, surprise, or inadvertence",
        }

    # If no CCP § 473(b) flags, check for other conditions
    if answers.get("judgment_void_on_face", False):
        return {
            "statutes": ["CCP § 473(d)"],
            "justification": "Void judgment due to lack of jurisdiction or facial defects",
        }

    return {"statutes": [], "justification": {}}

    for statute, info in rules.items():
        matched_flags = [f for f in flags if f in info["flags"]]
        if matched_flags:
            result["statutes"].append(statute)
            result["justification"][statute] = matched_flags

    return result
