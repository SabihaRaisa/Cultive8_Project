
from app.services.correlation import correlate_findings


def main():

    print("Testing cross-chunk correlation...")

    sample_findings = [

        {
            "attack_type": "Possible brute-force attack",
            "severity": "Medium",
            "identifier": "192.168.1.10",
            "evidence": "Repeated failed login attempts.",
            "line_numbers": [5, 8],
            "reason": "Multiple failed logins detected.",
            "suggested_action": "Review authentication activity.",
            "chunk_number": 1
        },

        {
            "attack_type": "Possible brute-force attack",
            "severity": "High",
            "identifier": "192.168.1.10",
            "evidence": "Additional failed login attempts.",
            "line_numbers": [8, 12, 15],
            "reason": "The attempts continued in another chunk.",
            "suggested_action": "Investigate the source IP.",
            "chunk_number": 2
        },

        {
            "attack_type": "Possible SQL injection",
            "severity": "Medium",
            "identifier": "192.168.1.20",
            "evidence": "Suspicious SQL query parameters.",
            "line_numbers": [30],
            "reason": "Possible SQL injection indicator.",
            "suggested_action": "Review the request.",
            "chunk_number": 3
        }
    ]

    results = correlate_findings(sample_findings)

    print("\n========== CORRELATION RESULTS ==========")

    for finding in results:
        print("\nAttack:", finding["attack_type"])
        print("Severity:", finding["severity"])
        print("Identifier:", finding["identifier"])
        print("Lines:", finding["line_numbers"])
        print("Chunks:", finding["source_chunks"])
        print("Evidence:", finding["evidence"])

    # Verify brute-force findings were combined.
    brute_force = next(
        item for item in results
        if item["identifier"] == "192.168.1.10"
    )

    assert brute_force["severity"] == "High"
    assert brute_force["line_numbers"] == [5, 8, 12, 15]
    assert brute_force["source_chunks"] == [1, 2]

    assert len(results) == 2

    print("\nSUCCESS: Cross-chunk correlation passed!")


if __name__ == "__main__":
    main()
