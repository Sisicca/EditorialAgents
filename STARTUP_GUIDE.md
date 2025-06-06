# EditorialAgents 启动指南

本项目提供了跨平台的一键启动脚本，支持 Windows、macOS 和 Linux 系统。

## 系统要求

### 通用要求
- **Conda**: 用于管理 Python 环境
- **Node.js 和 npm**: 用于运行前端服务
- **Python 环境**: DeepEdit conda 环境（包含项目依赖）

### 平台特定要求

#### Windows
- Windows 10 或更高版本
- PowerShell 或 Command Prompt

#### macOS
- macOS 10.14 或更高版本
- Terminal 应用程序

#### Linux
- 任何现代 Linux 发行版
- 终端模拟器（gnome-terminal、xterm、konsole 等）

## 使用方法

### Windows

1. 双击运行 `start.bat` 文件
2. 或者在命令提示符中执行：
   ```cmd
   start.bat
   ```

### macOS 和 Linux

1. 打开终端
2. 导航到项目目录：
   ```bash
   cd /path/to/Deep\ Editor
   ```
3. 给脚本添加执行权限（首次运行时）：
   ```bash
   chmod +x start.sh
   ```
4. 运行启动脚本：
   ```bash
   ./start.sh
   ```

## 脚本功能

启动脚本会自动执行以下操作：

1. **激活 Conda 环境**: 激活名为 `DeepEdit` 的 conda 环境
2. **启动后端服务**: 在新的终端窗口中启动 FastAPI 后端服务（端口 8000）
3. **启动前端服务**: 在新的终端窗口中启动 React 前端服务（端口 5173）
4. **打开浏览器**: 自动打开默认浏览器并导航到前端页面

## 服务地址

- **后端 API**: http://localhost:8000
- **前端界面**: http://localhost:5173
- **API 文档**: http://localhost:8000/docs

## 故障排除

### 常见问题

#### 1. Conda 环境不存在
```
Error: Failed to activate conda environment DeepEdit
```

**解决方案**:
- 确保已安装 Conda
- 创建 DeepEdit 环境：
  ```bash
  conda create -n DeepEdit python=3.9
  conda activate DeepEdit
  pip install -r requirements.txt
  ```

#### 2. npm 命令未找到
```
Error: npm is not installed or not in PATH
```

**解决方案**:
- 安装 Node.js 和 npm
- 确保 npm 在系统 PATH 中

#### 3. 端口被占用
如果端口 8000 或 5173 被占用，请：
- 关闭占用端口的程序
- 或修改脚本中的端口号

#### 4. Linux 下无法打开新终端窗口
脚本会尝试使用以下终端模拟器：
- gnome-terminal
- xterm
- konsole

如果都不可用，服务将在后台启动，日志输出到 `backend.log` 和 `frontend.log` 文件。

### 手动启动

如果自动启动脚本遇到问题，可以手动启动服务：

#### 启动后端
```bash
conda activate DeepEdit
uvicorn web_api.main:app --reload --host 0.0.0.0 --port 8000
```

#### 启动前端
```bash
cd frontend-react
npm run dev
```

## 停止服务

要停止应用程序：
1. 关闭后端和前端的终端窗口
2. 或在各自的终端中按 `Ctrl+C`

## 开发模式

启动脚本默认以开发模式运行：
- 后端启用热重载（`--reload`）
- 前端启用开发服务器
- 代码更改会自动反映在运行的服务中

## 注意事项

- 首次运行前请确保已安装所有依赖
- 在 Linux 系统上，可能需要安装额外的系统包
- 如果遇到权限问题，请检查文件权限设置
- 建议在虚拟环境中运行以避免依赖冲突