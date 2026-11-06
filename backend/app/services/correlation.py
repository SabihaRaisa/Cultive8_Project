
SEVERITY_RANK = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4
}


def normalize(value):
    """Normalize text for comparison."""
    return str(value or "").strip().lower()


def correlate_findings(findings):
    """
    Combine related findings from multiple log chunks.

    Findings are grouped by attack type and identifier.
    Original line numbers and evidence are preserved.
    """

    grouped = {}

    for finding in findings:

        attack_type = finding.get("attack_type", "")
        identifier = finding.get("identifier", "")

        if not attack_type or not identifier:
            continue

        key = (
            normalize(attack_type),
            normalize(identifier)
        )

        if key not in grouped:

            grouped[key] = {
                "attack_type": attack_type,
                "severity": finding.get("severity", "Low"),
                "identifier": identifier,
                "evidence_list": [],
                "line_numbers": [],
                "reason_list": [],
                "action_list": [],
                "source_chunks": []
            }

        existing = grouped[key]

        # Keep the strongest supported severity.
        new_severity = finding.get("severity", "Low")

        if (
            SEVERITY_RANK.get(new_severity, 0)
            > SEVERITY_RANK.get(existing["severity"], 0)
        ):
            existing["severity"] = new_severity

        # Preserve unique evidence.
        evidence = finding.get("evidence", "")

        if evidence and evidence not in existing["evidence_list"]:
            existing["evidence_list"].append(evidence)

        # Preserve original line numbers.
        for number in finding.get("line_numbers", []):

            if (
                isinstance(number, int)
                and not isinstance(number, bool)
                and number > 0
                and number not in existing["line_numbers"]
            ):
                existing["line_numbers"].append(number)

        # Preserve explanations.
        reason = finding.get("reason", "")

        if reason and reason not in existing["reason_list"]:
            existing["reason_list"].append(reason)

        # Preserve suggested actions.
        action = finding.get("suggested_action", "")

        if action and action not in existing["action_list"]:
            existing["action_list"].append(action)

        # Track which chunks contributed.
        chunk_number = finding.get("chunk_number")

        if (
            chunk_number is not None
            and chunk_number not in existing["source_chunks"]
        ):
            existing["source_chunks"].append(chunk_number)

    final_findings = []

    for item in grouped.values():

        item["line_numbers"].sort()
        item["source_chunks"].sort()

        final_findings.append({
            "attack_type": item["attack_type"],
            "severity": item["severity"],
            "identifier": item["identifier"],
            "evidence": " | ".join(item["evidence_list"]),
            "line_numbers": item["line_numbers"],
            "reason": " ".join(item["reason_list"]),
            "suggested_action": " ".join(item["action_list"]),
            "source_chunks": item["source_chunks"]
        })

    final_findings.sort(
        key=lambda item: SEVERITY_RANK.get(
            item["severity"], 0
        ),
        reverse=True
    )

    return final_findings
