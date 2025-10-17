import os, time, yaml
from typing import Dict
from .metrics_collector import MetricsCollector
from .issue_detector import IssueDetector
from .strategy_registry import StrategyRegistry
from .variant_builder import build_variant, variant_hash
from .sandbox_executor import SandboxExecutor
from .evaluator import VariantEvaluator
from .patch_store import PatchStore
from scrapers.logger import log_info, log_error

class CrawlerIterationEngine:
    def __init__(self, cfg_path="config/crawler_iter_config.yaml"):
        self.cfg = yaml.safe_load(open(cfg_path, "r", encoding="utf-8"))
        self.last_run_ts = 0
        self.metrics_collector = MetricsCollector()
        self.issue_detector = IssueDetector()
        self.strategy_registry = StrategyRegistry(self.cfg)
        self.sandbox = SandboxExecutor(self.cfg["sandbox_dir"])
        self.patch_store = PatchStore(self.cfg["patch_output_dir"])
        self.production_file = self.cfg["production_file"]

    def can_run(self) -> bool:
        if not self.cfg.get("enabled", True):
            return False
        now = time.time()
        if now - self.last_run_ts < self.cfg.get("min_interval_minutes", 30) * 60:
            return False
        return True

    def run_once(self) -> Dict:
        if not self.can_run():
            return {"status": "skipped", "reason": "interval or disabled"}

        self.last_run_ts = time.time()
        log_info("[AUTO-ITER] 开始自迭代流程")

        # 1. 基础指标
        base_metrics = self.metrics_collector.collect()
        issues = self.issue_detector.detect(base_metrics)
        log_info(f"[AUTO-ITER] Issues: {issues}")

        # 2. 选策略 & 生成变体配置
        chosen_strategies = self.strategy_registry.pick_strategies(issues)
        patch_conf = self.strategy_registry.materialize(chosen_strategies)

        # 3. 读取生产源码
        original_source = open(self.production_file, "r", encoding="utf-8").read()
        variant_source = build_variant(patch_conf, original_source, chosen_strategies)
        tag = variant_hash(variant_source)

        # 4. 沙箱测试 A/B
        variant_path = self.sandbox.write_variant(variant_source, tag)
        prod_module = self.sandbox._dynamic_import(self.production_file)
        variant_module = self.sandbox._dynamic_import(variant_path)

        base_stats = self.sandbox.run_test(prod_module, self.cfg["test_urls"])
        new_stats = self.sandbox.run_test(variant_module, self.cfg["test_urls"])

        evaluator = VariantEvaluator(
            weights=self.cfg["weights"],
            threshold=self.cfg["score_threshold"],
            require_error_drop=self.cfg["require_error_drop"]
        )
        eval_result = evaluator.score(base_stats, new_stats)
        log_info(f"[AUTO-ITER] Eval result: {eval_result}")

        # 5. 如果通过 → 生成补丁文件
        if eval_result["passed"]:
            patch_path = self.patch_store.build_patch(original_source, variant_source, tag)
            return {
                "status": "candidate",
                "tag": tag,
                "patch_path": patch_path,
                "strategies": chosen_strategies,
                "base_stats": base_stats,
                "new_stats": new_stats,
                "score": eval_result["raw_score"]
            }
        else:
            return {
                "status": "rejected",
                "reason": "score_not_improved",
                "strategies": chosen_strategies,
                "base_stats": base_stats,
                "new_stats": new_stats,
                "score": eval_result["raw_score"]
            }

    def apply_patch(self, tag: str):
        patch_file = os.path.join(self.cfg["patch_output_dir"], f"{tag}.patch")
        variant_file = os.path.join(self.cfg["sandbox_dir"], f"amazon_scraper_{tag}.py")
        if not (os.path.exists(patch_file) and os.path.exists(variant_file)):
            return {"status": "error", "reason": "patch_or_variant_missing"}
        variant_code = open(variant_file, "r", encoding="utf-8").read()
        backup = self.patch_store.apply_patch_direct(patch_file, self.production_file, variant_code)
        log_info(f"[AUTO-ITER] 补丁已应用: {tag}, 备份: {backup}")
        return {"status": "applied", "tag": tag, "backup": backup}