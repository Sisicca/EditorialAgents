# EditorialAgents

Target:
  - Input: 某个topic（自然科学、医学、人文社科等），和相关description、problem
  - Progress: 分解问题、联网搜索、本地知识库搜索、综合回答
  - Output: 完整的Science Article

Agents:
  - 问题初步分析agent（gpt4o）
    - 分析问题、给出框架、提出主题/关键词、给出假设性文档
    - Reference: https://arxiv.org/pdf/2212.10496
  - 网络检索agent（gpt4o）
    - tavily关键词检索文档
    - 使用假设性文档匹配联网检索到的文档
    - 给检索到的文档生成总结
  - 本地知识库检索agent（gpt4o）
    - 假设性文档匹配
    - 给检索到的文档生成总结
  - 综合回答agent（gpt4o）
    - 根据所有检索文档和整体框架，完成写作