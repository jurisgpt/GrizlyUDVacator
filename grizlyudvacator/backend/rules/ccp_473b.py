from datetime import datetime
from typing import Any, Dict, List


def evaluate_ccp_473b(answers: dict[str, Any]) -> list[str]:
    """
    Evaluate whether CCP § 473(b) applies based on the interview answers.

    Returns:
        List[str]: List of flags indicating which CCP § 473(b) conditions are met
    """
    flags = []

    # Check for excusable neglect
    if answers.get("tenant_unaware_of_hearing", False):
        flags.append("tenant_unaware_of_hearing")

    if answers.get("mailing_not_done", False):
        flags.append("mailing_not_done")

    if answers.get("service_defective", False):
        flags.append("service_defective")

    if answers.get("tenant_mistake_or_confusion", False):
        flags.append("tenant_mistake_or_confusion")

    if answers.get("unable_to_appear_due_to_emergency", False):
        flags.append("unable_to_appear_due_to_emergency")

    return flags
