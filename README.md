# 桌面宠物 Desktop Pet

一个基于Python + PyQt5开发的可爱桌面陪伴应用，支持拖拽交互、动画效果、定时提醒和系统托盘功能。

## 🎯 功能特性

### 🐾 核心功能
- ✅ **宠物显示**：可爱的桌面宠物形象，支持三种状态（正常、拖拽、下落）
- ✅ **拖拽交互**：点击并拖拽宠物到任意位置
- ✅ **下落动画**：将宠物拖拽到屏幕上半部分释放触发重力下落和反弹效果
- ✅ **透明窗口**：无边框透明背景，置顶显示，不干扰其他应用

### 🔔 提醒功能
- ✅ **单次提醒**：设置指定时间的一次性提醒
- ✅ **循环提醒**：支持按分钟/小时间隔的重复提醒
- ✅ **提醒管理**：查看、编辑、删除多个提醒任务
- ✅ **智能定位**：提醒时宠物自动调整到最佳位置
- ✅ **数据持久化**：提醒数据自动保存，重启后恢复

### 🖥️ 系统托盘
- ✅ **托盘图标**：在系统托盘显示可爱的狗狗头像
- ✅ **托盘菜单**：右键托盘图标显示功能菜单
- ✅ **显示/隐藏**：双击托盘图标或菜单项切换宠物显示状态
- ✅ **任务栏隐藏**：Windows系统下自动隐藏任务栏图标
- ✅ **程序坞隐藏**：macOS系统下自动隐藏程序坞图标

### ⚙️ 个性化设置
- ✅ **置顶显示**：可选择是否始终置顶显示
- ✅ **宠物缩放**：支持50%-200%的大小调整
- ✅ **自动下落**：可开启/关闭自动下落功能
- ✅ **开机自启**：支持开机自动启动（可选）
- ✅ **宠物命名**：自定义宠物名称

### 🌍 跨平台支持
- ✅ **Windows**：完整支持，包含任务栏隐藏功能
- ✅ **macOS**：完整支持，包含程序坞隐藏功能
- ✅ **Linux**：基础功能支持

## 🚀 快速开始

### 环境要求
- Python 3.7+
- PyQt5
- 支持系统托盘的桌面环境

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行应用
```bash
python3 main.py
```

