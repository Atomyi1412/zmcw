#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建示例宠物图像
生成三种状态的宠物图像用于测试
"""

import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QPen, QColor, QFont
from PyQt5.QtCore import Qt

def create_pet_image(state, size=(80, 80)):
    """创建宠物图像"""
    # 创建RGBA格式的pixmap确保透明度支持
    pixmap = QPixmap(size[0], size[1])
    pixmap.fill(QColor(0, 0, 0, 0))  # 完全透明的背景
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    # 设置合成模式确保透明度正确处理
    painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
    
    # 根据状态设置不同的颜色和形状
    if state == 'normal':
        # 正常状态：蓝色圆形
        painter.setBrush(QBrush(QColor(100, 150, 255)))
        painter.setPen(QPen(QColor(50, 100, 200), 2))
        painter.drawEllipse(10, 10, 60, 60)
        
        # 添加眼睛
        painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(25, 25, 10, 10)
        painter.drawEllipse(45, 25, 10, 10)
        
        painter.setBrush(QBrush(Qt.black))
        painter.drawEllipse(28, 28, 4, 4)
        painter.drawEllipse(48, 28, 4, 4)
        
        # 添加嘴巴
        painter.setPen(QPen(Qt.black, 2))
        painter.drawArc(30, 40, 20, 15, 0, 180 * 16)
        
    elif state == 'dragging':
        # 拖拽状态：绿色椭圆形（表示运动）
        painter.setBrush(QBrush(QColor(100, 255, 150)))
        painter.setPen(QPen(QColor(50, 200, 100), 2))
        painter.drawEllipse(5, 15, 70, 50)
        
        # 添加眼睛（惊讶表情）
        painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(20, 25, 12, 12)
        painter.drawEllipse(48, 25, 12, 12)
        
        painter.setBrush(QBrush(Qt.black))
        painter.drawEllipse(24, 29, 4, 4)
        painter.drawEllipse(52, 29, 4, 4)
        
        # 添加嘴巴（O形）
        painter.setBrush(QBrush(Qt.black))
        painter.drawEllipse(37, 42, 6, 8)
        
    elif state == 'falling':
        # 下落状态：红色圆形（表示紧张）
        painter.setBrush(QBrush(QColor(255, 100, 100)))
        painter.setPen(QPen(QColor(200, 50, 50), 2))
        painter.drawEllipse(10, 10, 60, 60)
        
        # 添加眼睛（害怕表情）
        painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(22, 22, 8, 12)
        painter.drawEllipse(50, 22, 8, 12)
        
        painter.setBrush(QBrush(Qt.black))
        painter.drawEllipse(24, 26, 4, 4)
        painter.drawEllipse(52, 26, 4, 4)
        
        # 添加嘴巴（倒U形）
        painter.setPen(QPen(Qt.black, 2))
        painter.drawArc(30, 45, 20, 15, 180 * 16, 180 * 16)
    
    painter.end()
    return pixmap

def main():
    """主函数"""
    # 创建QApplication实例（生成图像需要）
    app = QApplication([])
    
    # 确保assets目录存在
    assets_dir = 'assets'
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    # 生成三种状态的图像
    states = ['normal', 'dragging', 'falling']
    
    for state in states:
        print(f"正在生成 {state} 状态图像...")
        pixmap = create_pet_image(state)
        
        # 保存图像，确保透明度信息正确保存
        filename = f"assets/pet_{state}.png"
        # 使用PNG格式并确保透明度支持
        if pixmap.save(filename, 'PNG', 100):  # 质量100，保持透明度
            print(f"✓ 成功保存: {filename}")
        else:
            print(f"✗ 保存失败: {filename}")
    
    print("\n示例图像生成完成！")
    print("现在可以运行 python main.py 启动桌面宠物了。")

if __name__ == "__main__":
    main()