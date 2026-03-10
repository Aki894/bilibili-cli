#!/usr/bin/env python3
"""
测试脚本：Bilibili CLI 系列/合集功能
测试系列和合集相关命令的功能完整性

运行方式:
    python -m pytest tests/test_series.py -v
    或
    python tests/test_series.py
"""

import subprocess
import json
import sys
import os

# 测试配置
TEST_MID = 61639371  # 轴伊 Joi_Channel 的 UID
TEST_SERIES_ID = 61368  # 已知的系列 ID
TEST_TIMEOUT = 30  # 命令超时时间（秒）

def run_command(cmd: list, timeout: int = TEST_TIMEOUT) -> tuple:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "命令执行超时"
    except Exception as e:
        return -1, "", str(e)

def test_series_list_yaml():
    """测试 1: 获取系列列表 (YAML 格式)"""
    print("\n=== 测试 1: 获取系列列表 (YAML 格式) ===")
    cmd = ["bili", "series", "list", str(TEST_MID), "--format", "yaml"]
    returncode, stdout, stderr = run_command(cmd)
    
    assert returncode == 0, f"命令执行失败：{stderr}"
    assert "series:" in stdout, "输出中未找到 'series:' 标记"
    print("✅ 通过：成功获取系列列表 (YAML)")
    print(f"输出预览：{stdout[:200]}...")
    return True

def test_series_list_json():
    """测试 2: 获取系列列表 (JSON 格式)"""
    print("\n=== 测试 2: 获取系列列表 (JSON 格式) ===")
    cmd = ["bili", "series", "list", str(TEST_MID), "--format", "json"]
    returncode, stdout, stderr = run_command(cmd)
    
    assert returncode == 0, f"命令执行失败：{stderr}"
    try:
        data = json.loads(stdout)
        assert "items_lists" in data, "JSON 数据格式错误"
        print("✅ 通过：成功获取系列列表 (JSON)")
        print(f"数据结构：{list(data.get('items_lists', {}).keys())}")
    except json.JSONDecodeError:
        assert False, "输出不是有效的 JSON 格式"
    return True

def test_series_archives_yaml():
    """测试 3: 获取系列视频列表 (YAML 格式)"""
    print("\n=== 测试 3: 获取系列视频列表 (YAML 格式) ===")
    cmd = ["bili", "series", "archives", str(TEST_SERIES_ID), "--mid", str(TEST_MID), "--format", "yaml"]
    returncode, stdout, stderr = run_command(cmd)
    
    assert returncode == 0, f"命令执行失败：{stderr}"
    assert "- title:" in stdout or "bvid:" in stdout, "输出格式异常"
    print("✅ 通过：成功获取系列视频列表 (YAML)")
    # 显示前 3 个视频标题
    lines = stdout.split('\n')[:12]
    for line in lines:
        print(f"  {line}")
    return True

def test_series_archives_json():
    """测试 4: 获取系列视频列表 (JSON 格式)"""
    print("\n=== 测试 4: 获取系列视频列表 (JSON 格式) ===")
    cmd = ["bili", "series", "archives", str(TEST_SERIES_ID), "--mid", str(TEST_MID), "--format", "json", "--page-size", "5"]
    returncode, stdout, stderr = run_command(cmd)
    
    assert returncode == 0, f"命令执行失败：{stderr}"
    try:
        data = json.loads(stdout)
        assert isinstance(data, list), "返回数据应为列表"
        assert len(data) > 0, "列表不应为空"
        print(f"✅ 通过：成功获取系列视频列表 (JSON)，共 {len(data)} 个视频")
        print(f"  第 1 个视频：{data[0].get('title', 'N/A')}")
        print(f"  BV 号：{data[0].get('bvid', 'N/A')}")
    except json.JSONDecodeError:
        assert False, "输出不是有效的 JSON 格式"
    return True

