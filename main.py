#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌面宠物主程序入口
启动桌面宠物应用
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QIcon

# 兼容不同PyQt5版本的高DPI设置
try:
    from PyQt5.QtCore import Qt
    AA_EnableHighDpiScaling = getattr(Qt, 'AA_EnableHighDpiScaling', None)
    AA_UseHighDpiPixmaps = getattr(Qt, 'AA_UseHighDpiPixmaps', None)
except (ImportError, AttributeError):
    AA_EnableHighDpiScaling = None
    AA_UseHighDpiPixmaps = None

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 在macOS打包环境下，确保Resources与Frameworks目录在Python搜索路径中（修复某些环境下第三方包如bcrypt无法导入问题）
try:
    if getattr(sys, 'frozen', False) and sys.platform == 'darwin':
        exe_dir = os.path.dirname(sys.executable)  # .../Contents/MacOS
        contents_dir = os.path.abspath(os.path.join(exe_dir, '..'))  # .../Contents
        resources_dir = os.path.join(contents_dir, 'Resources')
        frameworks_dir = os.path.join(contents_dir, 'Frameworks')
        lib_dynload_dir = os.path.join(frameworks_dir, 'lib-dynload')
        for p in (resources_dir, frameworks_dir, lib_dynload_dir):
            if os.path.isdir(p) and p not in sys.path:
                sys.path.insert(0, p)
except Exception:
    pass

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
        # 在创建 QApplication 之前启用高DPI缩放（对 macOS/Retina 至关重要）
        try:
            if AA_EnableHighDpiScaling is not None:
                QCoreApplication.setAttribute(AA_EnableHighDpiScaling, True)
            if AA_UseHighDpiPixmaps is not None:
                QCoreApplication.setAttribute(AA_UseHighDpiPixmaps, True)
        except Exception:
            pass
        # 创建应用程序实例
        app = QApplication(sys.argv)
        
        # 设置应用程序属性
        app.setApplicationName("桌面宠物")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("DesktopPet")
        
        # 防止应用在最后一个窗口关闭时退出（适用于托盘应用）
        app.setQuitOnLastWindowClosed(False)
        
        # Windows特定：隐藏任务栏图标
        if os.name == 'nt':  # Windows系统
            try:
                import ctypes
                from ctypes import wintypes
                
                # 获取当前进程ID
                pid = os.getpid()
                
                # 定义Windows API函数
                user32 = ctypes.windll.user32
                kernel32 = ctypes.windll.kernel32
                
                # 枚举窗口回调函数
                def enum_windows_proc(hwnd, lParam):
                    # 获取窗口进程ID
                    window_pid = wintypes.DWORD()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
                    
                    # 如果是当前进程的窗口
                    if window_pid.value == pid:
                        # 获取窗口类名
                        class_name = ctypes.create_unicode_buffer(256)
                        user32.GetClassNameW(hwnd, class_name, 256)
                        
                        # 如果是Qt应用程序窗口，隐藏任务栏图标
                        if 'Qt' in class_name.value:
                            # 获取扩展窗口样式
                            ex_style = user32.GetWindowLongW(hwnd, -20)  # GWL_EXSTYLE
                            # 添加WS_EX_TOOLWINDOW样式来隐藏任务栏图标
                            ex_style |= 0x80  # WS_EX_TOOLWINDOW
                            user32.SetWindowLongW(hwnd, -20, ex_style)
                    
                    return True
                
                # 定义回调函数类型
                EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
                
                # 延迟执行，确保窗口已创建
                from PyQt5.QtCore import QTimer
                def hide_taskbar_icon():
                    try:
                        user32.EnumWindows(EnumWindowsProc(enum_windows_proc), 0)
                    except Exception as e:
                        print(f"隐藏任务栏图标时出错: {e}")
                
                # 延迟500ms执行
                QTimer.singleShot(500, hide_taskbar_icon)
                
            except Exception as e:
                print(f"Windows任务栏隐藏功能初始化失败: {e}")
        
        # 检查系统托盘支持
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "系统托盘", "系统不支持系统托盘功能")
            return 1
        
        # 设置应用程序图标
        tray_icon = None
        # 优先使用狗狗头像图标
        dog_icon_path = resource_path("assets/dog_icon.svg")
        if os.path.exists(dog_icon_path):
            tray_icon = QIcon(dog_icon_path)
        else:
            # 回退到其他图标
            if sys.platform.startswith('darwin'):
                icns_path = resource_path("assets/app.icns")
                if os.path.exists(icns_path):
                    tray_icon = QIcon(icns_path)
            elif os.name == 'nt':
                ico_path = resource_path("assets/app.ico")
                if os.path.exists(ico_path):
                    tray_icon = QIcon(ico_path)
            
            if not tray_icon:
                icon_path = resource_path("assets/icon.png")
                if os.path.exists(icon_path):
                    tray_icon = QIcon(icon_path)
        
        if tray_icon:
            app.setWindowIcon(tray_icon)
        
        # 创建桌面宠物窗口
        pet = DesktopPet()
        
        # 创建系统托盘
        if not tray_icon:
            tray_icon = QIcon()  # 创建空图标作为默认值
        system_tray = QSystemTrayIcon(tray_icon, app)
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 显示/隐藏宠物
        show_action = QAction("显示宠物", app)
        hide_action = QAction("隐藏宠物", app)
        
        def toggle_pet_visibility():
            if pet.isVisible():
                pet.hide()
                show_action.setVisible(True)
                hide_action.setVisible(False)
            else:
                pet.show()
                show_action.setVisible(False)
                hide_action.setVisible(True)
        
        def show_pet():
            pet.show()
            show_action.setVisible(False)
            hide_action.setVisible(True)
        
        def hide_pet():
            pet.hide()
            show_action.setVisible(True)
            hide_action.setVisible(False)
        
        show_action.triggered.connect(show_pet)
        hide_action.triggered.connect(hide_pet)
        
        # 设置菜单
        settings_action = QAction("设置", app)
        settings_action.triggered.connect(lambda: pet.show_settings_dialog())
        
        # 退出
        quit_action = QAction("退出", app)
        quit_action.triggered.connect(app.quit)
        
        # 添加菜单项
        tray_menu.addAction(hide_action)
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(settings_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        # 设置托盘菜单
        system_tray.setContextMenu(tray_menu)
        
        # 托盘图标双击事件
        def on_tray_activated(reason):
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
                toggle_pet_visibility()
        
        system_tray.activated.connect(on_tray_activated)
        
        # 显示托盘图标
        system_tray.show()
        
        # 初始状态：显示宠物，隐藏"显示宠物"菜单项
        pet.show()
        show_action.setVisible(False)
        
        # 设置托盘提示
        system_tray.setToolTip("桌面宠物 - 双击显示/隐藏宠物")
        
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