#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理工具模块
提供统一的日志输出接口，确保所有日志都能正确显示在日志窗口
"""

# 只保留ui_module变量用于UI日志输出
ui_module = None

# 定义add_log函数

def add_log(message):
    """添加日志信息
    Args:
        message: 要添加的日志信息
    """
    global ui_module
    
    # 1. 总是输出到终端
    print(message)
    
    # 2. 尝试导入ui模块（如果尚未导入）
    if ui_module is None:
        try:
            import ui
            ui_module = ui
        except ImportError:
            # 静默失败，只在终端显示日志
            return
    
    # 3. 使用ui模块的_add_log_to_ui函数（如果可用）
    if hasattr(ui_module, '_add_log_to_ui'):
        try:
            ui_module._add_log_to_ui(message)
        except Exception:
            # 静默失败，只在终端显示日志
            pass
    
    return
