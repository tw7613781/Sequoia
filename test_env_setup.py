#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_sequoia_installation.py - 验证 Sequoia 环境安装

import os
import sys
import time

import numpy as np
import pandas as pd


def print_header(message):
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)


def check_imports():
    print_header("检查基本依赖包导入")

    packages = [
        ("pyyaml", "yaml"),  # PyYAML installed as pyyaml, imported as yaml
        "requests",
        "pandas",
        "numpy",
        "xlrd",
        ("ta-lib", "talib"),  # TA-Lib installed as ta-lib, imported as talib
        ("pytables", "tables"),  # pytables installed as pytables, imported as tables
        "schedule",
        "wxpusher",
        "pytest",
        "akshare",
    ]

    all_success = True

    for package in packages:
        if isinstance(package, tuple):
            install_name, import_name = package
        else:
            install_name = import_name = package

        try:
            module = __import__(import_name)
            version = getattr(module, "__version__", "未知版本")
            print(
                f"✅ 成功导入 {import_name} (安装为 {install_name}) - 版本: {version}"
            )
        except ImportError as e:
            print(f"❌ 导入 {import_name} 失败: {e}")
            all_success = False

    return all_success


def test_talib_functionality():
    print_header("测试 TA-Lib 功能")

    try:
        import numpy as np
        import talib

        # 创建一些示例数据
        data = np.array(
            [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 10.10], dtype=np.float64
        )

        # 测试 TA-Lib 函数
        sma = talib.SMA(data, timeperiod=3)
        print(f"SMA(3) 计算结果: {sma}")

        ema = talib.EMA(data, timeperiod=3)
        print(f"EMA(3) 计算结果: {ema}")

        rsi = talib.RSI(data, timeperiod=5)
        print(f"RSI(5) 计算结果: {rsi}")

        print("✅ TA-Lib 功能测试通过")
        return True
    except Exception as e:
        print(f"❌ TA-Lib 功能测试失败: {e}")
        return False


def test_akshare_connectivity():
    print_header("测试 AKShare 连接")

    try:
        import akshare as ak

        # 打印 akshare 版本
        print(f"AKShare 版本: {ak.__version__}")

        # 尝试使用几个稳定的接口
        print("\n测试获取股票列表...")
        stock_info = ak.stock_info_a_code_name()
        print(f"A股上市公司数量: {len(stock_info)}")
        print(f"数据示例: \n{stock_info.head(3)}")

        print("\n测试获取最新交易日沪深股市行情...")
        try:
            # 先尝试新API
            stock_zh_a_spot_df = ak.stock_zh_a_spot_em()
            print("使用 stock_zh_a_spot_em API 成功")
        except:
            # 如果失败，尝试备选API
            try:
                stock_zh_a_spot_df = ak.stock_zh_a_spot()
                print("使用 stock_zh_a_spot API 成功")
            except:
                print("获取实时行情失败，尝试其他API")
                # 继续尝试其他API
                stock_zh_a_hist_df = ak.stock_zh_a_hist(
                    symbol="000001",
                    period="daily",
                    start_date="20220101",
                    end_date="20220201",
                )
                print("使用 stock_zh_a_hist API 成功")
                stock_zh_a_spot_df = stock_zh_a_hist_df  # 用历史数据替代

        print(f"获取股票数据行数: {len(stock_zh_a_spot_df)}")
        print(f"数据列: {stock_zh_a_spot_df.columns.tolist()[:5]}...")

        print("\n✅ AKShare 连接测试通过")
        return True
    except Exception as e:
        print(f"❌ AKShare 连接测试失败: {str(e)}")
        print("这可能是由于网络连接问题或 AKShare 接口变更导致")

        # 提供更多调试信息
        import akshare as ak

        print("\n可用的 AKShare 函数:")
        api_list = [
            name
            for name in dir(ak)
            if not name.startswith("_") and name.startswith("stock_")
        ][:10]
        print(f"部分股票相关函数示例: {api_list}...")

        return False


def check_config_file():
    print_header("检查配置文件")

    config_path = os.path.join(os.getcwd(), "config.yaml")
    if os.path.exists(config_path):
        print(f"✅ 配置文件存在: {config_path}")
        return True
    else:
        print(f"❌ 配置文件不存在: {config_path}")
        print("请使用 'cp config.yaml.example config.yaml' 创建配置文件")
        return False


def test_environment():
    print_header("检查 Python 环境")

    print(f"Python 版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")

    # 检查是否在 conda 环境中
    conda_env = os.environ.get("CONDA_DEFAULT_ENV")
    if conda_env:
        print(f"✅ 当前 Conda 环境: {conda_env}")
    else:
        print("❌ 未检测到 Conda 环境")

    return True


def main():
    print("\n📊 Sequoia 选股系统安装验证")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Python 环境检查", test_environment),
        ("依赖包导入检查", check_imports),
        ("TA-Lib 功能测试", test_talib_functionality),
        ("AKShare 连接测试", test_akshare_connectivity),
        ("配置文件检查", check_config_file),
    ]

    results = []

    for name, test_func in tests:
        print(f"\n📋 执行测试: {name}")
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append((name, False))

    print_header("验证测试结果汇总")

    all_success = True
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {name}")
        if not success:
            all_success = False

    if all_success:
        print("\n🎉 恭喜! 所有测试都已通过，Sequoia 环境安装成功!")
        print("您可以通过运行 'python main.py' 来启动 Sequoia 选股系统")
    else:
        print("\n⚠️ 一些测试未通过，请解决上述问题后再尝试运行 Sequoia 选股系统")


if __name__ == "__main__":
    main()