### 下载预编译版本
访问 [Releases](https://github.com/Atomyi1412/zmcw/releases) 页面下载：
- **Windows**：`DesktopPet-Windows-Installer.exe`
- **macOS**：`DesktopPet-v1.4.2.dmg`

#### v1.4.2 更新说明（推荐）
- 🔥 进一步修复macOS启动问题：确保 bcrypt 扩展在 DMG 安装后可被正确加载
- ✅ 在打包入口中增强 macOS 下的 sys.path 配置（Contents/Resources、Frameworks、lib-dynload）
- ✅ 在打包配置中显式收集 bcrypt 纯包和 `_bcrypt.abi3.so` 扩展

#### v1.4.1 更新说明（历史）
- 🔥 修复关键问题：解决bcrypt模块导入错误导致的闪退问题
- ✅ 完善PyInstaller打包配置，确保所有依赖正确包含
- ✅ 修复Mac版本从GitHub下载后无法启动的问题
- ✅ 提升应用稳定性和兼容性

#### v1.4.0 更新说明
- ✅ 修复Mac版本兼容性问题
- ✅ 解决PyQt5高DPI属性访问错误
- ✅ 提升应用启动稳定性
- ✅ 优化资源路径处理逻辑

#### Mac安装问题解决
如果Mac版本下载后无法打开或闪退，请参考：
- 📖 [Mac安装说明](Mac安装说明.md) - 详细解决方案
- 🔧 [一键修复脚本](fix_mac_quarantine.sh) - 自动移除隔离属性

**快速解决方法：**
1. 右键点击应用选择"打开"
2. 或在终端执行：`xattr -rd com.apple.quarantine /Applications/DesktopPet.app`

## 📱 使用说明

### 基础操作
- **拖拽移动**：左键点击并拖拽宠物到任意位置
- **下落动画**：将宠物拖拽到屏幕上半部分释放触发下落动画
- **右键菜单**：右键点击宠物显示功能菜单
- **系统托盘**：双击托盘图标显示/隐藏宠物

### 提醒功能
1. **设置单次提醒**：
   - 右键点击宠物，选择"设置提醒"
   - 选择"单次提醒"，设置时间和内容
   - 点击确认，到时间会自动弹出提醒

2. **设置循环提醒**：
   - 选择"循环提醒"，设置间隔时间和内容
   - 支持按分钟或小时间隔重复提醒

3. **管理提醒**：
   - 右键选择"提醒管理"查看所有提醒
   - 可以编辑、删除或暂停提醒

### 个性化设置
1. 右键点击宠物，选择"设置"
2. 在设置对话框中调整：
   - 置顶显示开关
   - 宠物大小（50%-200%）
   - 自动下落功能
   - 开机自启动
   - 宠物名称

## 🎨 项目结构

```
zmcw/
├── main.py                    # 主程序入口，系统托盘管理
├── desktop_pet.py             # 桌面宠物主窗口类
├── pet_state.py               # 宠物状态枚举
├── config.py                  # 配置文件
├── reminder_dialog.py         # 提醒设置对话框
├── reminder_list_dialog.py    # 提醒管理对话框
├── reminder_manager.py        # 提醒管理器
├── settings_dialog.py         # 设置对话框
├── requirements.txt           # 依赖包列表
├── DesktopPet.spec           # PyInstaller打包配置
├── assets/                   # 图像资源
│   ├── dog_icon.svg          # 托盘图标
│   ├── icon.png              # 应用图标
│   ├── pet_normal.png        # 正常状态
│   ├── pet_dragging.png      # 拖拽状态
│   └── pet_falling.png       # 下落状态
├── installer/                # 安装程序配置
│   └── desktop_pet.iss       # Inno Setup脚本
├── .github/workflows/        # GitHub Actions
│   └── build.yml             # 自动构建配置
└── 自定义图片说明.md          # 图片自定义指南
```

## ⚙️ 配置说明

可以通过修改 `config.py` 文件来自定义：

### 窗口配置
- `WINDOW_WIDTH/HEIGHT`：宠物窗口大小
- `INITIAL_X/Y_OFFSET`：初始位置偏移
- `DEFAULT_PET_SCALE`：默认缩放比例

### 动画配置
- `FALL_DURATION`：下落动画时长
- `BOUNCE_HEIGHT`：反弹高度
- `LEAF_FALL_DURATION`：叶子飘落效果时长

### 提醒配置
- `DEFAULT_REPEAT_INTERVAL`：默认循环间隔
- `REMINDER_MESSAGE_DURATION`：提醒显示时长
- `AUTO_CLEANUP_EXPIRED_DAYS`：自动清理过期提醒天数

### 个性化配置
- `DEFAULT_PET_NAME`：默认宠物名称
- `DEFAULT_AUTO_FALL`：默认自动下落开关
- `ALWAYS_ON_TOP`：默认置顶显示

## 🔧 技术实现

### 核心技术栈
- **界面框架**：PyQt5
- **动画系统**：QPropertyAnimation + QEasingCurve
- **事件处理**：Qt事件系统
- **定时功能**：QTimer
- **数据存储**：JSON文件
- **系统集成**：QSystemTrayIcon
- **跨平台**：ctypes (Windows API调用)

### 主要类结构
- `DesktopPet`：主窗口类，处理宠物显示和交互
- `ReminderManager`：提醒管理器，处理定时任务
- `SettingsDialog`：设置对话框，个性化配置
- `ReminderDialog/ReminderListDialog`：提醒相关对话框
- `PetConfig`：配置管理类

## 🎨 自定义图片

支持自定义宠物图片和托盘图标，详见 [自定义图片说明.md](自定义图片说明.md)：

### 宠物图片要求
- **格式**：PNG（支持透明度）
- **尺寸**：推荐80x80像素
- **文件名**：`pet_normal.png`、`pet_dragging.png`、`pet_falling.png`

### 托盘图标要求
- **格式**：SVG（矢量格式，推荐）
- **尺寸**：16x16-32x32像素
- **设计**：简洁单色，适合小尺寸显示

## 📦 打包和分发

### 本地打包
```bash
# 安装PyInstaller
pip install pyinstaller

# 打包应用
pyinstaller DesktopPet.spec
```

### 自动构建
项目配置了GitHub Actions自动构建：
- 推送代码自动触发构建
- 创建标签自动发布Release
- 同时构建Windows和macOS版本

## 📝 更新日志

### v1.2.0 (2024-12)
- 🆕 新增系统托盘功能
- 🆕 Windows任务栏图标隐藏
- 🆕 macOS程序坞图标隐藏
- 🎨 更新托盘图标设计
- 🔧 完善跨平台兼容性

### v1.1.0 (2024-12)
- 🆕 新增个性化设置对话框
- 🆕 支持宠物大小缩放
- 🆕 新增自动下落开关
- 🆕 支持开机自启动设置
- 🆕 新增宠物命名功能

### v1.0.0 (2024-12)
- 🆕 新增提醒管理功能
- 🆕 支持单次和循环提醒
- 🆕 新增提醒列表管理
- 🆕 数据持久化存储
- 🔧 优化用户交互体验

### v0.9.0 (2024-12)
- ✨ 基础拖拽功能
- ✨ 下落动画效果
- ✨ 透明窗口显示
- ✨ 三种状态图像

## 🛠️ 故障排除

### 常见问题

1. **PyQt5安装失败**
   ```bash
   pip install --upgrade pip
   pip install PyQt5
   ```

2. **系统托盘不显示**
   - 确保系统支持系统托盘功能
   - 检查系统托盘设置是否允许显示图标

3. **图片显示异常**
   - 检查 `assets/` 目录中的图像文件是否存在
   - 确保图片格式为PNG且支持透明度

4. **提醒功能异常**
   - 检查系统时间设置是否正确
   - 确保应用有足够的系统权限

5. **Windows任务栏图标仍然显示**
   - 重启应用程序
   - 检查Windows版本兼容性

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 开发环境设置
1. Fork本仓库
2. 克隆到本地：`git clone <your-fork-url>`
3. 安装依赖：`pip install -r requirements.txt`
4. 运行测试：`python3 main.py`

### 提交规范
- 使用清晰的提交信息
- 遵循现有的代码风格
- 添加必要的注释和文档

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- PyQt5社区提供的优秀GUI框架
- 所有贡献者和用户的支持
- 开源社区的宝贵建议

---

**让可爱的桌面宠物陪伴您的工作时光！** 🐾✨