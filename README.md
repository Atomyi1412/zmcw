# 桌面宠物 Desktop Pet

一个基于Python + PyQt5开发的可爱桌面陪伴应用，支持拖拽交互、动画效果和定时提醒功能。

## 🎯 功能特性

### 1.0版本 - 基础拖拽功能
- ✅ **宠物图像显示**：三种状态图像（正面、拖拽、下落）
- ✅ **拖拽交互**：点击拖拽宠物到任意位置
- ✅ **下落动画**：拖拽到屏幕上半部分触发重力下落和反弹效果
- ✅ **窗口优化**：无边框透明背景，置顶显示

### 2.0版本 - 定时提醒功能 🆕
- ✅ **右键菜单**：右键点击宠物显示功能菜单
- ✅ **提醒设置**：通过对话框设置提醒时间和内容
- ✅ **定时提醒**：到时间自动弹出提醒消息
- ✅ **智能定位**：提醒时宠物自动调整到最佳位置

## 🚀 快速开始

### 环境要求
- Python 3.7+
- PyQt5

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行应用
```bash
python3 main.py
```

## 📱 使用说明

### 基础操作
- **拖拽移动**：左键点击并拖拽宠物到任意位置
- **下落动画**：将宠物拖拽到屏幕上半部分释放触发下落动画
- **右键菜单**：右键点击宠物显示功能菜单

### 定时提醒功能
1. 右键点击宠物，选择"设置提醒"
2. 在对话框中选择提醒时间和输入提醒内容
3. 点击确认，系统将在指定时间弹出提醒
4. 提醒时宠物会自动移动到屏幕中央上方

## 🎨 项目结构

```
zmcw/
├── main.py              # 主程序入口
├── desktop_pet.py       # 桌面宠物主窗口类
├── pet_state.py         # 宠物状态枚举
├── reminder_dialog.py   # 提醒设置对话框
├── config.py           # 配置文件
├── requirements.txt    # 依赖包列表
├── assets/            # 图像资源
│   ├── pet_normal.png
│   ├── pet_dragging.png
│   └── pet_falling.png
└── README.md          # 项目说明
```

## ⚙️ 配置说明

可以通过修改 `config.py` 文件来自定义：
- 窗口大小和初始位置
- 动画持续时间和效果
- 提醒对话框尺寸
- 图像文件路径

## 🔧 技术实现

- **界面框架**：PyQt5
- **动画系统**：QPropertyAnimation + QEasingCurve
- **事件处理**：Qt事件系统
- **定时功能**：QTimer
- **对话框**：QDialog + QTimeEdit + QLineEdit

## 📝 更新日志

### v2.0.0 (2024-12-19)
- 🆕 新增右键菜单功能
- 🆕 新增定时提醒功能
- 🆕 新增提醒设置对话框
- 🆕 新增智能位置调整
- 🔧 优化用户交互体验

### v1.0.0 (2024-12-19)
- ✨ 基础拖拽功能
- ✨ 下落动画效果
- ✨ 透明窗口显示
- ✨ 三种状态图像

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📄 许可证

MIT License

一个基于Python + PyQt5开发的可爱桌面宠物应用，为您的桌面增添趣味性和陪伴感。

## 功能特性

### 🎯 核心功能
- **宠物显示**：在桌面右下角显示可爱的宠物形象
- **拖拽交互**：点击并拖拽宠物到任意位置
- **状态切换**：支持三种状态（正面、拖拽、下落）
- **下落动画**：将宠物拖拽到屏幕上半部分释放时触发重力下落和反弹效果
- **透明窗口**：无边框透明背景，置顶显示

### 🎨 界面特色
- 无边框透明窗口设计
- 平滑的动画过渡效果
- 可爱的宠物形象（三种状态）
- 置顶显示，不干扰其他应用

## 安装要求

### 系统要求
- Python 3.7+
- macOS / Windows / Linux

### 依赖包
```bash
pip install PyQt5
```

## 快速开始

### 1. 克隆或下载项目
```bash
git clone <repository-url>
cd zmcw
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 生成示例图像（可选）
```bash
python3 create_sample_images.py
```

### 4. 启动桌面宠物
```bash
python3 main.py
```

## 使用说明

### 基本操作
1. **启动应用**：运行 `python3 main.py`
2. **移动宠物**：点击并拖拽宠物到任意位置
3. **触发下落动画**：将宠物拖拽到屏幕上半部分释放
4. **退出程序**：关闭终端或使用 Ctrl+C

### 状态说明
- **正面状态（蓝色）**：宠物的默认状态
- **拖拽状态（绿色）**：正在拖拽时的状态
- **下落状态（红色）**：执行下落动画时的状态

## 项目结构

```
zmcw/
├── assets/                 # 图像资源目录
│   ├── pet_normal.png      # 正面状态图像
│   ├── pet_dragging.png    # 拖拽状态图像
│   └── pet_falling.png     # 下落状态图像
├── config.py               # 配置文件
├── pet_state.py            # 状态枚举定义
├── desktop_pet.py          # 主窗口类
├── main.py                 # 程序入口
├── create_sample_images.py # 图像生成脚本
├── requirements.txt        # 依赖包列表
└── README.md              # 项目说明
```

## 配置说明

在 `config.py` 中可以自定义以下参数：

```python
class PetConfig:
    # 窗口配置
    WINDOW_WIDTH = 100          # 窗口宽度
    WINDOW_HEIGHT = 100         # 窗口高度
    INITIAL_X_OFFSET = 150      # 距离右边缘距离
    INITIAL_Y_OFFSET = 150      # 距离底边缘距离
    
    # 动画配置
    FALL_DURATION = 1000        # 下落动画时长（毫秒）
    BOUNCE_HEIGHT = 50          # 反弹高度（像素）
    
    # 交互配置
    DRAG_THRESHOLD = 5          # 拖拽触发阈值（像素）
    SCREEN_TOP_THRESHOLD = 0.5  # 屏幕上半部分阈值
```

## 自定义图像

您可以替换 `assets/` 目录中的图像文件来自定义宠物外观：
- `pet_normal.png`：正面状态图像
- `pet_dragging.png`：拖拽状态图像
- `pet_falling.png`：下落状态图像

建议图像尺寸：80x80 像素，PNG格式，支持透明背景。

## 技术架构

### 核心技术
- **PyQt5**：GUI框架
- **QPropertyAnimation**：动画系统
- **QPixmap + QLabel**：图像显示
- **Qt事件系统**：鼠标交互处理

### 主要类
- `DesktopPet`：主窗口类，继承QWidget
- `PetState`：状态枚举类
- `PetConfig`：配置管理类

## 故障排除

### 常见问题

1. **PyQt5安装失败**
   ```bash
   pip install --upgrade pip
   pip install PyQt5
   ```

2. **图像显示异常**
   - 检查 `assets/` 目录中的图像文件是否存在
   - 运行 `python3 create_sample_images.py` 重新生成示例图像

3. **窗口无法显示**
   - 确保系统支持GUI应用程序
   - 检查是否有其他应用程序冲突

4. **动画效果异常**
   - 检查系统性能和显卡驱动
   - 调整 `config.py` 中的动画参数

## 开发计划

### 未来版本功能
- [ ] 右键菜单（退出、设置等）
- [ ] 多种宠物形象选择
- [ ] 自动行为（随机移动、表情变化）
- [ ] 声音效果
- [ ] 系统托盘集成
- [ ] 配置界面

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 致谢

感谢PyQt5社区提供的优秀GUI框架支持。