# EditorialAgents

Target:
  - Input: 某个topic（自然科学、医学、人文社科等），和相关description、problem
  - Progress: 分解问题、联网搜索、本地知识库搜索、综合回答
  - Output: 完整的Science Article

Agents:
  - 问题初步分析agent（gpt4o）
    - 分析问题、给出框架
    - Reference: https://arxiv.org/pdf/2212.10496
  - 网络检索agent（gpt4o）
    - tavily关键词检索文档
    - 给检索到的文档生成总结
  - 本地知识库检索agent（gpt4o）
    - 生成假设性文档
    - 使用假设性文档检索
    - 给检索到的文档生成总结
  - 综合回答agent（gpt4o）
    - 根据所有检索文档和整体框架，分段落地完成写作

初始化环境
```bash
conda create -n new_env python=3.10
pip install -r requirements.txt
```

下载模型
```bash
cd models
git clone https://www.modelscope.cn/maidalun/bce-embedding-base_v1.git
git clone https://www.modelscope.cn/maidalun/bce-reranker-base_v1.git
```

配置 config/config.yaml

一键成文
```bash
python main.py
```

交互页面
```bash
streamlit run web.py
```