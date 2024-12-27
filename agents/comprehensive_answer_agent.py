from typing import Any, Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from agents.prompts import PROMPTS
from agents.initial_analysis_agent import ArticleOutline
from pprint import pprint
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveAnswerAgent:
    def __init__(self, config):
        self.llm = ChatOpenAI(
            api_key=config['api_key'],
            base_url=config['base_url'],
            model=config['model'],
        )
        # 设置最大线程数，可以根据实际情况调整
        self.max_workers = config['max_workers']
        
        # 预构建处理链以提高性能
        # try:
        #     compose_template = PromptTemplate(
        #         input_variables=['outline', 'title', 'summary', 'documents'],
        #         template=PROMPTS['compose']
        #     )
        #     self.compose_chain = compose_template | self.llm | StrOutputParser()
        # except Exception as e:
        #     logger.error(f"预构建 Compose 处理链失败: {e}")
        #     self.compose_chain = None
            
        try:
            compose_single_paragraph_template = PromptTemplate(
                input_variables=['outline', 'title', 'summary', 'documents'],
                template=PROMPTS['compose_single_paragraph']
            )
            self.compose_single_paragraph_chain = compose_single_paragraph_template | self.llm | StrOutputParser()

            compose_with_subparagraphs_template = PromptTemplate(
                input_variables=['outline', 'title', 'summary', 'documents'],
                template=PROMPTS['compose_with_subparagraphs']
            )
            self.compose_with_subparagraphs_chain = compose_with_subparagraphs_template | self.llm | StrOutputParser()

            compose_entire_article_template = PromptTemplate(
                input_variables=['outline', 'title', 'summary', 'documents'],
                template=PROMPTS['compose_entire_article']
            )
            self.compose_entire_article_chain = compose_entire_article_template | self.llm | StrOutputParser()               
        except Exception as e:
            logger.error(f"预构建 Compose 处理链失败: {e}")
            self.compose_single_paragraph_chain = None
            self.compose_with_subparagraphs_chain = None
            self.compose_entire_article_chain = None

    def _compose_single(self, node: dict, framework: ArticleOutline):
        try:
            outline = framework.generate_paper_structure()
            title = node['title']
            summary = node['summary']
            
            # 判断是否为叶子节点
            if not node.get('children'):
                documents = node.get('web_docs_refined', []) + node.get('kb_docs_refined', [])
                compose_chain = self.compose_single_paragraph_chain
            else:
                # 如果有子节点，假设子节点有 'content' 字段
                documents = [child.get('content', '') for child in node.get('children', [])]
                compose_chain = self.compose_with_subparagraphs_chain
            
            if node['level'] == 1:
                title = f"《{title}》"
                summary = ""
                compose_chain = self.compose_entire_article_chain
            
            # 调用Compose链生成内容
            content = compose_chain.invoke(
                {
                    'outline': outline,
                    'title': title,
                    'summary': summary,
                    'documents': documents
                }
            )
            node['content'] = content
            logger.info(f"节点 '{title}' 的内容已生成。")
        except Exception as e:
            logger.error(f"生成节点内容失败 (标题: {node.get('title', 'Unknown')}): {e}")
            node['content'] = ""

    def compose(self, framework: ArticleOutline) -> ArticleOutline:
        """为文章大纲中的每个节点生成综合性内容，使用多线程优化"""
        curr_level = framework.find_max_level()
        logger.info(f"文章大纲的最大层级为: {curr_level}")
        
        while curr_level >= 1:
            curr_nodes = framework.find_level_n_nodes(level_n=curr_level)
            num_nodes = len(curr_nodes)
            logger.info(f"处理层级 {curr_level}，共有 {num_nodes} 个节点。")
            
            # 使用 ThreadPoolExecutor 来并发处理节点
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 提交所有节点的处理任务
                future_to_node = {
                    executor.submit(self._compose_single, node, framework): node for node in curr_nodes
                }
                
                # 使用 tqdm 显示进度条
                for future in tqdm(as_completed(future_to_node), total=num_nodes, desc=f"处理层级 {curr_level}"):
                    node = future_to_node[future]
                    try:
                        future.result()  # 触发异常捕获
                    except Exception as e:
                        logger.error(f"节点 '{node.get('title', 'Unknown')}' 处理失败: {e}")
            
            # 处理下一层级
            curr_level -= 1
        
        logger.info("所有层级的节点内容生成完成。")
        return framework