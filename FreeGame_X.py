#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FreeGame-X 引擎 - Python版
对应原FreeGame-X.lua功能，适配Mac平台
"""

import os
import sys
import time
import random
import numpy as np
import cv2
import pyautogui
from PIL import Image
import json

# 导入日志管理工具
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from log_utils import add_log

# 导入UI模块
try:
    import ui
except ImportError:
    # 如果导入失败，日志将只会输出到终端
    pass

# 常量定义
下 = 0
右 = 1
左 = 2
上 = 3
退出 = 1
跳过 = 2
找到退出 = 1
找不到退出 = 2

# 错误信息配置
ERROR_INIT_ORE_MSG = "初始化前,请配置方法 FreeGame:home()"
ERROR_INIT_PAGE_MSG = "初始化前,请配置方法 FreeGame:page(\"特征库文件\")"
ERROR_RUN_UNKNOWPAGE = "未知游戏界面"
ERROR_JOB_NIL = "任务列表不可以为空"

PAGE_GETPAGE_MSG = "当前游戏界面:"
PAGE_UNKNOWPAGE_MSG = "未知界面"

BTN_CLICK_MSG = "点击"
BTN_CLICK_MSG_PY = "偏移点击"
BTN_CLICK_MSG_RADDOM = "范围随机点击"
POINT_SLIDE_MSG = "滑动"
INPUT_MSG = "输入"
ACTON_SLEEP = "睡眠"

ACTION_SKIP_MSG = "跳过"
ACTION_EXCEPT_SKIP_MSG = "排除"
ACTION_UNCKEC_RETURN_MSG = "未检测到特征 退出:"

RUN_EXEC_DES = "延时执行【%s】秒 后执行任务"
RUN_CARD_OPEN = True
RUN_CARD_CLOSE = False

class Point:
    """点类，用于表示坐标"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"

class Rect:
    """矩形类，用于表示区域"""
    def __init__(self, x, y, x1, y1):
        self.x = x
        self.y = y
        self.x1 = x1
        self.y1 = y1
    
    def __repr__(self):
        return f"Rect({self.x}, {self.y}, {self.x1}, {self.y1})"

class Action:
    """动作类，用于构建自动化操作序列"""
    def __init__(self, *targets):
        self.targets = targets
        self.actions = []
        self.except_targets = []
        self.uncheck_targets = []
        self.before_func = None
        self.after_func = None
    
    def click(self, *offset):
        """点击操作
        参数：
        - 无参数：普通点击
        - offset_x, offset_y：固定偏移点击
        - 'random'：随机±5偏移点击
        - Point对象：精确点击
        """
        if offset:
            if len(offset) == 1:
                if isinstance(offset[0], Point):
                    self.actions.append(('click_py', offset[0]))
                elif offset[0] == 'random':
                    # 随机偏移点击标记
                    self.actions.append(('click', 'random'))
            else:
                self.actions.append(('click', offset))
        else:
            self.actions.append(('click', None))
        return self
    
    def sleep(self, times):
        """睡眠操作"""
        self.actions.append(('sleep', times))
        return self
    
    def slid(self, start_point, end_point):
        """滑动操作"""
        self.actions.append(('slide', (start_point, end_point)))
        return self
    
    def s(self, times):
        """简写的睡眠操作"""
        return self.sleep(times)
    
    def cs(self, count):
        """重试次数"""
        self.actions.append(('cs', count))
        return self
    
    def except_(self, *targets):
        """排除目标"""
        self.except_targets.extend(targets)
        return self
    
    def uncheck(self, *targets):
        """未检测到目标时执行"""
        self.uncheck_targets.extend(targets)
        return self
    
    def before(self, func):
        """执行前回调"""
        self.before_func = func
        return self
    
    def after(self, func):
        """执行后回调"""
        self.after_func = func
        return self

