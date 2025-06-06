# EditorialAgents

EditorialAgents 是一个用于生成完整科学文章的自动化工具。该工具通过分解问题、执行网络搜索和本地知识库检索，最终生成综合回答，帮助用户快速撰写高质量的科学文章。

## 目录

- [EditorialAgents](#editorialagents)
  - [目录](#目录)
  - [项目简介](#项目简介)
  - [组件](#组件)
  - [安装指南](#安装指南)
    - [下载安装 uv](#下载安装-uv)
    - [环境初始化](#环境初始化)
    - [安装依赖](#安装依赖)
    - [下载检索模型](#下载检索模型)
    - [配置 `config.yaml`](#配置-configyaml)
  - [启动项目](#启动项目)
    - [启动后端](#启动后端)
    - [启动前端](#启动前端)
  - [配置文件说明](#配置文件说明)
    - [配置结构](#配置结构)
      - [初始分析](#初始分析)
      - [网络搜索](#网络搜索)
      - [本地知识库 (KB)](#本地知识库-kb)
      - [综合回答](#综合回答)
      - [统一检索](#统一检索)
  - [使用指南](#使用指南)
    - [创建文章](#创建文章)
    - [编辑大纲](#编辑大纲)
    - [执行检索](#执行检索)
    - [生成文章](#生成文章)
  - [故障排除](#故障排除)
  - [许可协议](#许可协议)

## 项目简介

EditorialAgents 旨在自动化生成科学文章，适用于自然科学、医学、人文社科等多个领域。通过以下步骤，EditorialAgents 可以高效地生成结构完整且内容丰富的科学文章：

1. **输入**：提供一个主题（如自然科学、医学、人文社科等）以及相关描述和问题。
2. **处理过程**：分解问题、执行网络搜索和本地知识库搜索，最终生成综合回答。
3. **输出**：生成完整的科学文章。

## 组件

EditorialAgents 由以下几个关键组件组成：

- **问题初步分析 Agent**

  - 分析问题并给出框架
- **网络检索 Agent**

  - 使用 Tavily 搜索引擎进行关键词检索
  - 为检索到的文档生成总结
- **本地知识库检索 Agent**

  - 生成假设性文档
  - 使用假设性文档进行检索
  - 为检索到的文档生成总结
- **深度迭代检索模块**

  - 系统性分析并提取所有有价值信息
  - 自动评估内容完整性，确定是否需要进一步检索
  - 基于内容空缺生成针对性的检索查询
- **综合回答 Agent**

  - 根据所有检索文档和整体框架，分段落完成写作
- **Web 界面**

  - 用户友好的交互界面
  - 大纲编辑功能
  - 检索状态实时监控
  - 文章生成与预览

## 安装指南

### 下载安装 uv

[uv](https://hellowac.github.io/uv-zh-cn/) 是一个现代化的 Python 包管理工具，用于替代传统的 pip。安装 uv 的方法如下：

**MacOS/Linux**:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows**:

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**直接使用pip安装**:

```bash
pip install uv
```

验证安装:

```bash
uv --version
```

### 环境初始化

创建一个新的虚拟环境：

```bash
# 创建虚拟环境
uv venv -p 3.10

# 激活环境
# Linux/MacOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

### 安装依赖

安装所需依赖项：

```bash
# 安装依赖
uv sync
```

### 下载检索模型

进入 `models` 目录并克隆所需的模型仓库：

```bash
# 创建 models 目录（如果不存在）
mkdir -p models

# 进入 models 目录
cd models

# 克隆检索模型
git clone https://www.modelscope.cn/maidalun/bce-embedding-base_v1.git
git clone https://www.modelscope.cn/maidalun/bce-reranker-base_v1.git
```

### 配置 `config.yaml`

1. 在项目根目录下创建 `config.yaml` 文件：

```bash
# 回到项目根目录
cd ..

# 复制示例配置文件
cp config/config_example.yaml config/config.yaml
```

2. 编辑 `config.yaml` 文件，填入您的 API 密钥和其他配置：

```yaml
# 打开并编辑配置文件
# 使用您喜欢的文本编辑器，例如 VS Code
code config/config.yaml
```

请确保替换以下关键配置：

- OpenAI API 密钥
- 基础 URL
- Tavily 搜索 API 密钥
- 设备类型 (CUDA/CPU/MPS)

## 启动项目

### 启动后端

后端服务包括 API 服务器和处理逻辑：

```bash
# 在项目根目录下启动后端 API 服务
uvicorn web_api.main:app --reload --host 0.0.0.0 --port 8000
```

### 启动前端

前端提供用户界面：

```bash
# 进入前端目录
cd frontend-react

# 安装依赖（如果尚未安装）
npm install

# 启动开发服务器
npm run dev
# 或：.\node_modules\.bin\vite
```

启动后，您可以通过浏览器访问 http://localhost:5173/ 打开应用。

## 配置文件说明

### 配置结构

`config.yaml` 文件分为五个主要部分：

#### 初始分析

```yaml
initial_analysis:
  api_key: "YOUR_OPENAI_API_KEY"
  base_url: "YOUR_OPENAI_BASE_URL"
  model: "gpt-4o"
```

该部分配置初始分析阶段使用的语言模型和 API 设置。

#### 网络搜索

```yaml
web_search:
  api_key: "YOUR_OPENAI_API_KEY"
  base_url: "YOUR_OPENAI_BASE_URL"
  model: "gpt-4o"
  search_engine: "tavily"
  search_api_key: "YOUR_TAVILY_API_KEY"
  web_num: 5
  max_length: 2000
  max_workers: 10
```

该部分管理网络搜索功能，包括搜索引擎选择和并发设置。

#### 本地知识库 (KB)

```yaml
local_kb:
  api_key: "YOUR_OPENAI_API_KEY"
  base_url: "YOUR_OPENAI_BASE_URL"
  model: "gpt-4o"
  kb_path: "knowledge_base/test"
  embedding_model: "models/bce-embedding-base_v1"
  reranker_model: "models/bce-reranker-base_v1"
  k: 5
  top_n: 1
  chunk_size: 2000
  chunk_overlap: 200
  device: "YOUR_DEVICE" # cuda/cpu/mps
  max_workers: 10
```

该部分处理与本地知识库交互的设置，包括嵌入和重排序模型配置。

#### 综合回答

```yaml
comprehensive_answer:
  api_key: "YOUR_OPENAI_API_KEY"
  base_url: "YOUR_OPENAI_BASE_URL"
  model: "gpt-4o"
  max_workers: 10
```

该部分配置生成综合回答的参数。

#### 统一检索

```yaml
unified_search:
  max_iterations: 2
  web_max_concurrency: 5
  local_max_concurrency: 2
  max_retries: 3
  retry_delay: 1
  similarity_threshold: 0.7
  api_key: "YOUR_OPENAI_API_KEY"
  base_url: "YOUR_OPENAI_BASE_URL"
  model: "gpt-4o"
```

该部分配置统一检索模块的参数，包括迭代次数和并发设置。

## 使用指南

### 创建文章

1. 访问应用首页
2. 输入文章主题和描述
3. 点击"创建"按钮

### 编辑大纲

1. 在大纲页面查看自动生成的大纲
2. 可以添加、编辑或删除章节
3. 完成编辑后点击"保存大纲"

### 执行检索

1. 进入检索页面
2. 选择检索选项（网络检索、知识库检索）
3. 点击"开始检索"
4. 实时监控检索进度

### 生成文章

1. 检索完成后进入文章页面
2. 点击"开始生成文章"
3. 等待文章生成完成
4. 查看并导出最终文章

## 故障排除

- **API 密钥无效**：确保所有 API 密钥正确且具有必要的权限。
- **连接问题**：验证 `base_url` 的值是否正确，并确保网络允许对这些 URL 的外部请求。
- **资源限制**：如果遇到性能问题，可以考虑调整 `max_workers` 参数以更好地适应系统能力。
- **模型兼容性**：确保指定的模型可用且与你的 API 订阅兼容。
- **检索模型和重排模型**：当前版本只支持 BCE 模型，确保你使用的是正确的 BCE 模型。

## 许可协议

本项目采用 [MIT 许可](LICENSE) 进行许可。

---

如需进一步帮助，请联系 [huangkywork@163.com](mailto:huangkywork@163.com)。
