# EditorialAgents

EditorialAgents 是一个用于生成完整科学文章的自动化工具。该工具通过分解问题、执行网络搜索和本地知识库检索，最终生成综合回答，帮助用户快速撰写高质量的科学文章。

## 目录

- [EditorialAgents](#editorialagents)
  - [目录](#目录)
  - [项目简介](#项目简介)
  - [目标](#目标)
  - [组件](#组件)
  - [前提条件](#前提条件)
  - [安装指南](#安装指南)
    - [环境初始化](#环境初始化)
    - [安装依赖](#安装依赖)
    - [下载模型](#下载模型)
    - [配置 `config.yaml`](#配置-configyaml)
    - [保存配置](#保存配置)
  - [配置文件说明](#配置文件说明)
    - [配置结构](#配置结构)
      - [初始分析](#初始分析)
      - [网络搜索](#网络搜索)
      - [本地知识库 (KB)](#本地知识库-kb)
      - [综合回答](#综合回答)
    - [参数说明](#参数说明)
      - [API 密钥和基础 URL](#api-密钥和基础-url)
      - [模型配置](#模型配置)
      - [并发设置](#并发设置)
      - [其他参数](#其他参数)
  - [示例用法](#示例用法)
  - [示例操作](#示例操作)
    - [一键成文](#一键成文)
    - [交互页面](#交互页面)
  - [故障排除](#故障排除)
  - [许可协议](#许可协议)

## 项目简介

EditorialAgents 旨在自动化生成科学文章，适用于自然科学、医学、人文社科等多个领域。通过以下步骤，EditorialAgents 可以高效地生成结构完整且内容丰富的科学文章：

1. **输入**：提供一个主题（如自然科学、医学、人文社科等）以及相关描述和问题。
2. **处理过程**：分解问题、执行网络搜索和本地知识库搜索，最终生成综合回答。
3. **输出**：生成完整的科学文章。

## 目标

- **输入**：某个主题（自然科学、医学、人文社科等），以及相关描述和问题。
- **过程**：
  - 分解问题
  - 联网搜索
  - 本地知识库搜索
  - 综合回答
- **输出**：完整的科学文章

## 组件

EditorialAgents 由以下几个关键组件组成：

- **问题初步分析 Agent（gpt4o）**
  - 分析问题并给出框架
  
- **网络检索 Agent（gpt3.5-turbo）**
  - 使用 Tavily 搜索引擎进行关键词检索
  - 为检索到的文档生成总结
  
- **本地知识库检索 Agent（gpt3.5-turbo）**
  - 生成假设性文档
  - 使用假设性文档进行检索
  - 为检索到的文档生成总结
  
- **综合回答 Agent（gpt4o）**
  - 根据所有检索文档和整体框架，分段落完成写作

- **参考文献** 
  - [Precise Zero-Shot Dense Retrieval without Relevance Labels](https://arxiv.org/pdf/2212.10496)
  - [SAIL: Search-Augmented Instruction Learning](https://arxiv.org/pdf/2305.15225)
  - [Query Rewriting for Retrieval-Augmented Large Language Models](https://arxiv.org/pdf/2305.14283)
  - [RECOMP: IMPROVING RETRIEVAL-AUGMENTED LMs WITH COMPRESSION AND SELECTIVE AUGMENTATION](https://arxiv.org/pdf/2310.04408)

## 前提条件

在配置 `config.yaml` 文件之前，请确保具备以下条件：

- **OpenAI API 密钥**：用于访问 OpenAI 服务。
- **Tavily 搜索引擎 API 密钥**：用于使用 Tavily 搜索引擎进行网络搜索。
- **本地知识库设置**：如果使用本地知识库，请确保 KB 路径和嵌入模型已正确设置。
- **适当的环境**：确保系统具备必要的资源（CPU、CUDA、MPS 等）并已安装所需的依赖项。

## 安装指南

### 环境初始化

使用 Conda 创建一个新的虚拟环境并安装必要的 Python 版本：

```bash
conda create -n new_env python=3.10
```

激活环境：

```bash
conda activate new_env
```

### 安装依赖

根据 `requirements.txt` 安装所需依赖项：

```bash
pip install -r requirements.txt
```

### 下载模型

进入 `models` 目录并克隆所需的模型仓库：

```bash
cd models
git clone https://www.modelscope.cn/maidalun/bce-embedding-base_v1.git
git clone https://www.modelscope.cn/maidalun/bce-reranker-base_v1.git
```

### 配置 `config.yaml`

在项目根目录下创建并配置 `config.yaml` 文件。参考以下步骤：

1. **创建并打开配置文件**：

   使用你喜欢的文本编辑器创建并打开 `config.yaml`。

2. **填写 API 密钥**：

   - 将 `"YOUR OPENAI_API_KEY"` 替换为你的实际 OpenAI API 密钥。
   - 将 `"YOUR TAVILY_API_KEY"` 替换为你的 Tavily 搜索引擎 API 密钥。

3. **设置基础 URL**：

   - 将 `"YOUR OPENAI_BASE_URL"` 替换为相应的 OpenAI API 基础 URL。

4. **指定模型**：

   - 将 `"model"` 字段设置为你打算使用的具体语言模型（例如，`gpt-4`，`gpt-3.5-turbo`）。

5. **本地知识库设置**：

   - 如果使用本地知识库，请提供 `"kb_path"`，`"embedding_model"` 和 `"reranker_model"`。
   - 设置检索模型检索数 `k` 和重排模型保留数 `top_n`，以及文档大小 `chunk_size` 和重合度 `chunk_overlap`。
   - 确保 `"device"` 设置为你的硬件（例如，`cuda`，`cpu`，`mps`）。

6. **调整并发**：

   - 根据系统能力设置每个部分的 `"max_workers"`，以优化性能。

### 保存配置

填写完所有必要字段后，保存 `config.yaml` 文件。

## 配置文件说明

### 配置结构

`config.yaml` 文件分为四个主要部分：

1. [初始分析](#初始分析)
2. [网络搜索](#网络搜索)
3. [本地知识库 (KB)](#本地知识库-kb)
4. [综合回答](#综合回答)

#### 初始分析

```yaml
initial_analysis:
  api_key: "YOUR OPENAI_API_KEY"
  base_url: "YOUR OPENAI_BASE_URL"
  model: "model"
```

**说明**：  
此部分配置初始分析阶段的设置，系统将在此阶段使用 OpenAI 的语言模型处理输入数据。

#### 网络搜索

```yaml
web_search:
  api_key: "YOUR OPENAI_API_KEY"
  base_url: "YOUR OPENAI_BASE_URL"
  model: "model"
  search_engine: "tavily"
  search_api_key: "YOUR TAVILY_API_KEY"
  web_num: 5
  max_length: "MAX LENGTH OF WEB DOCUMENT"
  max_workers: "THE MAX CONCURRENCY NUM OF WEB SEARCH AND REFINE"
```

**说明**：  
此部分管理使用 Tavily 搜索引擎执行网络搜索并处理检索到的网页文档的配置。

#### 本地知识库 (KB)

```yaml
local_kb:
  api_key: "YOUR OPENAI_API_KEY"
  base_url: "YOUR OPENAI_BASE_URL"
  model: "model"
  kb_path: ""
  embedding_model: ""
  reranker_model: ""
  k: 100
  top_n: 5
  chunk_size: 1200
  chunk_overlap: 200
  device: "YOUR DEVICE CUDA/CPU/MPS..."
  max_workers: "THE MAX CONCURRENCY NUM OF HY_DOC GENERATE AND REFINE"
```

**说明**：  
此部分处理与本地知识库交互的设置，包括嵌入和重新排序模型、数据分块以及并发管理。

#### 综合回答

```yaml
comprehensive_answer:
  api_key: "YOUR OPENAI_API_KEY"
  base_url: "YOUR OPENAI_BASE_URL"
  model: "model"
  max_workers: "THE MAX CONCURRENCY NUM OF COMPOSE"
```

**说明**：  
此部分配置生成综合回答的参数，通过组合来自不同来源的信息来生成最终回答。

### 参数说明

#### API 密钥和基础 URL

- **api_key**：用于访问 OpenAI 服务的 API 密钥。
- **search_api_key**：用于 Tavily 搜索引擎的 API 密钥。
- **base_url**：各自 API 的基础 URL（OpenAI 或 Tavily）。

#### 模型配置

- **model**：具体使用的语言模型（例如，`gpt-4`，`gpt-3.5-turbo`）。

#### 并发设置

- **max_workers**：确定任务（如网络搜索、文档精炼和回答组合）的最大并发线程或进程数。根据系统的 CPU 和内存资源进行调整。

#### 其他参数

- **search_engine**：指定要使用的搜索引擎，例如 `"tavily"`。
- **web_num**：搜索过程中检索的网页文档数量。
- **max_length**：每个网页文档的最大长度。
- **kb_path**：本地知识库文件的路径。
- **embedding_model**：用于生成 KB 条目嵌入的模型。
- **reranker_model**：用于重新排序检索到的 KB 条目的模型。
- **k**：从知识库中考虑的顶级条目数量。
- **top_n**：重排后返回的顶级结果数量。
- **chunk_size**：处理大文档时每个数据块的大小。
- **chunk_overlap**：数据块之间的重叠量，以确保上下文的连贯性。
- **device**：用于计算的硬件设备（`CUDA`，`CPU`，`MPS` 等）。

## 示例用法

以下是你填写后的 `config.yaml` 可能的示例：

```yaml
initial_analysis:
  api_key: "sk-YourOpenAIKeyHere"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o"

web_search:
  api_key: "sk-YourOpenAIKeyHere"
  base_url: "https://api.openai.com/v1"
  model: "gpt-3.5-turbo"
  search_engine: "tavily"
  search_api_key: "YourTavilyAPIKeyHere"
  web_num: 5
  max_length: 2048
  max_workers: 10

local_kb:
  api_key: "sk-YourOpenAIKeyHere"
  base_url: "https://api.openai.com/v1"
  model: "gpt-3.5-turbo"
  kb_path: "/path/to/your/kb"
  embedding_model: "models/bce-embedding-base_v1"
  reranker_model: "models/bce-reranker-base_v1"
  k: 100
  top_n: 5
  chunk_size: 1200
  chunk_overlap: 200
  device: "cpu"
  max_workers: 8

comprehensive_answer:
  api_key: "sk-YourOpenAIKeyHere"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o"
  max_workers: 5
```

## 示例操作

### 一键成文

执行以下命令，启动生成过程：

```bash
python main.py
```

### 交互页面

启动 Web 交互界面：

```bash
streamlit run web.py
```

## 故障排除

- **API 密钥无效**：确保所有 API 密钥正确且具有必要的权限。
- **连接问题**：验证 `base_url` 的值是否正确，并确保网络允许对这些 URL 的外部请求。
- **资源限制**：如果遇到性能问题，可以考虑调整 `max_workers` 参数以更好地适应系统能力。
- **模型兼容性**：确保指定的模型可用且与你的 API 订阅兼容。
- **检索模型和重排模型**：当前版本只支持bce模型，确保你使用的是正确的bce模型。

## 许可协议

本项目采用 [MIT 许可](LICENSE) 进行许可。

---

如需进一步帮助，请联系 [huangkywork@163.com](mailto:huangkywork@163.com)。