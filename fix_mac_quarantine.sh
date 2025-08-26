#!/bin/bash

# Mac版本桌面宠物 - 修复隔离属性脚本
# 此脚本用于移除macOS的隔离属性，解决从网络下载的应用无法运行的问题

echo "=== 桌面宠物 Mac版本修复脚本 ==="
echo "正在修复macOS隔离属性问题..."
echo ""

# 检查应用是否存在
if [ -d "/Applications/DesktopPet.app" ]; then
    echo "✓ 找到应用：/Applications/DesktopPet.app"
    
    # 移除隔离属性
    echo "正在移除隔离属性..."
    xattr -d com.apple.quarantine "/Applications/DesktopPet.app" 2>/dev/null
    
    # 检查是否成功
    if [ $? -eq 0 ]; then
        echo "✓ 隔离属性已移除"
    else
        echo "! 隔离属性可能已经不存在或移除失败"
    fi
    
    echo ""
    echo "尝试启动应用..."
    open "/Applications/DesktopPet.app"
    
    echo "✓ 修复完成！如果应用仍无法运行，请查看 Mac安装说明.md"
else
    echo "✗ 未找到应用，请先安装 DesktopPet-v1.4.0.dmg"
    echo "下载地址：https://github.com/Atomyi1412/zmcw/releases"
fi

echo ""
echo "如果仍有问题，请访问：https://github.com/Atomyi1412/zmcw/issues"