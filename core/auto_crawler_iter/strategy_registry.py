import random
from typing import Dict, List

class StrategyRegistry:
    """
    每个策略返回一个dict，描述要修改的配置片段。
    """
    def __init__(self, cfg: Dict):
        self.cfg = cfg

    def pick_strategies(self, issues: List[str]) -> List[str]:
        enabled = self.cfg.get("strategies_enabled", [])
        chosen = set()
        for issue in issues:
            if issue == "low_yield" and "extend_selectors" in enabled:
                chosen.add("extend_selectors")
            if issue == "too_many_zeros" and "fallback_data_asins" in enabled:
                chosen.add("fallback_data_asins")
            if issue == "captcha_blocks" and "switch_user_agent" in enabled:
                chosen.add("switch_user_agent")
            if issue == "frequent_errors" and "add_second_pass" in enabled:
                chosen.add("add_second_pass")
        # 补充一个保底策略
        if not chosen and enabled:
            chosen.add(random.choice(enabled))
        return list(chosen)

    def materialize(self, strategy_list: List[str]) -> Dict:
        patch_conf = {}
        base = self.cfg.get("selector_bundles", {}).get("base", {})
        extended = self.cfg.get("selector_bundles", {}).get("extended", {})
        # 默认使用 base
        patch_conf.update(base)

        if "extend_selectors" in strategy_list:
            patch_conf.update(extended)

        if "switch_user_agent" in strategy_list:
            patch_conf["ua_mode"] = "hybrid"
        else:
            patch_conf["ua_mode"] = "desktop"

        if "increase_scroll_cycles" in strategy_list:
            patch_conf["scroll_cycles"] = self.cfg.get("scroll_cycles_extended", 5)
        else:
            patch_conf["scroll_cycles"] = self.cfg.get("scroll_cycles_base", 3)

        if "adjust_wait_time" in strategy_list:
            patch_conf["wait_min"] = self.cfg.get("wait_time_extended", {}).get("min", 1.2)
            patch_conf["wait_max"] = self.cfg.get("wait_time_extended", {}).get("max", 2.2)
        else:
            patch_conf["wait_min"] = self.cfg.get("wait_time_base", {}).get("min", 1.0)
            patch_conf["wait_max"] = self.cfg.get("wait_time_base", {}).get("max", 1.6)

        patch_conf["enable_second_pass"] = ("add_second_pass" in strategy_list)
        patch_conf["enable_fallback_asin"] = ("fallback_data_asins" in strategy_list)
        return patch_conf