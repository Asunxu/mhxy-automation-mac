#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户界面模块 - 对应触动精灵的ui.lua功能
使用PyQt5实现图形界面
"""

import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QLineEdit, 
                             QRadioButton, QButtonGroup, QPushButton, 
                             QGroupBox, QTabWidget, QMessageBox, QTextEdit, 
                             QScrollArea)
from PyQt5.QtCore import Qt, QRect, QThread, QTimer, QMetaObject, pyqtSlot
from PyQt5.QtGui import QFont, QGuiApplication, QTextCursor
from log_utils import add_log

class ConfigWindow(QMainWindow):
    """配置窗口类"""
    
    def __init__(self):
        super().__init__()
        self.界面数据 = {}
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('梦幻西游自动化脚本 - Mac版')
        self.setFixedSize(600, 500)
        
        # 中央窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        

        
        # 任务选择组
        task_group = QGroupBox('请选择要做的任务')
        task_layout = QVBoxLayout()
        
        # 任务选择标签
        task_label = QLabel('任务类型:')
        task_label.setFont(QFont('Arial', 12))
        task_layout.addWidget(task_label)
        
        # 任务选择下拉框
        self.job_combo = QComboBox()
        self.job_combo.addItems(['抓鬼', '师门', '采集花草', '挖掘矿石', '测试', '截图'])
        self.job_combo.setFont(QFont('Arial', 10))
        self.job_combo.currentTextChanged.connect(self.on_task_changed)
        task_layout.addWidget(self.job_combo)
        
        # 提示信息
        self.tip_label = QLabel('开启脚本前手动点击钟馗一下！！！')
        self.tip_label.setStyleSheet('color: magenta; font-weight: bold;')
        self.tip_label.setFont(QFont('Arial', 10))
        self.tip_label.setVisible(False)  # 初始隐藏
        task_layout.addWidget(self.tip_label)
        
        task_group.setLayout(task_layout)
        layout.addWidget(task_group)
        
        # 抓鬼设置组（默认隐藏，与采集设置保持一致）
        self.ghost_group = QGroupBox('抓鬼设置')
        self.ghost_group.setVisible(False)
        ghost_layout = QVBoxLayout()
        
        ghost_label = QLabel('设置抓多少轮鬼：')
        ghost_label.setFont(QFont('Arial', 10))
        ghost_layout.addWidget(ghost_label)
        
        self.zgls_edit = QLineEdit('15')
        self.zgls_edit.setPlaceholderText('请输入抓鬼轮数')
        self.zgls_edit.setFont(QFont('Arial', 10))
        ghost_layout.addWidget(self.zgls_edit)
        
        self.ghost_group.setLayout(ghost_layout)
        layout.addWidget(self.ghost_group)
        
        # 采集设置组（默认隐藏）
        self.collect_group = QGroupBox('采集设置')
        self.collect_group.setVisible(False)
        collect_layout = QVBoxLayout()
        
        # 地图选择
        map_label = QLabel('选择采集地图：')
        map_label.setFont(QFont('Arial', 10))
        collect_layout.addWidget(map_label)
        
        # 地图选择单选按钮组
        map_group = QButtonGroup(self)
        map_layout = QHBoxLayout()
        
        maps = ['东海', '长寿', '花果', '大雪', '两界']
        self.map_buttons = {}
        for i, map_name in enumerate(maps):
            radio = QRadioButton(map_name)
            if i == 0:
                radio.setChecked(True)
            map_group.addButton(radio, i)
            map_layout.addWidget(radio)
            self.map_buttons[map_name] = radio
        
        collect_layout.addLayout(map_layout)
        
        # 采集次数
        count_label = QLabel('设置采集次数：')
        count_label.setFont(QFont('Arial', 10))
        collect_layout.addWidget(count_label)
        
        self.cjcs_edit = QLineEdit('15')
        self.cjcs_edit.setPlaceholderText('请输入采集次数')
        self.cjcs_edit.setFont(QFont('Arial', 10))
        collect_layout.addWidget(self.cjcs_edit)
        
        self.collect_group.setLayout(collect_layout)
        layout.addWidget(self.collect_group)
        
        # 添加拉伸空间，将元素推到顶部
        layout.addStretch(1)
        
        # 按钮组
        button_layout = QHBoxLayout()
        
        # 开始按钮
        self.start_btn = QPushButton('开始执行')
        self.start_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.start_btn.setStyleSheet('background-color: green; color: white; padding: 10px;')
        self.start_btn.clicked.connect(self.on_start_clicked)
        button_layout.addWidget(self.start_btn)
        
        # 退出按钮
        exit_btn = QPushButton('退出')
        exit_btn.setFont(QFont('Arial', 12))
        exit_btn.setStyleSheet('background-color: red; color: white; padding: 10px;')
        exit_btn.clicked.connect(self.exit_application)
        button_layout.addWidget(exit_btn)
        
        layout.addLayout(button_layout)
        

    
    def on_task_changed(self, task_name):
        """任务选择改变事件"""
        # 根据选择的任务显示/隐藏相关设置
        if task_name == '抓鬼':
            self.ghost_group.setVisible(True)
            self.collect_group.setVisible(False)
            self.tip_label.setVisible(True)  # 选择抓鬼时显示提示
        elif task_name in ['采集花草', '挖掘矿石']:
            self.ghost_group.setVisible(False)
            self.collect_group.setVisible(True)
            self.tip_label.setVisible(False)  # 其他任务隐藏提示
        else:
            self.ghost_group.setVisible(False)
            self.collect_group.setVisible(False)
            self.tip_label.setVisible(False)  # 其他任务隐藏提示
    
    def on_start_clicked(self):
        """开始按钮点击事件"""
        # 收集界面数据
        self.界面数据 = {
            'job': str(self.job_combo.currentIndex()),  # 对应触动精灵的job索引
            'zgls': self.zgls_edit.text() or '15',
            'cjcs': self.cjcs_edit.text() or '15'
        }
        
        # 获取选择的地图
        selected_map = '东海'  # 默认
        for map_name, button in self.map_buttons.items():
            if button.isChecked():
                selected_map = map_name
                break
        self.界面数据['xzdt'] = selected_map
        
        # 验证输入
        if not self.validate_input():
            return
        
        self.start_btn.setEnabled(False)
        
        # 这里可以启动任务执行线程
        # 取消弹窗，使用add_log在终端日志中显示配置信息
        #add_log(f'开始执行{self.job_combo.currentText()}任务！配置: {json.dumps(self.界面数据, ensure_ascii=False)}')
        # 在实际实现中，这里会调用automation模块执行相应任务
        self.close()
    
    def exit_application(self):
        """退出应用程序，终止整个Python进程"""
        add_log("用户点击了退出按钮，程序将终止")
        # 首先关闭窗口
        self.close()
        # 然后退出应用程序，终止整个Python进程
        import sys
        sys.exit(0)
    
    def validate_input(self):
        """验证输入"""
        try:
            zgls = int(self.界面数据['zgls'])
            cjcs = int(self.界面数据['cjcs'])
            
            if zgls <= 0 or cjcs <= 0:
                QMessageBox.warning(self, '输入错误', '请输入大于0的数字！')
                return False
            
            return True
            
        except ValueError:
            QMessageBox.warning(self, '输入错误', '请输入有效的数字！')
            return False
    
    def get_config(self):
        """获取配置数据"""
        return self.界面数据

def show_ui(app=None):
    """显示用户界面"""
    # 如果没有提供QApplication实例，则创建一个
    if app is None:
        app = QApplication(sys.argv)
    
    window = ConfigWindow()
    window.show()
    window.activateWindow()
    
    # 使用QTimer定期检查窗口是否已经关闭
    from PyQt5.QtCore import QTimer
    
    def check_window_closed():
        if not window.isVisible():
            timer.stop()
            if window.界面数据:
                add_log(f"界面数据已收集: {window.界面数据}")
            else:
                add_log("未收集到界面数据")
    
    # 创建定时器，每100毫秒检查一次窗口状态
    timer = QTimer()
    timer.timeout.connect(check_window_closed)
    timer.start(100)
    
    # 如果没有提供app实例，说明是独立运行，需要启动事件循环
    if app is None:
        ret = app.exec_()
        if ret == 0 and window.界面数据:
            return 1, window.界面数据
        else:
            return 0, {}
    else:
        # 如果已经有app实例，说明事件循环已经在运行，直接返回
        # 注意：这里会立即返回，需要在主线程中处理界面数据
        return 1, window.界面数据

# 兼容触动精灵的接口
def showUI(config_json):
    """兼容触动精灵的showUI函数"""
    # 这里可以解析JSON配置，但在这个简单实现中我们使用固定界面
    ret, 界面数据 = show_ui()
    return ret, 界面数据

class LogWindow(QWidget):
    """日志显示窗口类"""
    
    def __init__(self, start_callback=None, pause_callback=None, stop_callback=None):
        super().__init__()
        self.start_callback = start_callback
        self.pause_callback = pause_callback
        self.stop_callback = stop_callback
        self.is_paused = False
        self.is_running = False
        self.init_ui()
        self.clear_log()  # 初始化时清空日志
        # 使用队列存储待显示的日志，避免日志覆盖
        self._pending_log_queue = []
        self.init_shortcuts()  # 初始化快捷键
    
    def init_shortcuts(self):
        """初始化键盘快捷键"""
        from PyQt5.QtGui import QKeySequence
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtCore import Qt, QTimer
        
        # 创建定时器，定期检查并确保窗口保持置顶
        self.stay_on_top_timer = QTimer(self)
        self.stay_on_top_timer.timeout.connect(self.ensure_stay_on_top)
        self.stay_on_top_timer.start(1000)  # 每秒检查一次
        
        # 暂停/继续快捷键 (左方向键)
        pause_shortcut = QShortcut(QKeySequence(Qt.Key_Left), self)
        pause_shortcut.activated.connect(self.on_pause_shortcut)
        
        # 开始快捷键 (上方向键)
        start_shortcut = QShortcut(QKeySequence(Qt.Key_Up), self)
        start_shortcut.activated.connect(self.on_start_shortcut)
        
        # 停止快捷键 (右方向键)
        stop_shortcut = QShortcut(QKeySequence(Qt.Key_Right), self)
        stop_shortcut.activated.connect(self.on_stop_shortcut)
    
    def on_pause_shortcut(self):
        """处理暂停/继续快捷键"""
        if self.pause_callback:
            # 切换暂停状态
            self.is_paused = not self.is_paused
            self.pause_callback(self.is_paused)
            
            # 更新暂停按钮状态
            if hasattr(self, 'pause_btn'):
                if self.is_paused:
                    self.pause_btn.setText('继续')
                    self.pause_btn.setStyleSheet('background-color: green; color: white; padding: 2px; border: none;')
                else:
                    self.pause_btn.setText('暂停')
                    self.pause_btn.setStyleSheet('background-color: orange; color: white; padding: 2px; border: none;')
            
    def on_start_shortcut(self):
        """处理开始快捷键"""
        if self.start_callback:
            self.start_callback()
            
    def on_stop_shortcut(self):
        """处理停止快捷键"""
        if self.stop_callback:
            self.stop_callback()
    
    def ensure_stay_on_top(self):
        """确保窗口保持置顶状态"""
        if self.isVisible():
            self.activateWindow()  # 激活窗口
            self.raise_()  # 确保窗口在最顶层
    
    def update_callbacks(self, start_callback=None, pause_callback=None, stop_callback=None):
        """更新回调函数"""
        if start_callback is not None:
            self.start_callback = start_callback
        if pause_callback is not None:
            self.pause_callback = pause_callback
        if stop_callback is not None:
            self.stop_callback = stop_callback
    
    def init_ui(self):
        """初始化日志窗口界面"""
        # 获取屏幕尺寸
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        
        # 调试信息
        add_log(f"屏幕尺寸: {screen_geometry.width()}x{screen_geometry.height()}")
        
        # 设置窗口位置和大小 - 增大尺寸使其更易被发现
        window_width = 300
        window_height = 250
        x = screen_geometry.width() - window_width - 20  # 右边距20像素
        y = screen_geometry.height() - window_height - 70  # 底边距70像素（考虑任务栏）
        
        # 确保窗口在屏幕可见范围内
        x = max(0, x)
        y = max(0, y)
        
        add_log(f"窗口位置: x={x}, y={y}, 大小: {window_width}x{window_height}")
        
        # 使用稳定的窗口类型 - 保留边框使其更易识别
        self.setWindowFlags(
            Qt.Window |  # 基础窗口类型
            Qt.WindowStaysOnTopHint |  # 保持置顶
            Qt.WindowMinimizeButtonHint |  # 添加最小化按钮
            Qt.WindowCloseButtonHint  # 添加关闭按钮
        )
        
        self.setGeometry(x, y, window_width, window_height)
        self.setWindowTitle('脚本日志')
        self.setStyleSheet('background-color: #000; border: none;')  # 移除边框，减少黑边
        self.raise_()  # 确保窗口在最顶层
        
        # 主布局 - 减少边距
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 设置布局边距为0
        layout.setSpacing(0)  # 设置控件间距为0
        self.setLayout(layout)
        
        # 日志显示区域 - 直接使用QTextEdit，它本身就有滚动功能
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont('Arial', 9))
        # 减少文本框内边距，移除边框
        self.log_text.setStyleSheet('background-color: #000; color: #0f0; padding: 3px; border: none;')
        self.log_text.setLineWrapMode(QTextEdit.WidgetWidth)
        
        # 直接将日志文本框添加到布局中
        layout.addWidget(self.log_text)
        
        # 控制按钮布局
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(0)
        
        # 启动按钮
        self.start_btn = QPushButton('启动')
        self.start_btn.setFont(QFont('Arial', 8))
        self.start_btn.setStyleSheet('background-color: #4CAF50; color: white; padding: 2px; border: none;')
        self.start_btn.clicked.connect(self.on_start_clicked)
        control_layout.addWidget(self.start_btn)
        
        # 暂停/继续按钮
        self.pause_btn = QPushButton('暂停')
        self.pause_btn.setFont(QFont('Arial', 8))
        self.pause_btn.setStyleSheet('background-color: orange; color: white; padding: 2px; border: none;')
        self.pause_btn.clicked.connect(self.on_pause_clicked)
        control_layout.addWidget(self.pause_btn)
        
        # 停止按钮
        self.stop_btn = QPushButton('停止')
        self.stop_btn.setFont(QFont('Arial', 8))
        self.stop_btn.setStyleSheet('background-color: red; color: white; padding: 2px; border: none;')
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        control_layout.addWidget(self.stop_btn)
        

        
        # 关闭按钮
        self.close_btn = QPushButton('关闭')
        self.close_btn.setFont(QFont('Arial', 8))
        self.close_btn.setStyleSheet('background-color: #666; color: white; padding: 2px; border: none;')
        self.close_btn.clicked.connect(self.close)
        control_layout.addWidget(self.close_btn)
        
        layout.addLayout(control_layout)
    
    def add_log(self, message):
        """添加日志信息"""
        # 使用QTimer.singleShot确保在主线程更新UI
        try:
            # 将消息添加到队列，避免日志覆盖
            self._pending_log_queue.append(message)
            
            # 使用QTimer.singleShot确保在主线程执行
            QTimer.singleShot(0, self.update_log_slot)
        except Exception as e:
            print(f"调用QTimer.singleShot失败: {e}")
            # 如果QTimer.singleShot失败，直接尝试更新（可能在主线程）
            try:
                self.log_text.append(message)
                cursor = QTextCursor(self.log_text.document())
                cursor.movePosition(QTextCursor.End)
                self.log_text.setTextCursor(cursor)
            except Exception as direct_e:
                print(f"直接更新UI失败: {direct_e}")
    
    @pyqtSlot()
    def update_log_slot(self):
        """用于invokeMethod调用的槽函数，更新日志信息"""
        try:
            # 处理队列中的所有日志消息
            while self._pending_log_queue:
                # 获取队列中的第一个日志消息
                message = self._pending_log_queue.pop(0)
                if message:
                    # 添加日志信息
                    self.log_text.append(message)
                    
                    # 确保自动滚动到底部
                    cursor = QTextCursor(self.log_text.document())
                    cursor.movePosition(QTextCursor.End)
                    self.log_text.setTextCursor(cursor)
                    
                    # 刷新UI
                    self.log_text.update()
        except Exception as e:
            print(f"更新日志槽函数失败: {e}")
    
    def clear_log(self):
        """清空日志内容"""
        try:
            # 使用QTimer.singleShot确保在主线程更新UI
            QTimer.singleShot(0, self.clear_log_slot)
        except Exception as e:
            print(f"调用QTimer.singleShot清空日志失败: {e}")
            # 如果QTimer.singleShot失败，直接尝试更新（可能在主线程）
            try:
                self.log_text.clear()
            except Exception as direct_e:
                print(f"直接清空UI失败: {direct_e}")
    
    @pyqtSlot()
    def clear_log_slot(self):
        """用于invokeMethod调用的槽函数，清空日志信息"""
        try:
            self.log_text.clear()
        except Exception as e:
            print(f"清空日志槽函数失败: {e}")
    
    def focusOutEvent(self, event):
        """处理失去焦点事件，确保窗口不会关闭"""
        # 重写此事件，什么也不做，防止窗口在失去焦点时关闭
        pass
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件，确保窗口不会关闭"""
        # 重写此事件，什么也不做，防止窗口在点击时关闭
        pass
    
    def closeEvent(self, event):
        """处理窗口关闭事件，如果脚本没有停止，先停止再关闭"""
        # 检查脚本是否正在运行
        if self.is_running and self.stop_callback:
            # 调用停止回调函数
            self.stop_callback()
            # 等待短暂时间确保停止命令生效
            import time
            time.sleep(0.5)
        # 接受关闭事件
        event.accept()
        # 退出整个应用程序，确保Python进程完全停止
        import sys
        sys.exit()
    
    def on_pause_clicked(self):
        """暂停/继续按钮点击事件"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.setText('继续')
            self.pause_btn.setStyleSheet('background-color: green; color: white; padding: 2px; border: none;')
            self.add_log('脚本已暂停...')
        else:
            self.pause_btn.setText('暂停')
            self.pause_btn.setStyleSheet('background-color: orange; color: white; padding: 2px; border: none;')
            self.add_log('脚本已恢复执行...')
        
        # 调用回调函数
        if self.pause_callback:
            self.pause_callback(self.is_paused)
    
    def on_start_clicked(self):
        """启动按钮点击事件"""
        self.add_log('开始执行任务...')
        self.is_running = True
        self.is_paused = False
        # 更新按钮状态
        self.start_btn.setText('启动')
        self.pause_btn.setText('暂停')
        self.pause_btn.setStyleSheet('background-color: orange; color: white; padding: 2px; border: none;')
        # 调用回调函数
        if self.start_callback:
            self.start_callback()
    
    def on_stop_clicked(self):
        """停止按钮点击事件"""
        self.add_log('脚本已停止...')
        self.is_running = False
        
        # 调用停止回调函数
        if self.stop_callback:
            self.stop_callback()
        
        # 如果暂停按钮显示的是继续状态，改回暂停状态
        if self.is_paused:
            self.is_paused = False
            self.pause_btn.setText('暂停')
            self.pause_btn.setStyleSheet('background-color: orange; color: white; padding: 2px; border: none;')
        
        # 调用回调函数
        if self.stop_callback:
            self.stop_callback()
    

    


            


# 全局日志窗口实例
log_window = None
# 未显示日志的缓冲区
pending_logs = []

# 显示日志窗口的函数
def show_log_window(start_callback=None, pause_callback=None, stop_callback=None):
    """显示日志窗口"""
    global log_window
    if log_window is None:
        log_window = LogWindow(start_callback, pause_callback, stop_callback)
        
        # 显示所有未显示的日志
        if pending_logs:
            for msg in pending_logs:
                log_window.add_log(msg)
            pending_logs.clear()
    else:
        # 更新回调函数
        log_window.update_callbacks(start_callback, pause_callback, stop_callback)
    
    log_window.show()
    log_window.activateWindow()  # 激活窗口
    log_window.raise_()  # 确保窗口在最顶层
    return log_window

# 添加日志的函数（内部使用，外部应使用log_utils.add_log）
def _add_log_to_ui(message):
    """添加日志信息到日志窗口"""
    global log_window, pending_logs
    if log_window is not None:
        log_window.add_log(message)
    else:
        # 保存未显示的日志到缓冲区
        pending_logs.append(message)

if __name__ == '__main__':
    ret, config = show_ui()
    add_log(f"返回值: {ret}, 配置: {config}")