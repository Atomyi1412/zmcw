# Mac版本安装说明

## 问题说明
由于应用使用自签名（adhoc），从网络下载后可能被macOS Gatekeeper标记隔离（quarantine），导致首次启动被拦截或运行时加载受限（如扩展模块无法加载）。

## 解决方案

### 方法一：允许运行未签名应用（推荐）
1. 下载并安装 `DesktopPet-v1.4.2.dmg`
2. 如果出现"无法打开，因为无法验证开发者"的提示：
   - 打开 **系统偏好设置** > **安全性与隐私** > **通用**
   - 点击 **"仍要打开"** 按钮
   - 或者在应用上右键选择 **"打开"**，然后点击 **"打开"**

### 方法二：移除隔离属性（更推荐）
在终端中执行以下命令（任选其一）：
```bash
# 直接移除已安装应用的隔离属性（推荐）
xattr -rd com.apple.quarantine "/Applications/DesktopPet.app"

# 或者在挂载DMG前移除DMG文件的隔离属性
xattr -d com.apple.quarantine ~/Downloads/DesktopPet-v1.4.2.dmg
```

### 方法三：临时禁用Gatekeeper（不推荐）
```bash
# 禁用Gatekeeper（不推荐）
sudo spctl --master-disable

# 安装完成后立即重新启用
sudo spctl --master-enable
```

## 验证安装
安装成功后，应用应能直接从“应用程序”中启动；如仍异常，可在终端运行以下命令查看日志：
```bash
"/Applications/DesktopPet.app/Contents/MacOS/DesktopPet"
```

## 注意事项
- 本应用是开源软件，源代码可在GitHub上查看
- 如果仍有问题，请在GitHub Issues中反馈
- 建议从官方GitHub Releases页面下载最新版本（当前推荐：v1.4.2）