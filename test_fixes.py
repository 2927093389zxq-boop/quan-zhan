#!/usr/bin/env python3
"""
测试脚本 - 验证所有修复的模块
Test script - Verify all fixed modules
"""
import sys

def test_all_imports():
    """测试所有模块导入"""
    print("=" * 60)
    print("测试所有模块导入 / Testing all module imports")
    print("=" * 60)
    
    modules = [
        "run_launcher",
        "scheduler", 
        "scheduler_batch",
        "ui.dashboard",
        "ui.analytics",
        "ui.prototype_view",
        "ui.api_admin",
        "ui.auto_evolution",
        "ui.auto_patch_view",
        "ui.ai_learning_center",
        "ui.source_attribution",
        "core.data_fetcher",
        "core.collectors.market_collector",
        "core.collectors.youtube_collector",
        "core.collectors.policy_collector",
        "core.processing.recommender",
        "core.processing.anomaly_detector",
        "core.crawl.dispatcher",
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module}: {e}")
            failed.append((module, str(e)))
    
    return len(failed) == 0, failed

def test_data_fetcher():
    """测试数据获取器"""
    print("\n" + "=" * 60)
    print("测试数据获取器 / Testing data fetcher")
    print("=" * 60)
    
    try:
        from core.data_fetcher import get_platform_data, PLATFORM_LIST
        
        print(f"支持的平台 / Supported platforms: {PLATFORM_LIST}")
        
        # Test demo data
        data = get_platform_data("1688", keyword="test", max_items=3)
        assert len(data) == 3, "Should return 3 items"
        assert "title" in data[0], "Should have title field"
        print(f"✓ 1688 demo data: {len(data)} items retrieved")
        
        return True, None
    except Exception as e:
        return False, str(e)

def test_anomaly_detector():
    """测试异常检测器"""
    print("\n" + "=" * 60)
    print("测试异常检测器 / Testing anomaly detector")
    print("=" * 60)
    
    try:
        from core.processing.anomaly_detector import detect_anomalies
        
        # Test with known anomaly
        data = [100, 103, 120, 115, 420, 130, 110]
        anomalies = detect_anomalies(data)
        
        assert 4 in anomalies, "Should detect anomaly at index 4"
        print(f"✓ Detected anomalies at indices: {anomalies}")
        print(f"  - Anomaly value at position 4: {data[4]}")
        
        return True, None
    except Exception as e:
        return False, str(e)

def test_youtube_collector():
    """测试 YouTube 收集器"""
    print("\n" + "=" * 60)
    print("测试 YouTube 收集器 / Testing YouTube collector")
    print("=" * 60)
    
    try:
        from core.collectors.youtube_collector import fetch_channel_stats
        
        result = fetch_channel_stats("test_channel_id")
        
        # Should gracefully handle missing API key
        assert "error" in result or "channel_id" in result
        print(f"✓ YouTube collector handles missing API key gracefully")
        
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    """主测试函数"""
    print("\n🧪 开始测试 quan-zhan 项目修复 / Starting quan-zhan fixes test\n")
    
    all_passed = True
    
    # Test 1: Module imports
    success, failed = test_all_imports()
    if not success:
        print(f"\n❌ {len(failed)} 个模块导入失败:")
        for module, error in failed:
            print(f"   - {module}: {error}")
        all_passed = False
    else:
        print(f"\n✅ 所有模块导入成功!")
    
    # Test 2: Data fetcher
    success, error = test_data_fetcher()
    if not success:
        print(f"\n❌ 数据获取器测试失败: {error}")
        all_passed = False
    else:
        print(f"✅ 数据获取器测试通过!")
    
    # Test 3: Anomaly detector
    success, error = test_anomaly_detector()
    if not success:
        print(f"\n❌ 异常检测器测试失败: {error}")
        all_passed = False
    else:
        print(f"✅ 异常检测器测试通过!")
    
    # Test 4: YouTube collector
    success, error = test_youtube_collector()
    if not success:
        print(f"\n❌ YouTube 收集器测试失败: {error}")
        all_passed = False
    else:
        print(f"✅ YouTube 收集器测试通过!")
    
    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过! / All tests passed!")
        print("=" * 60)
        return 0
    else:
        print("⚠️  部分测试失败 / Some tests failed")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
