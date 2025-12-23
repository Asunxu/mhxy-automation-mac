#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查Python虚拟环境是否存在
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo "=== 启动梦幻西游自动化脚本 (Mac版) ==="
    echo "请确保梦幻西游游戏窗口已经打开并可见！"
    # 激活虚拟环境
    source "$SCRIPT_DIR/venv/bin/activate"
    # 设置QT平台插件路径
    export QT_QPA_PLATFORM_PLUGIN_PATH="$SCRIPT_DIR/venv/lib/python3.13/site-packages/PyQt5/Qt5/plugins/platforms"
    # 运行主程序
    python "$SCRIPT_DIR/main.py"
    deactivate
    
    echo "=== 脚本执行结束 ==="
    read -p "按回车键退出..."
else
    echo "错误：未找到Python虚拟环境！"
    echo "请确保您已正确解压项目文件，并且包含venv文件夹。"
    echo "按任意键退出..."
    read -n 1
fi