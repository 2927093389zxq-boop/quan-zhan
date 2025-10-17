from typing import Dict, List

class IssueDetector:
    def detect(self, metrics: Dict) -> List[str]:
        issues = []
        if metrics.get("files_scanned", 0) >= 5 and metrics.get("avg_items_per_file", 0) < 3:
            issues.append("low_yield")
        if metrics.get("zero_files", 0) > 2:
            issues.append("too_many_zeros")
        if metrics.get("captcha_hits", 0) > 0:
            issues.append("captcha_blocks")
        if metrics.get("error_lines", 0) > 5:
            issues.append("frequent_errors")
        return issues