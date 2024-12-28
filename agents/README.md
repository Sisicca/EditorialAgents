# EditorialAgents - 核心模块

**EditorialAgents** 是一个自动化框架，旨在生成涵盖自然科学、医学和社会科学等各个学科的综合性科学文章。该系统利用先进的语言模型、网络搜索功能和本地知识库，生成结构良好且高质量的学术论文。

## 目录

- [EditorialAgents - 核心模块](#editorialagents---核心模块)
  - [目录](#目录)
  - [概述](#概述)
  - [核心模块](#核心模块)
    - [`initial_analysis_agent.py`](#initial_analysis_agentpy)
    - [`web_search_agent.py`](#web_search_agentpy)
    - [`local_kb_agent.py`](#local_kb_agentpy)
    - [`comprehensive_answer_agent.py`](#comprehensive_answer_agentpy)
    - [`prompts.py`](#promptspy)
  - [系统工作流程](#系统工作流程)
  - [许可](#许可)

## 概述

**EditorialAgents** 通过以下步骤自动化科学文章的生成过程：

1. **生成文章大纲**：将主题分解为结构化的大纲。
2. **进行网络搜索**：从互联网检索相关信息。
3. **利用本地知识库**：访问并优化来自预先存在的本地资源的信息。
4. **撰写综合内容**：将所有收集到的信息综合成连贯且全面的文章。

该系统是模块化设计，每个核心组件处理文章生成过程的特定方面。此设计确保了灵活性、可扩展性和易于维护。

## 核心模块

### `initial_analysis_agent.py`

**目的**：  
根据提供的主题、描述和问题陈述生成科学文章的初始大纲。

**主要组件**：

- **`ArticleOutline` 类**：
  - **初始化**：接受一个表示文章大纲的嵌套字典。
  - **`generate_paper_structure` 方法**：遍历大纲以生成格式化的论文结构。
  - **`check_outline_structure` 方法**：验证大纲的结构完整性。
  - **`find_leaf_nodes` 方法**：识别没有子部分的节点（叶节点）。
  - **`find_max_level` 方法**：确定大纲中标题的最深层级。
  - **`find_level_n_nodes` 方法**：检索特定标题层级的所有节点。

- **`InitialAnalysisAgent` 类**：
  - **初始化**：使用 API 凭证和选定的模型配置与 OpenAI GPT 模型的连接。
  - **`get_framework` 方法**：利用提示模板与 GPT 交互，根据用户输入生成嵌套的 JSON 大纲。

**使用方法**：
生成论文的层级结构，确保主题的逻辑流畅和全面涵盖。

### `web_search_agent.py`

**目的**：  
执行网络搜索，为文章大纲中的每个叶节点收集相关文档，优化检索到的信息以整合到最终文章中。

**主要组件**：

- **`WebSearchAgent` 类**：
  - **初始化**：使用提供的 API 密钥和配置参数，设置与 OpenAI GPT 模型和 Tavily 搜索引擎的连接。
  - **`_search_docs` 方法**：根据节点标题和摘要执行网络搜索，检索指定数量的文档，同时遵守长度限制。
  - **`_refine_doc` 方法**：使用 GPT 优化检索到的文档内容，确保相关性和简洁性。
  - **`search_for_leaf_nodes` 方法**：协调所有叶节点的搜索和优化过程，更新每个节点的优化后网络文档。

**使用方法**：
通过从互联网获取最新和相关的信息增强论文的每个部分，确保内容全面且权威。

### `local_kb_agent.py`

**目的**：  
与本地知识库交互，检索和优化与文章每个部分相关的信息，补充网络获取的数据。

**主要组件**：

- **辅助函数**：
  - **`_list_files_in_directory`**：列出指定目录中的所有文件。
  - **`_file2docs`**：根据文件类型和指定参数加载并拆分文档为可管理的块。

- **`LocalKBAgent` 类**：
  - **初始化**：配置与本地知识库交互的路径、模型和参数。
  - **`_create_retriever` 方法**：加载文档，生成嵌入，并设置基于 FAISS 的向量存储以实现高效检索。
  - **`_generate_hypothetical_doc` 方法**：使用 GPT 创建假设文档以指导检索过程。
  - **`_search_docs` 方法**：基于假设文档从本地知识库中检索相关文档。
  - **`_refine_doc` 方法**：优化检索到的文档，确保其适合纳入文章。
  - **`search_for_leaf_nodes` 方法**：管理所有叶节点的假设文档生成、文档检索和本地知识库文档优化过程。

**使用方法**：
通过来自可信本地来源的深入信息增强文章，确保内容准确且全面。

### `comprehensive_answer_agent.py`

**目的**：  
通过综合网络搜索和本地知识库的信息，生成科学文章的最终综合内容。

**主要组件**：

- **`ComprehensiveAnswerAgent` 类**：
  - **初始化**：配置与 OpenAI GPT 模型的连接，并准备各种撰写任务的提示模板。
  - **`_compose_single` 方法**：为单个节点生成内容，根据节点层级选择适当的撰写链。
  - **`compose` 方法**：迭代地为大纲的每个部分生成内容，从最深层级开始，向上推进，利用多线程提高效率。

**使用方法**：
将结构化的大纲和整理后的内容转化为撰写良好、连贯的科学文章各部分，确保整篇文档的一致性和学术严谨性。

### `prompts.py`

**目的**：  
定义各种提示模板，供不同的代理使用，以指导内容的生成、优化和撰写。

**主要组件**：

- **`PROMPTS` 字典**：
  - **`initial_analysis_agent`**：用于生成文章大纲的模板。
  - **`refine_doc`**：用于优化检索到的文档，确保相关性和简洁性的模板。
  - **`hypothetical_doc`**：根据标题和摘要生成假设文档以指导知识库搜索的模板。
  - **`compose_single_paragraph`**：根据大纲和优化后文档撰写单个段落的模板。
  - **`compose_with_subparagraphs`**：撰写包含子部分的段落的模板，确保逻辑流畅和连贯性。
  - **`compose_entire_article`**：根据所有撰写的部分组装完整文章的模板。

**使用方法**：
为 GPT 模型提供结构化的指导，确保生成的内容符合所需的格式、风格和学术标准。

## 系统工作流程

**EditorialAgents** 系统通过以下顺序步骤运行：

1. **初步分析**：
   - **输入**：用户提供一个主题、描述和问题陈述。
   - **过程**：`InitialAnalysisAgent` 使用 GPT 生成一个嵌套的 JSON 大纲，表示科学文章的结构。
   - **输出**：包含论文层级结构的已验证 `ArticleOutline` 对象。

2. **网络搜索**：
   - **过程**：`WebSearchAgent` 识别大纲中的所有叶节点，并使用 Tavily 搜索引擎并行执行网络搜索。
   - **子过程**：
     - 为每个叶节点检索相关文档。
     - 使用 GPT 优化检索到的文档，确保相关性和简洁性。
   - **输出**：每个叶节点更新了优化后的网络文档 (`web_docs_refined`)。

3. **本地知识库搜索**：
   - **过程**：`LocalKBAgent` 与本地知识库交互，为每个叶节点检索额外信息。
   - **子过程**：
     - 根据节点标题和摘要生成假设文档。
     - 使用假设文档搜索本地知识库。
     - 使用 GPT 优化检索到的知识库文档。
   - **输出**：每个叶节点更新了优化后的知识库文档 (`kb_docs_refined`)。

4. **综合答案生成**：
   - **过程**：`ComprehensiveAnswerAgent` 综合所有收集到的信息，为文章的每个部分撰写详细内容。
   - **子过程**：
     - 从最深层级开始为每个节点生成内容，确保子部分在父部分之前完成。
     - 利用多线程优化撰写过程。
   - **输出**：一个包含详细内容的完整 `ArticleOutline` 对象，准备进行最终组装。

5. **最终组装**：
   - 系统整合所有撰写的部分，组装完整的科学文章，确保逻辑流畅和学术完整性。

## 许可

本项目采用 [MIT 许可](LICENSE)。

---

如需进一步的帮助或有任何疑问，请联系 [huangkywork@163.com](mailto:huangkywork@163.com)。