class FreeGame:
    """FreeGame引擎主类"""
    
    def __init__(self):
        self.ore_p = None
        self.page_p = None
        self.s_p = None
        self.card_p = None
        self.fontlib_index = None
        self.status = None
        self.unexe_p = None
        self.actionr_p = None
        self.actionr_time = time.time()
        self.current_page = None
        self.action_count = 0
        self.app = None  # Qt应用程序实例
        
        add_log("\n-------------------------")
        add_log("欢迎您使用FreeGame-X 引擎[Python版]")
        add_log("-------------------------")
    
    def home(self, ore):
        """设置屏幕朝向"""
        self.ore_p = ore
        return self
    
    def page(self, page):
        """设置页面特征库"""
        # 注释掉调试日志，只保留核心功能
        # add_log(f"设置页面特征库: {page}")
        # add_log(f"特征库类型: {type(page)}")
        # add_log(f"特征库是否为空: {len(page) == 0}")
        self.page_p = page
        return self
    
    def fontlib(self, fontlib):
        """设置字体库"""
        self.fontlib_index = fontlib
        return self
    
    def set_app(self, app):
        """设置Qt应用程序实例"""
        self.app = app
        return self
    
    def s(self, times):
        """睡眠"""
        time.sleep(times / 1000.0)
        return self
    
    def cs(self, count):
        """设置重试次数"""
        self.action_count = count
        return self
    
    def unexe(self, func):
        """设置未执行回调"""
        self.unexe_p = func
        return self
    
    def findmulticolor(self, c, check_paused=None, check_running=None):
        """多色查找 - 使用find_color.py中的findMultiColor函数"""
        try:
            # 状态检查函数，如果没有提供则使用默认实现
            def default_check_paused():
                return False
            
            def default_check_running():
                return True
            
            check_paused = check_paused or default_check_paused
            check_running = check_running or default_check_running
            
            # 处理Qt事件队列
            if self.app:
                self.app.processEvents()
            
            # 检查是否暂停
            while check_paused():
                add_log("脚本已暂停，等待继续指令...")
                time.sleep(0.5)
                # 处理Qt事件队列
                if self.app:
                    self.app.processEvents()
                # 检查是否需要停止
                if not check_running():
                    return None
            
            # 导入find_color.py中的findMultiColor函数
            from find_color import findMultiColor
            
            # 解析c参数
            if isinstance(c, str):
                # 处理字符串形式的特征点引用，如't.测试点'
                if c.startswith('t.'):
                    # 从特征库中获取特征点数据
                    feature_name = c[2:]
                    # 检查特征库是否加载（使用page_p属性）
                    #add_log(f"FreeGame实例的page_p属性: {getattr(self, 'page_p', '未找到page_p属性')}")
                    #add_log(f"FreeGame实例的page_p类型: {type(getattr(self, 'page_p', None))}")
                    if hasattr(self, 'page_p') and self.page_p:
                        # 获取特征库（使用page_p属性）
                        page_data = self.page_p
                        if feature_name in page_data:
                            add_log(f"找到特征点 {feature_name}")
                            feature_data = page_data[feature_name]
                            # 检查feature_data的类型和结构
                        else:
                            add_log(f"未找到特征点 {feature_name}")
                            return None
                        if isinstance(feature_data, dict):
                            # 字典格式：{"color": 0xa38162, "posandcolors": "...", "degree": 80, "x1": 285, "y1": 117, "x2": 331, "y2": 132}
                            color = feature_data.get("color", 0)
                            # 确保颜色值是整数类型
                            if isinstance(color, str):
                                try:
                                    # 尝试作为十六进制解析（无论是否有0x前缀）
                                    if color.startswith("0x"):
                                        color = int(color, 16)
                                    else:
                                        # 尝试作为十六进制解析，如果失败则作为十进制
                                        try:
                                            color = int(color, 16)
                                        except ValueError:
                                            color = int(color)
                                except ValueError:
                                    add_log(f"特征点 {feature_name} 颜色值格式错误: {color}")
                                    return None
                            posandcolors = feature_data.get("posandcolors", "")
                            degree = feature_data.get("degree", 80)
                            x1 = feature_data.get("x1", 0)
                            y1 = feature_data.get("y1", 0)
                            x2 = feature_data.get("x2", 0)
                            y2 = feature_data.get("y2", 0)
                        elif isinstance(feature_data, (list, tuple)) and len(feature_data) >= 7:
                            # 列表/元组格式：[color, posandcolors, degree, x1, y1, x2, y2]
                            try:
                                color, posandcolors, degree, x1, y1, x2, y2 = feature_data
                            except ValueError:
                                add_log(f"特征点 {feature_name} 数据解析错误")
                                return None
                        else:
                            add_log(f"特征点 {feature_name} 数据格式错误")
                            return None
                    else:
                        add_log("未加载特征库")
                        return None
                else:
                    add_log(f"无效的特征点引用格式: {c}")
                    return None
            else:
                # 直接使用传入的特征点数据
                if isinstance(c, dict):
                    color = c.get("color", 0)
                    # 确保颜色值是整数类型
                    if isinstance(color, str):
                        try:
                            # 尝试作为十六进制解析（无论是否有0x前缀）
                            if color.startswith("0x"):
                                color = int(color, 16)
                            else:
                                # 尝试作为十六进制解析，如果失败则作为十进制
                                try:
                                    color = int(color, 16)
                                except ValueError:
                                    color = int(color)
                        except ValueError:
                            add_log(f"特征点颜色值格式错误: {color}")
                            return None
                    posandcolors = c.get("posandcolors", "")
                    degree = c.get("degree", 80)
                    x1 = c.get("x1", 0)
                    y1 = c.get("y1", 0)
                    x2 = c.get("x2", 0)
                    y2 = c.get("y2", 0)
                elif isinstance(c, (list, tuple)) and len(c) >= 7:
                    color, posandcolors, degree, x1, y1, x2, y2 = c
                else:
                    add_log(f"无效的特征点数据格式: {c}")
                    return None
            
            # 直接使用与test_find_multi_color相同的找色流程
            from find_color import find_multi_color, capture_search_region_optimized
            
            # 截取搜索区域图像
            image, region, full_image = capture_search_region_optimized(x1, y1, x2, y2)
            if image is None:
                add_log(f"截取区域图像失败")
                return None
            
            # 调用核心找色函数
            x, y = find_multi_color(image, color, posandcolors, degree, x1, y1, x2, y2)
            
            if x != -1 and y != -1:
                # 获取找到点的RGB值
                try:
                    # 获取屏幕上该点的颜色
                    pixel_color = pyautogui.pixel(x, y)
                    # 转换为十六进制格式
                    rgb_hex = f"#{pixel_color[0]:02x}{pixel_color[1]:02x}{pixel_color[2]:02x}"
                    # 输出RGB信息和degree
                    add_log(f"特征点 {feature_name} 找到位置: ({x}, {y})")
                    # add_log(f"该点RGB: {pixel_color} (十六进制: {rgb_hex})")
                    # add_log(f"特征点degree: {degree}")
                except Exception as e:
                    add_log(f"获取RGB值失败: {e}")
                return Point(x, y)
            else:
                return None
        except Exception as e:
            add_log(f"findmulticolor error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def runAction(self, action, check_running=None, check_paused=None):
        """执行动作序列"""
        if not action or not action.targets:
            return False
        
        try:
            # 状态检查函数，如果没有提供则使用默认实现
            def default_check_running():
                return True
            
            def default_check_paused():
                return False
            
            check_running = check_running or default_check_running
            check_paused = check_paused or default_check_paused
            
            # 检查排除目标
            for except_target in action.except_targets:
                if not check_running():
                    return False
                
                # 处理Qt事件队列
                if self.app:
                    self.app.processEvents()
                
                # 检查是否暂停
                while check_paused():
                    add_log("脚本已暂停，等待继续指令...")
                    time.sleep(0.5)
                    # 处理Qt事件队列
                    if self.app:
                        self.app.processEvents()
                    if not check_running():
                        return False
                        
                if self.findmulticolor(except_target, check_paused, check_running):
                    msg = f"{ACTION_EXCEPT_SKIP_MSG}: {except_target}"
                    add_log(msg)
                    return False
            
            # 查找所有目标，必须全部找到才执行操作（与手机脚本保持一致）
            all_points = []
            found_all = True
            uncheck_target = None
            
            for target in action.targets:
                if not check_running():
                    return False
                
                # 处理Qt事件队列
                if self.app:
                    self.app.processEvents()
                
                # 检查是否暂停
                while check_paused():
                    add_log("脚本已暂停，等待继续指令...")
                    time.sleep(0.5)
                    # 处理Qt事件队列
                    if self.app:
                        self.app.processEvents()
                    if not check_running():
                        return False
                        
                points = self.findmulticolor(target, check_paused, check_running)
                if points:
                    all_points.append(points)
                else:
                    found_all = False
                    uncheck_target = target
                    break
            
            if found_all:
                # 所有目标都找到，执行动作序列
                # 使用第一个找到的点作为点击位置（与手机脚本保持一致）
                points = all_points[0]
                msg = f"{BTN_CLICK_MSG}: {action.targets[0]}"
                add_log(msg)
                
                # 执行before回调
                ext = None
                skipaction = False
                if action.before_func:
                    msg = f"执行before回调: {action.before_func.__name__}"
                    add_log(msg)
                    # 调用before回调，支持返回ext和skipaction
                    result = action.before_func(action, points)
                    if isinstance(result, tuple) and len(result) == 2:
                        ext, skipaction = result
                    else:
                        ext = result
                    
                    # 处理返回值
                    if isinstance(ext, bool) and ext:
                        return True
                    if isinstance(ext, int):
                        if ext == 退出:  # 退出(1)
                            return True
                        if ext == 跳过:  # 跳过(2)
                            skipaction = True
                
                # 如果skipaction为False，执行动作序列
                if not skipaction:
                    for act_type, act_params in action.actions:
                        if not check_running():
                            return False
                        
                        # 处理Qt事件队列
                        if self.app:
                            self.app.processEvents()
                        
                        # 检查是否暂停
                        while check_paused():
                            add_log("脚本已暂停，等待继续指令...")
                            time.sleep(0.5)
                            # 处理Qt事件队列
                            if self.app:
                                self.app.processEvents()
                            if not check_running():
                                return False
                        
                        if act_type == 'click':
                            if act_params:
                                if act_params == 'random':
                                    # 随机±5偏移点击
                                    offset_x = random.randint(-5, 5)
                                    offset_y = random.randint(-5, 5)
                                    click_point = Point(points.x + offset_x, points.y + offset_y)
                                    msg = f"{BTN_CLICK_MSG_RADDOM}: {click_point} (随机偏移: +{offset_x}, +{offset_y})"
                                    add_log(msg)
                                    # 使用更真实的点击模拟：移动到目标位置，按下鼠标，等待，松开鼠标
                                    pyautogui.moveTo(click_point.x, click_point.y, duration=0.1)  # 增加移动时间到0.3秒
                                    time.sleep(0.2)  # 增加移动后的等待时间
                                    pyautogui.mouseDown(button='left')
                                    time.sleep(0.2)  # 增加按下鼠标的时间
                                    pyautogui.mouseUp(button='left')
                                    time.sleep(0.3)  # 增加点击后的等待时间
                                else:
                                    # 固定偏移点击
                                    offset_x, offset_y = act_params
                                    click_point = Point(points.x + offset_x, points.y + offset_y)
                                    msg = f"{BTN_CLICK_MSG_PY}: {click_point}"
                                    add_log(msg)
                                    pyautogui.moveTo(click_point.x, click_point.y, duration=0.1)
                                    time.sleep(0.2)
                                    pyautogui.mouseDown(button='left')
                                    time.sleep(0.2)
                                    pyautogui.mouseUp(button='left')
                                    time.sleep(0.3)
                            else:
                                # 普通点击
                                msg = f"{BTN_CLICK_MSG_PY}: {points}"
                                add_log(msg)
                                pyautogui.moveTo(points.x, points.y, duration=0.1)
                                time.sleep(0.2)
                                pyautogui.mouseDown(button='left')
                                time.sleep(0.2)
                                pyautogui.mouseUp(button='left')
                                time.sleep(0.3)
                        elif act_type == 'click_py':
                            # 精确点击
                            msg = f"{BTN_CLICK_MSG_PY}: {act_params}"
                            add_log(msg)
                            pyautogui.moveTo(act_params.x, act_params.y, duration=0.1)
                            time.sleep(0.2)
                            pyautogui.mouseDown(button='left')
                            time.sleep(0.2)
                            pyautogui.mouseUp(button='left')
                            time.sleep(0.3)
                        elif act_type == 'sleep':
                            msg = f"{ACTON_SLEEP}: {act_params}ms"
                            add_log(msg)
                            # 分块睡眠，以便响应停止和暂停指令
                            total_sleep = act_params / 1000.0
                            sleep_chunk = 0.1  # 每100毫秒检查一次指令
                            while total_sleep > 0 and check_running():
                                # 处理Qt事件队列
                                if self.app:
                                    self.app.processEvents()
                            
                                # 检查是否暂停
                                while check_paused():
                                    add_log("脚本已暂停，等待继续指令...")
                                    time.sleep(0.5)
                                    # 处理Qt事件队列
                                    if self.app:
                                        self.app.processEvents()
                                    if not check_running():
                                        return False
                            
                                sleep_time = min(sleep_chunk, total_sleep)
                                time.sleep(sleep_time)
                                total_sleep -= sleep_time
                            
                            if not check_running():
                                return False
                        elif act_type == 'slide':
                            start_point, end_point = act_params
                            # 检查点是否有效
                            if hasattr(start_point, 'x') and hasattr(start_point, 'y') and hasattr(end_point, 'x') and hasattr(end_point, 'y'):
                                msg = f"{POINT_SLIDE_MSG}: {start_point} -> {end_point}"
                                add_log(msg)
                                pyautogui.moveTo(start_point.x, start_point.y)
                                pyautogui.dragTo(end_point.x, end_point.y, duration=0.5)
                            else:
                                msg = "滑动点参数无效，跳过滑动操作"
                                add_log(msg)
                        elif act_type == 'cs':
                            # 重试次数，这里简化处理
                            pass
                
                # 处理Qt事件队列
                if self.app:
                    self.app.processEvents()
                
                # 检查是否暂停
                while check_paused():
                    add_log("脚本已暂停，等待继续指令...")
                    time.sleep(0.5)
                    # 处理Qt事件队列
                    if self.app:
                        self.app.processEvents()
                    if not check_running():
                        return False
                
                # 执行after回调
                if action.after_func:
                    msg = f"执行after回调: {action.after_func.__name__}"
                    add_log(msg)
                    return action.after_func(action, all_points)
                
                return True
            
            # 未找到所有目标，执行uncheck操作
            ext = None
            if action.uncheck_targets:
                for uncheck_target in action.uncheck_targets:
                    if hasattr(uncheck_target, '__call__'):
                        msg = f"执行uncheck回调: {uncheck_target.__name__}"
                        add_log(msg)
                        # 调用uncheck回调，支持返回值
                        ext = uncheck_target(action, uncheck_target)
                        
                        # 处理返回值
                        if isinstance(ext, bool) and ext:
                            msg = f"{ACTION_UNCKEC_RETURN_MSG} {action.targets}"
                            add_log(msg)
                            return True
                        if isinstance(ext, int) and ext == 退出:  # 退出(1)
                            msg = f"{ACTION_UNCKEC_RETURN_MSG} {action.targets}"
                            add_log(msg)
                            return True
            
            msg = f"{ACTION_UNCKEC_RETURN_MSG} {action.targets}"
            add_log(msg)
            return False
            
        except Exception as e:
            msg = f"runAction error: {e}"
            add_log(msg)
            return False
    
    def run(self, job_dict, check_paused=None, check_running=None):
        """执行任务列表"""
        if not job_dict:
            msg = ERROR_JOB_NIL
            add_log(msg)
            return False
        
        # 状态检查函数，如果没有提供则使用默认实现
        def default_check_paused():
            return False
        
        def default_check_running():
            return True
            
        check_paused = check_paused or default_check_paused
        check_running = check_running or default_check_running
        
        all_success = True
        for action_name, action in job_dict.items():
            # 检查是否停止
            if not check_running():
                msg = "收到停止指令，退出任务执行"
                add_log(msg)
                return False
            
            # 处理Qt事件队列
            if self.app:
                self.app.processEvents()
            
            # 检查是否暂停
            while check_paused():
                add_log("脚本已暂停，等待继续指令...")
                time.sleep(0.5)
                # 处理Qt事件队列
                if self.app:
                    self.app.processEvents()
                if not check_running():
                    msg = "收到停止指令，退出任务执行"
                    add_log(msg)
                    return False
            
            msg = f"执行任务: {action_name}"
            add_log(msg)
            if not self.runAction(action, check_running, check_paused):
                msg = f"任务执行失败: {action_name}"
                add_log(msg)
                # 容错处理：不终止整个任务列表，继续执行后续任务
                all_success = False
        
        return all_success

# 兼容函数
def messagebox(msg):
    """消息框"""
    add_log(f"[提示] {msg}")

def sleep(times):
    """睡眠"""
    time.sleep(times / 1000.0)

def gettickcount():
    """获取当前时间戳"""
    return int(time.time() * 1000)

def lineprint(msg):
    """行打印"""
    add_log(msg)

# 全局实例
# 创建全局FreeGame实例，保持与Lua版本兼容性
FreeGame = FreeGame()