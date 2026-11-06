
import json


ALLOWED_SEVERITIES = {
    "Low",
    "Medium",
    "High",
    "Critical"
}


REQUIRED_FIELDS = {
    "attack_type",
    "severity",
    "identifier",
    "evidence",
    "line_numbers",
    "reason",
    "suggested_action"
}


def validate_findings(response_text, valid_line_numbers):

    try:
        data = json.loads(response_text)

        if not isinstance(data, dict):
            return {
                "success": False,
                "findings": [],
                "error": "Response must be a JSON object."
            }

        findings = data.get("findings")

        if not isinstance(findings, list):
            return {
                "success": False,
                "findings": [],
                "error": "Findings must be a list."
            }

        valid_lines = set(valid_line_numbers)
        validated = []

        for finding in findings:

            if not isinstance(finding, dict):
                continue

            if not REQUIRED_FIELDS.issubset(finding.keys()):
                continue

            if finding["severity"] not in ALLOWED_SEVERITIES:
                continue

            line_numbers = finding["line_numbers"]

            if not isinstance(line_numbers, list) or not line_numbers:
                continue

            if not all(
                isinstance(number, int)
                and not isinstance(number, bool)
                and number in valid_lines
                for number in line_numbers
            ):
                continue

            if not all(
                isinstance(finding[field], str)
                and finding[field].strip()
                for field in REQUIRED_FIELDS - {
                    "severity", "line_numbers"
                }
            ):
                continue

            finding["line_numbers"] = sorted(set(line_numbers))
            validated.append(finding)

        return {
            "success": True,
            "findings": validated,
            "summary": data.get("summary", "")
        }

    except (json.JSONDecodeError, TypeError, ValueError) as error:

        return {
            "success": False,
            "findings": [],
            "error": f"Invalid AI JSON response: {error}"
        }
