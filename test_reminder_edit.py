#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试编辑提醒功能的修复效果
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reminder_list_dialog import ReminderEditDialog
from reminder_manager import ReminderManager

def test_reminder_edit_dialog():
    """测试编辑提醒对话框"""
    app = QApplication(sys.argv)
    
    # 创建提醒管理器
    reminder_manager = ReminderManager()
    
    # 存储对话框引用以便清理
    dialogs = []
    
    def safe_cleanup():
        """安全清理所有对话框"""
        print("开始清理资源...")
        for dialog in dialogs:
            try:
                if dialog and not dialog.isHidden():
                    dialog.close()
                    dialog.deleteLater()
            except Exception as e:
                print(f"清理对话框时出错: {e}")
        dialogs.clear()
        
        # 延迟退出应用
        QTimer.singleShot(500, app.quit)
    
    # 测试添加提醒对话框
    print("测试添加提醒对话框...")
    add_dialog = ReminderEditDialog()
    dialogs.append(add_dialog)
    
    # 设置测试数据
    add_dialog.title_edit.setText("测试提醒")
    add_dialog.content_edit.setText("这是一个测试提醒")
    
    # 显示对话框
    add_dialog.show()
    
    # 设置定时器自动关闭对话框
    def close_dialog():
        print("自动关闭对话框...")
        try:
            add_dialog.accept_reminder()
            print("✓ 确定按钮测试通过")
        except Exception as e:
            print(f"✗ 确定按钮测试失败: {e}")
        
        # 测试取消按钮
        cancel_dialog = ReminderEditDialog()
        dialogs.append(cancel_dialog)
        cancel_dialog.show()
        
        def test_cancel():
            try:
                cancel_dialog.safe_reject()
                print("✓ 取消按钮测试通过")
            except Exception as e:
                print(f"✗ 取消按钮测试失败: {e}")
            
            # 测试关闭按钮
            close_dialog_test = ReminderEditDialog()
            dialogs.append(close_dialog_test)
            close_dialog_test.show()
            
            def test_close():
                try:
                    close_dialog_test.close()
                    print("✓ 关闭按钮测试通过")
                except Exception as e:
                    print(f"✗ 关闭按钮测试失败: {e}")
                
                print("\n所有测试完成！")
                # 安全清理并退出
                QTimer.singleShot(500, safe_cleanup)
            
            QTimer.singleShot(1000, test_close)
        
        QTimer.singleShot(1000, test_cancel)
    
    QTimer.singleShot(2000, close_dialog)
    
    return app.exec_()

if __name__ == '__main__':
    print("开始测试编辑提醒功能...")
    test_reminder_edit_dialog()
    print("测试结束。")