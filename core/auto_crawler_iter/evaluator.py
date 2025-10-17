from typing import Dict

class VariantEvaluator:
    def __init__(self, weights: Dict, threshold: float, require_error_drop: bool):
        self.weights = weights
        self.threshold = threshold
        self.require_error_drop = require_error_drop

    def score(self, base_stats: Dict, new_stats: Dict) -> Dict:
        # Δ 计算
        delta_items = new_stats["items"] - base_stats["items"]
        delta_zero = new_stats["zero_pages"] - base_stats["zero_pages"]
        delta_time = (new_stats["avg_time"] or 0) - (base_stats["avg_time"] or 0)
        delta_errors = new_stats["errors"] - base_stats["errors"]

        # 简单归一：用旧值防止除零扩展，可直接用绝对差乘权重
        raw_score = (self.weights["items"] * delta_items
                     + self.weights["zero"] * delta_zero
                     + self.weights["time"] * delta_time
                     + self.weights["errors"] * delta_errors)

        passed = raw_score >= self.threshold
        if self.require_error_drop and delta_errors > 0:
            passed = False

        return {
            "delta": {
                "items": delta_items,
                "zero": delta_zero,
                "time": delta_time,
                "errors": delta_errors
            },
            "raw_score": round(raw_score, 3),
            "passed": passed
        }