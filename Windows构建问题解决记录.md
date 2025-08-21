# Windows 构建问题解决记录

## 概述

本文档记录了桌面宠物项目在 GitHub Actions 中构建 Windows 安装包时遇到的问题及解决方案。

## 项目背景

- **项目名称**: 桌面宠物 (DesktopPet)
- **技术栈**: Python + PyQt5/PySide2
- **构建目标**: 生成 Windows EXE 安装包
- **构建工具**: PyInstaller + Inno Setup
- **CI/CD**: GitHub Actions

## 问题时间线与解决方案

### 问题 1: Windows 构建环境变更

**现象**: 
- GitHub Actions 的 `windows-latest` 标签从 Windows Server 2022 迁移到 Windows Server 2025
- 新环境中缺少 Inno Setup，导致构建失败

**解决方案**:
```yaml
# 方案A: 固定构建环境
runs-on: windows-2022

# 方案B: 自动安装 Inno Setup
- name: Install Inno Setup
  run: choco install innosetup --no-progress -y
```

**最终采用**: 方案B，在构建流程中自动检测并安装 Inno Setup

### 问题 2: Inno Setup 脚本语法错误

**现象**: 
```
Error on line 12: Undeclared identifier: GetStringDef
```

**原因**: 使用了不被支持的 ISPP 函数 `GetStringDef`

**解决方案**: 
```ini
; 错误写法
#define MyAppVersion GetStringDef("AppVersion", "0.0.0")

; 正确写法
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
```

### 问题 3: 相对路径解析失败

**现象**: Inno Setup 无法正确解析相对路径参数

**解决方案**: 在 GitHub Actions 中使用绝对路径
```powershell
$currentDir = Get-Location
$sourceDir = "$currentDir\dist\DesktopPet"
$outputDir = "$currentDir\dist\installer"

iscc $issScript /DSourceDir=$sourceDir /DOutputDir=$outputDir
```

### 问题 4: 语言包缺失

**现象**: 
```
Couldn't open include file "ChineseSimplified.isl": The system cannot find the file specified
```

**原因**: GitHub Actions Runner 上的 Inno Setup 安装不包含中文语言包

**解决方案**: 
```ini
; 移除缺失的语言包引用
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
```

### 问题 5: 错误处理机制不当

**现象**: 构建失败但没有明确错误信息

**解决方案**: 
- 移除 `continue-on-error: true`
- 添加详细的调试日志
- 实现 fail-fast 机制

## 最终工作流配置

### GitHub Actions 配置要点

```yaml
build-windows:
  runs-on: windows-2022  # 或使用 windows-latest + 自动安装
  steps:
    - name: Create EXE installer with Inno Setup
      shell: pwsh
      run: |
        # 检测并安装 Inno Setup
        $innoPath = @(
          "C:\Program Files (x86)\Inno Setup 6",
          "C:\Program Files\Inno Setup 6"
        ) | Where-Object { Test-Path $_ } | Select-Object -First 1
        
        if (-not $innoPath) {
          choco install innosetup --no-progress -y
          # 重新检测路径
        }
        
        # 使用绝对路径调用
        $currentDir = Get-Location
        $sourceDir = "$currentDir\dist\DesktopPet"
        $outputDir = "$currentDir\dist\installer"
        
        iscc $issScript /DAppVersion=${{ env.VERSION }} /DSourceDir=$sourceDir /DOutputDir=$outputDir
```

### Inno Setup 脚本配置要点

```ini
; 使用标准 ISPP 语法
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#ifndef SourceDir
  #define SourceDir "dist\\DesktopPet"
#endif

[Setup]
AppVersion={#AppVersion}
OutputDir={#OutputDir}
OutputBaseFilename={#OutBase}

[Languages]
; 仅使用可靠的默认语言包
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; 使用双反斜杠确保路径正确
Source: "{#SourceDir}\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
```

## 构建产物

成功构建后会生成以下产物：

1. **PyInstaller 原始文件夹**: `DesktopPet-Windows-folder-${VERSION}`
   - 包含可直接运行的应用程序文件夹
   - 适用于绿色版分发

2. **Inno Setup 安装包**: `DesktopPet-Windows-Installer-${VERSION}`
   - 包含 `DesktopPet-${VERSION}-Windows-Setup.exe`
   - 提供完整的安装向导体验

## 经验总结

### 最佳实践

1. **环境兼容性**: 优先使用自动安装而非依赖预装软件
2. **路径处理**: CI 环境中始终使用绝对路径
3. **错误处理**: 实现 fail-fast，避免静默失败
4. **语言包**: 使用最小可用集合，避免依赖可选组件
5. **调试信息**: 添加充分的日志输出便于问题排查

### 避免的陷阱

1. **不要使用** `continue-on-error: true` 掩盖真实错误
2. **不要依赖** 特定 Runner 镜像的预装软件
3. **不要使用** 非标准的 ISPP 函数
4. **不要假设** 所有语言包都可用

## 维护建议

1. **定期检查** GitHub Actions Runner 环境变更
2. **监控** Inno Setup 版本更新和兼容性
3. **测试** 不同 Windows 版本的安装包兼容性
4. **备份** 关键配置文件的工作版本

## 相关文件

- 工作流配置: `.github/workflows/build.yml`
- 安装脚本: `installer/desktop_pet.iss`
- 项目规格: `DesktopPet.spec`
- 依赖清单: `requirements.txt`

---

*文档创建时间: 2025年8月*  
*最后更新: 构建问题完全解决后*