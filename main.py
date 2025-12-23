#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序入口 - 对应原main.lua功能
"""

import os
import sys
import time
import json
import importlib
import subprocess

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 使用统一的日志管理工具
try:
    from log_utils import add_log
except ImportError:
    print("无法导入log_utils模块，将使用print代替add_log")
    def add_log(message):
        print(message)

# 尝试自动设置QT平台插件路径
try:
    # 获取pip安装位置
    pip_path = subprocess.check_output(['pip3', 'show', 'PyQt5']).decode('utf-8')
    for line in pip_path.split('\n'):
        if line.startswith('Location:'):
            qt_path = os.path.join(line.split(': ')[1], 'PyQt5', 'Qt5', 'plugins')
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(qt_path, 'platforms')
            print(f"设置QT平台插件路径: {os.environ['QT_QPA_PLATFORM_PLUGIN_PATH']}")
            break
except:
    print("无法自动设置QT平台插件路径")

# 导入PyQt5应用程序类和必要的组件
try:
    from PyQt5.QtWidgets import QApplication, QWidget, QShortcut
    from PyQt5.QtCore import QTimer, Qt, QEvent, QObject
    from PyQt5.QtGui import QKeySequence
except ImportError:
    QApplication = None
    QTimer = None
    QWidget = None
    QShortcut = None
    Qt = None
    QEvent = None
    QObject = None
    QKeySequence = None

# 导入兼容模块
from compat import *

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入模块
from ui import show_ui, show_log_window, ConfigWindow
from FreeGame_X import FreeGame, Point, Action, sleep, messagebox, 右, 下, 左, 上, 退出, 跳过, 找到退出, 找不到退出
# 使用统一的日志管理工具
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QObject, pyqtSignal

# 全局变量
界面数据 = {}

# 特征库缓存，用于存储加载后的page.txt特征库
page_cache = None
# 脚本控制变量
is_script_running = False  # 脚本是否正在运行
is_script_paused = False   # 脚本是否暂停

# 流控函数
class FlowControl:
    """流控函数类"""
    
    def __init__(self):
        self.抓鬼轮数 = 0
        self.采集次数 = 0
        self.当前时间 = 0
    
    def 判断次数0(self):
        """判断抓鬼轮数"""
        self.抓鬼轮数 += 1
        add_log(f"当前抓鬼轮数: {self.抓鬼轮数}")
        if self.抓鬼轮数 > int(界面数据.get('zgls', '15')):
            messagebox('抓鬼任务已完成！')
            return True
        return False
    
    def 判断次数1(self):
        """判断采集次数"""
        self.采集次数 += 1
        add_log(f"当前采集次数: {self.采集次数}")
        if self.采集次数 > int(界面数据.get('cjcs', '15')):
            messagebox('采集任务已完成！')
            return True
        return False
    
    def 滑动任务(self):
        """滑动任务"""
        return False
    
    def 检查滑动任务(self, ttime):
        """检查滑动任务"""
        return False
    
    def 测试程序(self, action, points):
        """测试程序"""
        add_log(f"测试程序执行: {action}, {points}")
        return True
    
    def 找不到飞东海(self):
        """找不到飞东海"""
        return False
    
    def 找不到飞长寿(self):
        """找不到飞长寿"""
        return False
    
    def 找不到飞花果(self):
        """找不到飞花果"""
        return False
    
    def 找不到飞大雪(self):
        """找不到飞大雪"""
        return False
    
    def 找不到飞两界(self):
        """找不到飞两界"""
        return False
    
    def 找花草2(self):
        """找花草2"""
        return False
    
    def 找矿石2(self):
        """找矿石2"""
        return False
    
    def 任务没有执行(self, ttime):
        """任务没有执行"""
        return False
    
    def 师门停止检测(self, smtime):
        """师门停止检测"""
        return False

def load_page_lua():
    """加载page.txt特征库
    
    实现了缓存机制：程序启动时读取一次page.txt文件并缓存，后续调用直接返回缓存的特征库
    """
    import os
    import re
    import ast
    
    # 使用全局缓存变量
    global page_cache
    
    # 如果缓存存在，直接返回缓存的特征库
    if page_cache is not None:
        add_log("使用缓存的特征库")
        return page_cache
    
    # 创建一个字典来存储特征库，键是特征名，值是特征数据数组
    t = {}
    # 从page.txt文件读取特征点数据
    page_lua_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'page.txt')
    
    # 检查page.lua文件是否存在
    if not os.path.exists(page_lua_path):
        add_log(f"page.txt文件不存在: {page_lua_path}")
        # 返回一个空字典，让程序能够继续执行
        return t
    
    try:
        add_log('加载page.txt特征库...')
        
        # 读取page.lua文件内容
        with open(page_lua_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # add_log(f"page.txt原始内容: {content}")
        
        # 移除所有换行符和制表符，使内容变成一行，更容易处理
        content = content.replace('\n', '').replace('\t', '').replace(' ', '')
        
        # add_log(f"处理后的内容: {content}")
        
        # 找到t表的开始位置
        t_start = content.find('t={')
        if t_start == -1:
            add_log("未找到t表定义")
            return t
        
        # 找到t表的结束位置
        # 这里需要考虑嵌套的大括号，所以需要计算大括号的数量
        t_end = -1
        brace_count = 0
        for i in range(t_start + 3, len(content)):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                if brace_count == 0:
                    t_end = i
                    break
                brace_count -= 1
        
        if t_end == -1:
            add_log("未找到t表的结束位置")
            return t
        
        # 提取t表的内容
        t_content = content[t_start + 3:t_end]
        # add_log(f"t表内容: {t_content}")
        
        # 初始化特征点列表
        features = []
        
        # 查找所有特征点定义
        # 特征点定义格式：特征点名称={数据};
        current_pos = 0
        while current_pos < len(t_content):
            # 找到等号的位置
            eq_pos = t_content.find('=', current_pos)
            if eq_pos == -1:
                break
            
            # 提取特征点名称
            feature_name = t_content[current_pos:eq_pos]
            
            # 找到大括号的开始位置
            brace_start = t_content.find('{', eq_pos)
            if brace_start == -1:
                break
            
            # 找到大括号的结束位置
            brace_end = -1
            brace_count = 0
            for i in range(brace_start + 1, len(t_content)):
                if t_content[i] == '{':
                    brace_count += 1
                elif t_content[i] == '}':
                    if brace_count == 0:
                        brace_end = i
                        break
                    brace_count -= 1
            
            if brace_end == -1:
                break
            
            # 提取特征点数据
            feature_data = t_content[brace_start + 1:brace_end]
            
            # 检查是否有分号，如果有，跳过
            semicolon_pos = t_content.find(';', brace_end)
            if semicolon_pos != -1:
                current_pos = semicolon_pos + 1
            else:
                current_pos = brace_end + 1
            
            # 添加到特征点列表
            features.append((feature_name, feature_data))
            # add_log(f"找到特征点: {feature_name}, 数据: {feature_data[:100]}...")
        
        # 处理每个特征点
        for feature_name, feature_data_str in features:
            key = feature_name.strip()
            value_str = feature_data_str.strip()
        
            #add_log(f"解析特征点: {key}")
            #add_log(f"特征点数据: {value_str}")
            
            # 解析值字符串
            # 先将值字符串按逗号分割成数组
            value_parts = []
            current_part = ''
            in_string = False
            
            for char in value_str:
                if char == '"':
                    in_string = not in_string
                    current_part += char
                elif char == ',' and not in_string:
                    value_parts.append(current_part.strip())
                    current_part = ''
                else:
                    current_part += char
            
            # 添加最后一个部分
            if current_part.strip():
                value_parts.append(current_part.strip())
            
            #add_log(f"分割后的值数组: {value_parts}")
            
            # 转换每个值为适当的类型
            values = []
            for part in value_parts:
                if part.startswith('"') and part.endswith('"'):
                    # 字符串类型，移除引号
                    values.append(part[1:-1])
                elif part.startswith('0x'):
                    # 十六进制数值
                    try:
                        values.append(int(part, 16))
                    except ValueError:
                        add_log(f"无效的十六进制值: {part}")
                        values.append(part)
                else:
                    # 尝试转换为整数
                    try:
                        values.append(int(part))
                    except ValueError:
                        # 保留原始字符串
                        values.append(part)
            
            # 将特征点添加到字典中，以数组形式存储
            t[key] = values
        
        # 只保留简洁的成功日志
        add_log(f"加载page.txt特征库成功，共加载 {len(t)} 个特征点")
        # 将加载的特征库缓存起来
        page_cache = t
        return t
    except Exception as e:
        add_log(f"加载page.txt特征库时发生错误: {e}")
        import traceback
        add_log(f"错误详情: {traceback.format_exc()}")
        # 返回一个空字典，让程序能够继续执行
        t = {}
        # 缓存空字典，避免重复加载失败
        page_cache = t
    
    return t

def test_find_multi_color(feature_name):
    """测试使用find_multi_color函数识别特征库中的点
    
    参数：
        feature_name: 特征点名称，如't.测试点'
    
    返回：
        (x, y): 找到的点坐标，未找到返回(-1, -1)
    """
    from find_color import find_multi_color, capture_search_region_optimized
    
    # 直接使用FreeGame实例中已经加载好的特征库
    page = FreeGame.page_p
    
    # 检查特征库是否为空
    if not page:
        add_log("特征库为空，无法进行识别")
        return -1, -1
    
    # 提取特征点名称（去掉't.'前缀）
    if feature_name.startswith('t.'):
        actual_name = feature_name[2:]
    else:
        actual_name = feature_name
    
    # 获取特征点数据
    feature_data = page.get(actual_name)
    if not feature_data:
        add_log(f"未找到特征点: {feature_name}")
        return -1, -1
    
    # 解析特征点数据
    try:
        if isinstance(feature_data, list) and len(feature_data) >= 7:
            # 列表格式：[color, posandcolors, degree, x1, y1, x2, y2]
            color, posandcolors, degree, x1, y1, x2, y2 = feature_data
        else:
            add_log(f"特征点 {feature_name} 数据格式不正确")
            return -1, -1
    except ValueError as e:
        add_log(f"特征点 {feature_name} 数据解析错误: {e}")
        return -1, -1
    
    # 检查参数有效性
    if not all([isinstance(color, int), isinstance(posandcolors, str), 
                isinstance(degree, int), isinstance(x1, int), 
                isinstance(y1, int), isinstance(x2, int), isinstance(y2, int)]):
        add_log(f"特征点 {feature_name} 参数类型错误")
        return -1, -1
    
    # 截取搜索区域图像
    image, region, full_image = capture_search_region_optimized(x1, y1, x2, y2)
    if image is None:
        add_log(f"截取区域图像失败")
        return -1, -1
    
    # 调用find_multi_color函数进行识别
    result = find_multi_color(image, color, posandcolors, degree, x1, y1, x2, y2)
    
    if result != (-1, -1):
        add_log(f"成功识别特征点 {feature_name}，坐标：{result}")
    else:
        add_log(f"未识别到特征点 {feature_name}")
    
    return result

def main():
    """主程序入口"""
    global 界面数据
    
    # 1. 显示UI界面
    add_log('显示UI界面...')
    
    # 创建ConfigWindow实例并显示
    window = ConfigWindow()
    window.show()
    window.activateWindow()
    
    def continue_main_with_config(config_data):
        """使用配置数据继续执行主程序"""
        global 界面数据
        界面数据 = config_data
        
        if 界面数据:
            add_log(f"界面数据收集完成: {界面数据}")
            
            # 获取或创建Qt应用实例
            app = QApplication.instance()
            if not app:
                app = QApplication(sys.argv)
            
            # 2. 初始化
            add_log('初始化FreeGame引擎...')
            # 加载特征库
            page = load_page_lua()
            # 设置特征库到FreeGame实例
            FreeGame.home(右).page(page).fontlib(None).s(1000)
            # 设置Qt应用实例
            FreeGame.set_app(app)
            
            # 注释掉测试代码，避免不必要的日志输出
            # 示例：使用test_find_multi_color函数测试识别特征点
            # add_log("\n=== 测试特征点识别 ===")
            # 测试直接调用find_multi_color函数
            # result = test_find_multi_color('t.测试点')
            # add_log(f"test_find_multi_color函数返回结果: {result}")
            
            # 测试使用FreeGame实例的findmulticolor方法
            # add_log("\n=== 测试FreeGame实例的findmulticolor方法 ===")
            # 检查FreeGame实例的page_p属性
            # add_log(f"FreeGame实例的page_p属性: {getattr(FreeGame, 'page_p', '未找到page_p属性')}")
            # add_log(f"FreeGame实例的page_p类型: {type(getattr(FreeGame, 'page_p', None))}")
            # if hasattr(FreeGame, 'page_p'):
            #     add_log(f"FreeGame实例的page_p长度: {len(FreeGame.page_p)}")
            #     add_log(f"FreeGame实例的page_p内容: {FreeGame.page_p}")
            
            # 3. 显示日志窗口
            add_log('显示日志窗口...')
            
            # 获取选择的任务
            job = 界面数据.get('job', '0')
            add_log(f"选择的任务索引: {job}")
            
            # 定义状态检查函数
            def check_paused():
                global is_script_paused
                return is_script_paused
            
            def check_running():
                global is_script_running
                return is_script_running
            
            def execute_task():
                """执行任务函数"""
                global is_script_running, is_script_paused
                task_round = 0  # 任务执行轮数计数器
                
                try:
                    # 循环执行任务
                    while is_script_running:
                        # 检查是否暂停
                        while is_script_paused:
                            add_log("脚本已暂停，按继续键恢复...")
                            time.sleep(0.5)
                            # 处理Qt事件队列
                            if app:
                                app.processEvents()
                        
                        # 处理Qt事件队列
                        if app:
                            app.processEvents()
                        
                        if job == '0':  # 抓鬼
                            if not is_script_running: break
                            FreeGame.run(抓鬼, check_paused, check_running)
                        elif job == '1':  # 师门
                            if not is_script_running: break
                            FreeGame.run(师门, check_paused, check_running)
                        elif job == '2':  # 采集花草
                            if not is_script_running: break
                            FreeGame.run(采集_花草, check_paused, check_running)
                        elif job == '3':  # 挖掘矿石
                            if not is_script_running: break
                            FreeGame.run(挖掘矿石, check_paused, check_running)
                        elif job == '4':  # 测试
                            if not is_script_running: break
                            FreeGame.run(测试, check_paused, check_running)
                        elif job == '5':  # 截图
                            if not is_script_running: break
                            # 截图功能实现
                            pass
                        
                        if not is_script_running: break
                        
                        # 处理Qt事件队列
                        if app:
                            app.processEvents()
                        
                        # 添加短暂延迟，避免过于频繁地执行任务
                        time.sleep(1)
                        task_round += 1
                        add_log(f"\n开始第 {task_round} 轮任务执行...")
                except Exception as e:
                    add_log(f"执行任务时发生错误: {e}")
                finally:
                    is_script_running = False
                    is_script_paused = False
            
            # 定义暂停和停止的回调函数
            def pause_callback(is_paused):
                """暂停/继续回调函数"""
                global is_script_paused
                is_script_paused = is_paused
                add_log(f"脚本{'暂停' if is_paused else '继续'}执行")
            
            def stop_callback():
                """停止回调函数"""
                global is_script_running, is_script_paused
                is_script_running = False
                is_script_paused = False
                add_log("脚本已停止")
            
            def start_callback():
                """启动回调函数"""
                global is_script_running, is_script_paused
                if not is_script_running:
                    is_script_running = True
                    is_script_paused = False
                    add_log(f"开始执行任务，任务索引: {job}")
                    # 创建一个新线程来执行任务
                    import threading
                    thread = threading.Thread(target=execute_task)
                    thread.daemon = True
                    thread.start()
            
            # 显示日志窗口并传递回调函数
            show_log_window(start_callback, pause_callback, stop_callback)
            
            # 5. 初始化PyQt5应用程序用于键盘事件监听
            app = QApplication.instance()
            if not app:
                app = QApplication(sys.argv)
            # 将Qt应用程序实例传递给FreeGame引擎
            FreeGame.set_app(app)
            
            # 快捷键功能已在LogWindow类中实现，此处不再重复创建
            
            # 4. 加载特征库
            t = load_page_lua()
            
            # 5. 初始化流控函数
            flow_control = FlowControl()
            
            # 6. 加载任务配置
            # 抓鬼任务
            抓鬼 = {
                '活动关闭1': Action('t.活动关闭1').click().sleep(1500),
                '测试点': Action('t.测试点').click().sleep(1500),
                '活动关闭2': Action('t.活动关闭2').click().sleep(1500),
                '活动关闭3': Action('t.活动关闭3').click().sleep(1500),
                '活动关闭4': Action('t.活动关闭4').click().sleep(1500),
                '师门关闭': Action('t.师门关闭').click().sleep(1500),
                '关闭使用': Action('t.关闭使用').click().sleep(1500),
                '关闭聊天': Action('t.关闭聊天').click().sleep(1500),
                '队伍图标': Action('t.队伍图标1', 't.任务图标0').click().sleep(1500),
                '抓鬼任务1': Action('t.抓鬼任务').sleep(1000).click().cs(2).sleep(3000),
                '抓鬼任务2': Action('t.抓鬼任务').sleep(1000).click().s(1).cs(2).sleep(3000),
                '点击捉鬼': Action('t.点击捉鬼').click(80, 30).sleep(1500).click(50, 20).s(2).cs(1).sleep(900).uncheck(flow_control.滑动任务),
                '继续抓鬼': Action('t.继续抓鬼', 't.确定继续').before(flow_control.判断次数0).sleep(1000).click().sleep(8000)
            }
            
            # 师门任务
            师门 = {
                '活动关闭1': Action('t.活动关闭1').click().sleep(1500),
                '活动关闭2': Action('t.活动关闭2').click().sleep(1500),
                '活动关闭3': Action('t.活动关闭3').click().sleep(1500),
                '活动关闭4': Action('t.活动关闭4').click().sleep(1500),
                '师门关闭': Action('t.师门关闭').click().sleep(1500),
                '关闭使用': Action('t.关闭使用').click().sleep(1500),
                '关闭聊天': Action('t.关闭聊天').click().sleep(1500)
            }
            
            # 测试任务
            测试 = {
                '测试点': Action('t.测试点').click('random').sleep(1500)
            }
            
            # 采集_花草任务
            采集_花草 = {
                '风物志关闭': Action('t.风物志关闭').click().sleep(1500),
                '任务列表': Action('t.任务列表').click().sleep(1500),
                '活动关闭1': Action('t.活动关闭1').click().sleep(1500),
                '活动关闭2': Action('t.活动关闭2').click().sleep(1500),
                '活动关闭3': Action('t.活动关闭3').click().sleep(1500),
                '活动关闭4': Action('t.活动关闭4').click().sleep(1500),
                '师门关闭': Action('t.师门关闭').click().sleep(1500),
                '关闭使用': Action('t.关闭使用').click().sleep(1500),
                '关闭聊天': Action('t.关闭聊天').click().sleep(1500),
                '采集花草': Action('t.采集花草').click(15, -40).s(1).cs(2).sleep(3000).uncheck(flow_control.找花草2),
                '列表花草1': Action('t.列表花草1').click().cs(2).sleep(1500),
                '列表花草2': Action('t.列表花草2').click().cs(2).sleep(1500),
                '采集按钮1': Action('t.采集按钮').before(flow_control.判断次数1).click().cs(1).sleep(12000),
                '采集按钮2': Action('t.采集按钮').before(flow_control.判断次数1).click().s(2).cs(1).sleep(12000)
            }
            
            # 挖掘_矿石任务
            挖掘矿石 = {
                '风物志关闭': Action('t.风物志关闭').click().sleep(1500),
                '任务列表': Action('t.任务列表').click().sleep(1500),
                '活动关闭1': Action('t.活动关闭1').click().sleep(1500),
                '活动关闭2': Action('t.活动关闭2').click().sleep(1500),
                '活动关闭3': Action('t.活动关闭3').click().sleep(1500),
                '活动关闭4': Action('t.活动关闭4').click().sleep(1500),
                '师门关闭': Action('t.师门关闭').click().sleep(1500),
                '关闭使用': Action('t.关闭使用').click().sleep(1500),
                '关闭聊天': Action('t.关闭聊天').click().sleep(1500),
                '采集矿石': Action('t.采集矿石').click(15, -40).s(1).cs(2).sleep(3000).uncheck(flow_control.找矿石2),
                '列表矿石1': Action('t.列表矿石1').click().cs(2).sleep(1500),
                '列表矿石2': Action('t.列表矿石2').click().cs(2).sleep(1500),
                '采集按钮1': Action('t.采集按钮').before(flow_control.判断次数1).click().cs(1).sleep(12000),
                '采集按钮2': Action('t.采集按钮').before(flow_control.判断次数1).click().s(2).cs(1).sleep(12000)
            }
            
            # 获取选择的任务
            job = 界面数据.get('job', '0')
            
            # 导入线程模块
            import threading
            
            # 自动启动任务
            add_log(f"选择的任务索引: {job}")
            start_callback()
        else:
            add_log("未收集到界面数据，退出程序")
            # 任务完成
            messagebox('再见！')
            add_log('脚本结束！')
    
    # 使用定时器定期检查窗口是否已关闭
    def check_window_closed():
        if not window.isVisible():
            timer.stop()
            continue_main_with_config(window.界面数据)
    
    # 创建定时器
    timer = QTimer()
    timer.timeout.connect(check_window_closed)
    timer.start(100)  # 每100毫秒检查一次

if __name__ == '__main__':
    try:
        add_log("开始初始化程序...")
        
        # 设置QT平台插件路径
        app_path = os.path.dirname(os.path.abspath(__file__))
        plugin_path = os.path.join(app_path, "venv", "lib", "python3.13", "site-packages", "PyQt5", "Qt5", "plugins")
        #print(f"设置QT平台插件路径: {plugin_path}")
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
        
        # 创建PyQt5应用程序实例（如果导入成功）
        app = None
        if QApplication and QTimer:
            #print("创建QApplication实例...")
            app = QApplication(sys.argv)
            
            # 设置应用程序退出策略，确保即使所有窗口都关闭，程序仍然保持运行状态
            app.setQuitOnLastWindowClosed(False)
            
            # 使用QTimer在事件循环启动后执行主程序
            timer = QTimer()
            timer.timeout.connect(lambda: (timer.stop(), main()))
            timer.start(100)
            
            # 启动事件循环，这会一直运行直到应用程序退出
            #print("进入应用程序主循环...")
            app.exec_()
        else:
            # 如果没有PyQt5，直接运行主程序
            print("未找到PyQt5，直接运行主程序...")
            main()
    except Exception as e:
        print(f"程序执行出错: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")