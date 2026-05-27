# test_matrix.py
# Swarup builds this in Week 2
# Automated runner for all 11 vendor test cases

# Placeholder — implementation coming Week 2

TEST_VENDORS = [
    {"name": "ClearPath Logistics", "expected_score": 18, "expected_path": "auto_approve"},
    {"name": "Nexus Global Holdings", "expected_score": 72, "expected_path": "auto_reject"},
    {"name": "ErrorTrigger Inc.", "expected_score": None, "expected_path": "exception"},
    {"name": "asdfghjkl corp", "expected_score": None, "expected_path": "human_review"},
    {"name": "Sneaky Risk Ltd", "expected_score": 25, "expected_path": "human_review"},
    # 6 more to be defined
]
