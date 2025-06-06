# 引言和总结生成功能

## 功能概述

本次更新为Deep Search Agent项目添加了智能引言和总结生成功能。该功能改变了原有的工作流程：

**原有流程**：
1. 生成大纲
2. 对所有章节（包括引言和总结）进行检索
3. 生成所有章节内容
4. 合并文章

**新流程**：
1. 生成大纲
2. 对主体章节进行检索（跳过引言和总结）
3. 生成主体章节内容
4. 基于已生成的主体内容生成引言和总结
5. 合并文章

## 主要改动

### 1. 新增 IntroductionConclusionAgent

**文件位置**: `agents/intro_conclusion_agent.py`

**主要功能**：
- 基于已生成的主体内容智能生成引言
- 基于已生成的主体内容智能生成总结
- 提供节点跳过判断功能，用于识别引言和总结节点

**核心方法**：
- `generate_introduction_and_conclusion()`: 生成引言和总结的主方法
- `should_skip_retrieval()`: 判断节点是否应该跳过检索
- `_extract_main_content()`: 提取主体内容（排除引言和总结）
- `_find_node_by_keywords()`: 根据关键词查找节点

### 2. 更新提示词模板

**文件位置**: `agents/prompts.py`

**新增提示词**：
- `generate_introduction`: 引言生成提示词
- `generate_conclusion`: 总结生成提示词

**提示词特点**：
- 基于文章主题、描述、大纲和主体内容生成
- 遵循学术写作规范
- 确保与主体内容的一致性和连贯性

### 3. 修改主处理链

**文件位置**: `chains/main_chain.py`

**主要改动**：
- 集成新的 IntroductionConclusionAgent
- 修改检索流程，添加跳过函数参数
- 修改内容生成流程，添加跳过函数参数
- 在主体内容生成完成后调用引言和总结生成

### 4. 增强检索和生成代理

**UnifiedRetrievalAgent** (`agents/unified_retrieval_agent.py`)：
- 添加 `skip_function` 参数支持
- 增加兼容性处理，支持可选的 process_id 和 status_manager
- 自动过滤需要跳过的节点

**ComprehensiveAnswerAgent** (`agents/comprehensive_answer_agent.py`)：
- 添加 `skip_function` 参数支持
- 在内容生成时自动跳过指定节点

### 5. 配置文件更新

**文件位置**: `config/config_example.yaml`

**新增配置**：
```yaml
intro_conclusion:
  api_key: "YOUR_OPENAI_API_KEY"
  base_url: "YOUR_OPENAI_BASE_URL"
  model: "gpt-4o"
```

## 支持的关键词

系统会自动识别以下关键词作为引言和总结节点：

**引言关键词**：
- 引言
- introduction
- 前言
- 导言

**总结关键词**：
- 总结
- conclusion
- 结论
- 小结
- 结语

## 使用方法

### 1. 配置设置

确保在配置文件中添加了 `intro_conclusion` 部分的配置。

### 2. 代码调用

```python
from chains.main_chain import ScienceArticleChain

# 加载配置
config = load_your_config()

# 创建处理链
chain = ScienceArticleChain(config)

# 运行处理流程
result = chain.run(
    topic="你的文章主题",
    description="文章描述",
    problem="要解决的问题"
)
```

### 3. 测试功能

运行测试脚本验证功能：

```bash
python test_intro_conclusion.py
```

## 技术特点

### 1. 智能内容感知
- 引言和总结的生成基于实际的主体内容
- 确保内容的一致性和连贯性
- 避免与主体内容的重复

### 2. 灵活的节点识别
- 支持中英文关键词识别
- 大小写不敏感
- 可扩展的关键词列表

### 3. 向后兼容
- 保持与现有API的兼容性
- 可选的跳过函数参数
- 渐进式功能集成

### 4. 错误处理
- 完善的异常处理机制
- 详细的日志记录
- 优雅的降级处理

## 生成质量

### 引言特点
- 提供充分的背景信息
- 明确研究目标和意义
- 概述文章结构
- 引导读者进入主题

### 总结特点
- 概括主要发现和结论
- 分析理论和实践意义
- 讨论局限性
- 提出未来展望
- 提供行动指导

## 性能优化

- 并行处理主体章节
- 串行生成引言和总结（确保基于完整内容）
- 智能内容提取和过滤
- 高效的节点查找算法

## 注意事项

1. **节点命名**：确保引言和总结节点使用支持的关键词命名
2. **内容依赖**：引言和总结的质量依赖于主体内容的质量
3. **配置完整**：确保所有必要的API配置都已正确设置
4. **模型选择**：建议使用较强的语言模型以获得更好的生成效果

## 未来扩展

- 支持更多语言的关键词识别
- 添加自定义引言和总结模板
- 支持多种写作风格
- 集成更多的内容分析功能