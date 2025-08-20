#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌面宠物主程序入口
启动桌面宠物应用
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 资源路径（兼容 PyInstaller）
def resource_path(relative_path: str) -> str:
    try:
        base_path = getattr(sys, '_MEIPASS')
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

try:
    from desktop_pet import DesktopPet
except ImportError as e:
    print(f"导入错误：{e}")
    print("请确保已安装PyQt5：pip install PyQt5")
    sys.exit(1)

def check_dependencies():
    """检查依赖项"""
    try:
        import PyQt5
        return True
    except ImportError:
        return False

def show_error_message(title, message):
    """显示错误消息"""
    try:
        app = QApplication(sys.argv)
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()
    except:
        print(f"{title}: {message}")

def main():
    """主函数"""
    # 检查依赖项
    if not check_dependencies():
        show_error_message(
            "依赖项缺失",
            "缺少PyQt5依赖项。\n\n请运行以下命令安装：\npip install PyQt5"
        )
        return 1
    
    try:
        # 创建应用程序实例
        app = QApplication(sys.argv)
        
        # 设置应用程序属性
        app.setApplicationName("桌面宠物")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("DesktopPet")
        
        # 设置应用程序图标（如果存在）
        icon_path = resource_path("assets/icon.png")
        if os.path.exists(icon_path):
            from PyQt5.QtGui import QIcon
            app.setWindowIcon(QIcon(icon_path))
        
        # 创建桌面宠物窗口
        pet = DesktopPet()
        
        # 显示窗口
        pet.show()
        
        print("桌面宠物已启动！")
        print("使用说明：")
        print("- 点击并拖拽宠物可以移动位置")
        print("- 将宠物拖拽到屏幕上半部分释放会触发下落动画")
        print("- 右键点击可以退出程序")
        
        # 运行应用程序事件循环
        return app.exec_()
        
    except Exception as e:
        error_msg = f"启动桌面宠物时发生错误：\n{str(e)}"
        print(error_msg)
        show_error_message("启动错误", error_msg)
        return 1

if __name__ == "__main__":
    sys.exit(main())