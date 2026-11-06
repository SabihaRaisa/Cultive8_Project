
import json

from app.services.security_prompt import build_analysis_prompt
from app.services.finding_validator import validate_findings


def main():

    print("Testing security prompt...")

    prompt = build_analysis_prompt(
        log_text="Line 5: Failed login from 192.168.1.10",
        saved_context=""
    )

    assert "untrusted data" in prompt.lower()

    print("Security prompt: PASSED")

    print("\nTesting finding validator...")

    sample_response = {
        "findings": [
            {
                "attack_type": "Possible brute-force attack",
                "severity": "High",
                "identifier": "192.168.1.10",
                "evidence": "Repeated failed login attempts.",
                "line_numbers": [5, 8],
                "reason": "Multiple failed login events.",
                "suggested_action": "Review authentication activity."
            }
        ],
        "summary": "Suspicious login activity detected."
    }

    result = validate_findings(
        json.dumps(sample_response),
        [5, 8, 10]
    )

    assert result["success"] is True
    assert len(result["findings"]) == 1

    print("Valid finding: PASSED")

    invalid_result = validate_findings(
        json.dumps(sample_response),
        [5, 10]
    )

    assert len(invalid_result["findings"]) == 0

    print("Invalid line number rejection: PASSED")

    print("\nALL TESTS PASSED!")


if __name__ == "__main__":
    main()
