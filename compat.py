#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lua兼容模块
实现原触动精灵lua脚本中不兼容的函数
"""

import os
import sys
import time
import random
import pyautogui
from PyQt5.QtWidgets import QMessageBox
from log_utils import add_log

# 全局界面数据
界面数据 = {}

# lua退出函数
def lua_exit():
    """退出lua脚本"""
    add_log('脚本退出')
    sys.exit(0)

# 对话框函数
def dialog(msg, duration=3):
    """显示对话框"""
    add_log(f'[对话框] {msg}')
    # 显示PyQt5消息框
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        QMessageBox.information(None, '提示', msg)
    except Exception as e:
        add_log(f'显示对话框失败: {e}')
    
    # 等待指定时间
    time.sleep(duration)

# 显示窗口
def fwShowWnd(wid, x, y, width, height, flag):
    """显示窗口"""
    add_log(f'显示窗口: {wid}, 位置: ({x},{y}), 尺寸: ({width}x{height}), 标志: {flag}')

# 显示文本视图
def fwShowTextView(wid, textid, text, align, color, font, size, x, y, width, height, opacity):
    """显示文本视图"""
    add_log(f'显示文本视图: {wid}, 文本: {text}, 对齐: {align}, 颜色: {color}')

# 提示消息
def toast(msg, duration=3):
    """显示提示消息"""
    add_log(f'[提示] {msg}')
    # 可以使用pyautogui的alert功能
    try:
        pyautogui.alert(text=msg, title='提示', button='确定')
    except Exception as e:
        add_log(f'显示提示失败: {e}')

# 日志函数
def nLog(msg):
    """记录日志"""
    add_log(f'[日志] {msg}')

# 获取屏幕尺寸
def getScreenSize():
    """获取屏幕尺寸"""
    width, height = pyautogui.size()
    return width, height

# 获取随机数
def getRndNum():
    """获取随机数"""
    return random.randint(1, 1000000)

# 延时函数
def mSleep(times):
    """毫秒级延时"""
    time.sleep(times / 1000.0)

# 多色查找函数
def findMultiColorInRegionFuzzy(color, mask, similarity, x, y, width, height, orient=None):
    """在指定区域查找多色"""
    add_log(f'查找多色: {color}, 区域: ({x},{y},{width},{height}), 相似度: {similarity}')
    # 简化实现，实际需要使用OpenCV进行图像识别
    return None

# 兼容模块初始化
def init_compat():
    """初始化兼容模块"""
    # 将兼容函数添加到全局命名空间
    import builtins
    builtins.lua_exit = lua_exit
    builtins.dialog = dialog
    builtins.fwShowWnd = fwShowWnd
    builtins.fwShowTextView = fwShowTextView
    builtins.toast = toast
    builtins.nLog = nLog
    builtins.getScreenSize = getScreenSize
    builtins.getRndNum = getRndNum
    builtins.mSleep = mSleep
    builtins.findMultiColorInRegionFuzzy = findMultiColorInRegionFuzzy

# 自动初始化
init_compat()