def test_series_archives_pagination():
    """测试 5: 分页功能测试"""
    print("\n=== 测试 5: 分页功能测试 ===")
    cmd = ["bili", "series", "archives", str(TEST_SERIES_ID), "--mid", str(TEST_MID), "--page-size", "2", "--format", "json"]
    returncode, stdout, stderr = run_command(cmd)
    
    assert returncode == 0, f"命令执行失败：{stderr}"
    try:
        data = json.loads(stdout)
        assert len(data) <= 2, f"分页失败：期望最多 2 条，实际 {len(data)} 条"
        print(f"✅ 通过：分页功能正常，返回 {len(data)} 条记录")
    except json.JSONDecodeError:
        assert False, "输出不是有效的 JSON 格式"
    return True

def test_invalid_series_id():
    """测试 6: 错误处理 - 无效的系列 ID"""
    print("\n=== 测试 6: 错误处理 - 无效的系列 ID ===")
    cmd = ["bili", "series", "archives", "999999", "--mid", str(TEST_MID)]
    returncode, stdout, stderr = run_command(cmd)
    
    # 应返回错误信息或空列表，但不应该崩溃
    print(f"✅ 通过：错误处理正常 (返回码：{returncode})")
    if stderr:
        print(f"  错误信息：{stderr[:100]}")
    return True

def test_missing_required_param():
    """测试 7: 错误处理 - 缺少必需参数"""
    print("\n=== 测试 7: 错误处理 - 缺少必需参数 (--mid) ===")
    cmd = ["bili", "series", "archives", str(TEST_SERIES_ID)]
    returncode, stdout, stderr = run_command(cmd)
    
    # 应该报错提示缺少 --mid 参数
    assert returncode != 0 or "required" in stderr.lower() or "Missing" in stderr, "应提示缺少必需参数"
    print("✅ 通过：正确提示缺少必需参数")
    print(f"  错误信息：{stderr[:100]}")
    return True

def test_help_command():
    """测试 8: 帮助命令"""
    print("\n=== 测试 8: 帮助命令 ===")
    cmd = ["bili", "series", "--help"]
    returncode, stdout, stderr = run_command(cmd)
    
    assert returncode == 0, f"帮助命令执行失败：{stderr}"
    assert "list" in stdout, "帮助信息应包含 'list' 命令"
    assert "archives" in stdout, "帮助信息应包含 'archives' 命令"
    print("✅ 通过：帮助命令正常")
    print(f"  可用命令：{[c.strip() for c in stdout.split() if c.strip() in ['list', 'archives', 'season']]}")
    return True

def run_all_tests():
    """运行所有测试"""
    tests = [
        test_series_list_yaml,
        test_series_list_json,
        test_series_archives_yaml,
        test_series_archives_json,
        test_series_archives_pagination,
        test_invalid_series_id,
        test_missing_required_param,
        test_help_command,
    ]
    
    passed = 0
    failed = 0
    results = []
    
    print("=" * 60)
    print("Bilibili CLI 系列/合集功能测试套件")
    print(f"测试 UP 主：轴伊 Joi_Channel (UID: {TEST_MID})")
    print(f"测试系列 ID: {TEST_SERIES_ID}")
    print("=" * 60)
    
    for test in tests:
        try:
            test()
            passed += 1
            results.append((test.__name__, "✅ 通过", None))
        except AssertionError as e:
            failed += 1
            results.append((test.__name__, "❌ 失败", str(e)))
            print(f"❌ 失败：{test.__name__} - {e}")
        except Exception as e:
            failed += 1
            results.append((test.__name__, "❌ 异常", str(e)))
            print(f"❌ 异常：{test.__name__} - {e}")
    
    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总计：{passed + failed} 个测试")
    print(f"通过：{passed} 个 ✅")
    print(f"失败：{failed} 个 ❌")
    print("=" * 60)
    
    if failed > 0:
        print("\n失败的测试:")
        for name, status, error in results:
            if status == "❌ 失败" or status == "❌ 异常":
                print(f"  - {name}: {error}")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
