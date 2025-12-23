#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多点找色核心函数封装
"""

import pyautogui
import cv2
import numpy as np
from log_utils import add_log
from PIL import Image
import os
from datetime import datetime
from typing import Tuple, Optional, List, Dict

def hex_to_bgr(hex_color: int) -> Tuple[int, int, int]:
    """十六进制颜色(0xRRGGBB)转BGR元组"""
    r = (hex_color >> 16) & 0xFF
    g = (hex_color >> 8) & 0xFF
    b = hex_color & 0xFF
    return (b, g, r)

def parse_posandcolors(posandcolors: str) -> List[Dict]:
    """解析偏移点参数字符串"""
    points = []
    for point_str in posandcolors.split(','):
        parts = point_str.split('|')
        if len(parts) != 3:
            continue
        dx = int(parts[0])
        dy = int(parts[1])
        color = hex_to_bgr(int(parts[2], 16))
        points.append({'dx': dx, 'dy': dy, 'color': color})
    return points

def calculate_color_difference(c1: Tuple[int, int, int],
                               c2: Tuple[int, int, int]) -> int:
    """计算两个BGR颜色的差异，将结果映射到0-100范围"""
    # 计算曼哈顿距离(0-765)
    distance = abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2])
    # 映射到0-100范围
    return int((distance / 765) * 100)

def degree_to_threshold(degree: int) -> int:
    """将精度degree(1~100)转换为颜色差异阈值(0~100)"""
    if degree >= 100:
        return 0    # 完全匹配
    elif degree <= 1:
        return 100  # 最大差异
    else:
        return 100 - degree  # 直接返回差异值

def find_multi_color(image: np.ndarray,
                    color: int,
                    posandcolors: str,
                    degree: int,
                    x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int]:
    """
    多点找色主函数 - 在指定区域内查找匹配点
    返回的坐标是相对于原始逻辑坐标的
    """
    if image is None:
        add_log(f"图像为空，无法进行特征点检测")
        return -1, -1
    if degree < 1 or degree > 100:
        add_log(f"degree参数错误: {degree}，必须在1-100之间")
        return -1, -1

    height, width = image.shape[:2]
    # add_log(f"开始特征点检测 - 搜索区域尺寸: {width}x{height}")

    # 预处理参数
    base_color_bgr = hex_to_bgr(color)
    offsets = parse_posandcolors(posandcolors)
    threshold = degree_to_threshold(degree)
    
    # 辅助函数：将BGR颜色转换为十六进制字符串
    def bgr_to_hex(color):
        b, g, r = color
        return f"#{r:02x}{g:02x}{b:02x}"
    
    base_color_hex = bgr_to_hex(base_color_bgr)
    # add_log(f"基准颜色: {base_color_hex}, 偏移点数量: {len(offsets)}, 阈值: {threshold}")
    
    # 计算最大偏移量，确定有效的基准点遍历范围
    max_dx_positive = max([offset['dx'] for offset in offsets], default=0)
    max_dx_negative = abs(min([offset['dx'] for offset in offsets], default=0))
    max_dy_positive = max([offset['dy'] for offset in offsets], default=0)
    max_dy_negative = abs(min([offset['dy'] for offset in offsets], default=0))
    
    # 计算基准点的有效遍历范围
    start_x = max_dx_negative
    end_x = width - max_dx_positive
    start_y = max_dy_negative
    end_y = height - max_dy_positive
    
    # add_log(f"有效基准点范围: x={start_x}-{end_x}, y={start_y}-{end_y}")
    
    # 如果有效范围无效（搜索区域太小），直接返回未找到
    if start_x >= end_x or start_y >= end_y:
        add_log(f"搜索区域太小，无法容纳所有偏移点")
        return -1, -1
    
    # 遍历有效的基准点范围（图像已经是区域截图，坐标从0开始）
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            # 检查基准点
            current_pixel = image[y, x]
            current_color = (int(current_pixel[0]), int(current_pixel[1]), int(current_pixel[2]))
            current_color_hex = bgr_to_hex(current_color)

            diff = calculate_color_difference(current_color, base_color_bgr)
            if diff > threshold:
                # 只输出前几个点的信息，避免日志过多
                # if x < 3 and y < 3:
                    # add_log(f"点({x+x1},{y+y1})颜色: {current_color_hex}, 与基准色差异: {diff} > 阈值: {threshold}，跳过")
                continue

            # add_log(f"找到潜在基准点({x+x1},{y+y1})，颜色: {current_color_hex}, 差异: {diff}")
            
            # 检查所有偏移点
            valid = True
            offset_check_results = []
            for offset in offsets:
                nx = x + offset['dx']
                ny = y + offset['dy']

                # 检查偏移点是否在图像范围内
                if nx < 0 or nx >= width or ny < 0 or ny >= height:
                    offset_check_results.append(f"偏移点({nx},{ny})超出图像范围，无效")
                    valid = False
                    break

                # 获取偏移点颜色
                offset_pixel = image[ny, nx]
                offset_color = (int(offset_pixel[0]), int(offset_pixel[1]), int(offset_pixel[2]))
                offset_color_hex = bgr_to_hex(offset_color)
                target_color_hex = bgr_to_hex(offset['color'])

                # 计算颜色差异
                offset_diff = calculate_color_difference(offset_color, offset['color'])
                if offset_diff > threshold:
                    offset_check_results.append(f"偏移点({nx},{ny})颜色: {offset_color_hex}, 目标颜色: {target_color_hex}, 差异: {offset_diff} > 阈值: {threshold}，无效")
                    valid = False
                    break
                else:
                    offset_check_results.append(f"偏移点({nx},{ny})颜色: {offset_color_hex}, 目标颜色: {target_color_hex}, 差异: {offset_diff} <= 阈值: {threshold}，有效")

            # 精简日志：只输出前几个偏移点的检查结果，避免日志过多
            # if len(offset_check_results) > 3:
            #     add_log(f"... 检查了{len(offset_check_results)}个偏移点")
            # else:
            #     for result in offset_check_results:
            #         add_log(result)
            
            # 找到匹配点（转换回原始逻辑坐标）
            if valid:
                #add_log(f"找到特征点: 逻辑坐标({x+x1},{y+y1})")
                return (x + x1, y + y1)

    # 未找到匹配点
    # 添加调试日志
    base_color_hex = bgr_to_hex(base_color_bgr)
    
    # 获取搜索区域的部分像素颜色样本
    sample_points = []
    if height > 0 and width > 0:
        # 取搜索区域的四个角和中心点
        sample_coords = [(0, 0), (0, height-1), (width-1, 0), (width-1, height-1), (width//2, height//2)]
        for sx, sy in sample_coords:
            pixel = image[sy, sx]
            sample_color = (int(pixel[0]), int(pixel[1]), int(pixel[2]))
            sample_hex = bgr_to_hex(sample_color)
            # 转换为实际的逻辑坐标
            real_x = sx + x1
            real_y = sy + y1
            sample_points.append(f"({real_x},{real_y})={sample_hex}")
    
    #add_log(f"未检测到特征: 目标颜色={base_color_hex}({color}), 搜索区域=({x1},{y1})-({x2},{y2}), 样本像素: {', '.join(sample_points)}")
    
    return -1, -1

def capture_search_region_optimized(x1: int, y1: int, x2: int, y2: int) -> Tuple[Optional[np.ndarray], Tuple[int, int, int, int], Optional[np.ndarray]]:
    """
    优化版：只截取指定区域，正确处理Retina缩放
    返回: (区域图像, 坐标元组, 全屏图像)
    """
    try:
        # add_log(f"开始截取搜索区域: ({x1}, {y1})-({x2}, {y2})")
        # 1. 获取逻辑分辨率
        logical_size = pyautogui.size()
        # add_log(f"逻辑分辨率: {logical_size.width}x{logical_size.height}")

        # 2. 截取全屏获取原始尺寸
        pil_screenshot = pyautogui.screenshot()
        original_width, original_height = pil_screenshot.size
        # add_log(f"原始截图尺寸: {original_width}x{original_height}")

        # 3. 保存全屏图片（已注释）
        # if not os.path.exists("log"):
        #     os.makedirs("log")
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # full_path_original = f"log/full_screen_original_{timestamp}.png"
        # pil_screenshot.save(full_path_original)
        # add_log(f"全屏截图已保存到: {full_path_original}")

        # 缩放到逻辑尺寸并保存（已注释）
        if original_width != logical_size.width:
            full_screen_resized = pil_screenshot.resize(logical_size, Image.Resampling.LANCZOS)
            # full_path_resized = f"log/full_screen_resized_{timestamp}.png"
            # full_screen_resized.save(full_path_resized)
            # add_log(f"缩放后的全屏截图已保存到: {full_path_resized}")
            full_cv_resized = cv2.cvtColor(np.array(full_screen_resized), cv2.COLOR_RGB2BGR)
        else:
            full_cv_resized = cv2.cvtColor(np.array(pil_screenshot), cv2.COLOR_RGB2BGR)

        # 4. 计算缩放比例
        if original_width != logical_size.width:
            scale_factor = original_width / logical_size.width

            # 5. 将逻辑坐标转换为原始坐标
            x1_raw = int(x1 * scale_factor)
            y1_raw = int(y1 * scale_factor)
            x2_raw = int(x2 * scale_factor)
            y2_raw = int(y2 * scale_factor)

            # 6. 截取原始区域
            width_raw = x2_raw - x1_raw + 1
            height_raw = y2_raw - y1_raw + 1
            region_img = pil_screenshot.crop((x1_raw, y1_raw, x2_raw + 1, y2_raw + 1))

            # 7. 缩放到逻辑尺寸
            target_width = x2 - x1 + 1
            target_height = y2 - y1 + 1
            resized_img = region_img.resize((target_width, target_height), Image.Resampling.LANCZOS)

        else:
            # 无需缩放
            target_width = x2 - x1 + 1
            target_height = y2 - y1 + 1
            region_img = pil_screenshot.crop((x1, y1, x2 + 1, y2 + 1))
            resized_img = region_img

        # 8. 转换为OpenCV格式
        cv_image = cv2.cvtColor(np.array(resized_img), cv2.COLOR_RGB2BGR)

        # 9. 保存区域截图（可选，已注释）
        # save_path = f"log/search_region_{timestamp}.png"
        # cv2.imwrite(save_path, cv_image)

        return cv_image, (x1, y1, x2, y2), full_cv_resized

    except Exception as e:
        add_log(f"❌ 截屏失败: {e}")
        return None, None, None

def findMultiColor(color: int,
                   posandcolors: str,
                   degree: int,
                   x1: int, y1: int,
                   x2: int, y2: int,
                   show_result: bool = False) -> Tuple[int, int]:
    """
    多点找色函数 - 优化版（仅截取指定区域）

    参数：
        color: number - 基准点颜色 (0xRRGGBB)
        posandcolors: string - 偏移点参数 "dx1|dy1|color1,dx2|dy2|color2,..."
        degree: number - 精度 (1-100)
        x1, y1, x2, y2: number - 搜索区域（逻辑坐标）
        show_result: bool - 是否显示结果图片（默认False）

    返回：
        (x, y) - 匹配点坐标，未找到返回 (-1, -1)
    """
    # 截取区域
    image, region, full_image = capture_search_region_optimized(x1, y1, x2, y2)
    if image is None:
        return -1, -1

    x1, y1, x2, y2 = region

    # 执行查找
    result = find_multi_color(image, color, posandcolors, degree, x1, y1, x2, y2)

    # 显示结果（可选）
    if show_result and result != (-1, -1):
        add_log(f"\n✅ findMultiColor 找到匹配点: {result}")

        try:
            # 在全屏图上标记
            if full_image is not None:
                full_display = full_image.copy()
                cv2.rectangle(full_display, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(full_display, result, 8, (0, 0, 255), -1)
                cv2.circle(full_display, result, 12, (0, 0, 255), 2)
                cv2.putText(full_display, "MATCH", (result[0]+15, result[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # 在搜索区域也标记
                local_rx = result[0] - x1
                local_ry = result[1] - y1
                search_display = image.copy()
                cv2.circle(search_display, (local_rx, local_ry), 6, (0, 0, 255), -1)
                cv2.circle(search_display, (local_rx, local_ry), 10, (0, 0, 255), 2)

                cv2.imshow("Full Screen Result", full_display)
                cv2.imshow("Search Region Result", search_display)
                print("按任意键关闭图像窗口...")
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        except:
            pass

    return result
