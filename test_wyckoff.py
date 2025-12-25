# -*- encoding: UTF-8 -*-
"""
威克夫策略测试脚本

使用方法：
1. 确保已安装所有依赖
2. 运行: python test_wyckoff.py
"""

import logging

import akshare as ak

from strategy import (
    wyckoff_accumulation,
    wyckoff_divergence,
    wyckoff_selling_climax,
    wyckoff_spring,
)

# 配置日志
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)


def test_wyckoff_strategies():
    """测试威克夫策略"""
    
    print("\n" + "=" * 70)
    print("威克夫策略测试")
    print("=" * 70)
    
    # 获取测试股票数据（这里用几只常见股票做测试）
    test_stocks = [
        ("000001", "平安银行"),
        ("600519", "贵州茅台"),
        ("000858", "五粮液"),
    ]
    
    strategies = {
        "弹簧策略": wyckoff_spring.check,
        "量价背离": wyckoff_divergence.check,
        "SC反弹": wyckoff_selling_climax.check,
        "吸筹完成": wyckoff_accumulation.check,
    }
    
    for code, name in test_stocks:
        print(f"\n{'=' * 70}")
        print(f"测试股票: {name} ({code})")
        print(f"{'=' * 70}")
        
        try:
            # 获取股票数据
            data = ak.stock_zh_a_hist(
                symbol=code, period="daily", start_date="20220101", adjust="qfq"
            )
            
            if data is None or data.empty:
                print(f"❌ 无法获取{name}的数据")
                continue
            
            # 计算涨跌幅
            import talib as tl
            data["p_change"] = tl.ROC(data["收盘"], 1)
            
            # 测试每个策略
            for strategy_name, strategy_func in strategies.items():
                try:
                    result = strategy_func((code, name), data)
                    status = "✅ 符合" if result else "❌ 不符合"
                    print(f"{strategy_name:12} {status}")
                except Exception as e:
                    print(f"{strategy_name:12} ⚠️  测试出错: {str(e)}")
                    
        except Exception as e:
            print(f"❌ 获取{name}数据时出错: {str(e)}")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)
    print("\n提示: 如果想测试更多股票，请修改 test_stocks 列表")
    print("提示: 详细策略说明请查看 README_WYCKOFF.md\n")


if __name__ == "__main__":
    test_wyckoff_strategies()


