# Mac版本安装说明

## 问题说明
由于应用使用自签名（adhoc），从网络下载后可能被macOS Gatekeeper阻止运行，导致闪退。

## 解决方案

### 方法一：允许运行未签名应用（推荐）
1. 下载并安装 `DesktopPet-v1.4.0.dmg`
2. 如果出现"无法打开，因为无法验证开发者"的提示：
   - 打开 **系统偏好设置** > **安全性与隐私** > **通用**
   - 点击 **"仍要打开"** 按钮
   - 或者在应用上右键选择 **"打开"**，然后点击 **"打开"**

### 方法二：移除隔离属性
在终端中执行以下命令：
```bash
# 移除DMG文件的隔离属性
xattr -d com.apple.quarantine ~/Downloads/DesktopPet-v1.4.0.dmg

# 或者移除应用的隔离属性
xattr -d com.apple.quarantine /Applications/DesktopPet.app
```

### 方法三：临时禁用Gatekeeper（不推荐）
```bash
# 禁用Gatekeeper
sudo spctl --master-disable

# 安装完成后重新启用
sudo spctl --master-enable
```

## 验证安装
安装成功后，应用应该能够正常启动并显示桌面宠物。

## 注意事项
- 本应用是开源软件，源代码可在GitHub上查看
- 如果仍有问题，请在GitHub Issues中反馈
- 建议从官方GitHub Releases页面下载最新版本