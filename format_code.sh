#!/bin/bash
# 格式化所有 Python 文件

# 安装所需工具（如果尚未安装）
pip install black isort

# 使用 isort 整理导入
echo "整理导入顺序..."
isort .

# 使用 Black 格式化代码
echo "格式化代码..."
black .

echo "完成!"