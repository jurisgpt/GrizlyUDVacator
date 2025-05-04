# backend/rules/rule_engine.py

def evaluate_statutes(flags):
    """
    Given a list of flags, return applicable CCP statutes and the justification map.
    """
    rules = {
        "CCP § 473(b)": {
            "description": "Excusable neglect, mistake, surprise, or inadvertence",
            "flags": [
                "tenant_unaware_of_hearing",
                "mailing_not_done",
                "service_defective",
                "tenant_mistake_or_confusion",
                "unable_to_appear_due_to_emergency"
            ]
        },
        "CCP § 473(d)": {
            "description": "Void judgments due to lack of jurisdiction or facial defects",
            "flags": [
                "judgment_void_on_face",
                "no_subject_matter_jurisdiction",
                "wrong_party_named"
            ]
        },
        "CCP § 473.5": {
            "description": "Lack of actual notice of the lawsuit",
            "flags": [
                "no_actual_notice",
                "served_at_wrong_address",
                "mailing_failed",
                "did_not_receive_summons"
            ]
        }
    }

    result = {
        "statutes": [],
        "justification": {}
    }

    for statute, info in rules.items():
        matched_flags = [f for f in flags if f in info["flags"]]
        if matched_flags:
            result["statutes"].append(statute)
            result["justification"][statute] = matched_flags

    return result


