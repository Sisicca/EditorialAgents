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
            api_key=config['api_key'] or os.environ["OPENAI_API_KEY"],
            base_url=config['base_url'] or os.environ["OPENAI_BASE_URL"],
            model=config['model'],
        )
        # 设置最大线程数，可以根据实际情况调整
        self.max_workers = config['max_workers']
        
        # 预构建处理链以提高性能
        try:
            # 移除不再需要的compose_single_paragraph_chain
            # 只保留用于非叶子节点的处理链
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
            self.compose_with_subparagraphs_chain = None
            self.compose_entire_article_chain = None

    def _compose_single(self, node: dict, framework: ArticleOutline):
        try:
            outline = framework.generate_paper_structure()
            title = node['title']
            summary = node['summary']
            
            # 判断节点类型
            if node['level'] == 1:
                # 顶层节点处理 - 生成完整文章
                title = f"《{title}》"
                summary = ""
                compose_chain = self.compose_entire_article_chain
                # 使用所有子节点的内容作为文档
                documents = [child.get('content', '') for child in node.get('children', [])]
            elif not node.get('children'):
                # 叶子节点处理 - 跳过，因为内容已由迭代检索生成
                # 直接使用现有content，如果没有则保持空字符串
                logger.info(f"跳过叶子节点 '{title}' 的内容合成，使用迭代检索生成的内容。")
                return
            else:
                # 非叶子节点处理 - 使用子节点内容合成
                documents = [child.get('content', '') for child in node.get('children', [])]
                compose_chain = self.compose_with_subparagraphs_chain
            
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

    def compose(self, framework: ArticleOutline, skip_function=None) -> ArticleOutline:
        """为文章大纲中的每个节点生成综合性内容，使用多线程优化
        
        Args:
            framework: 文章框架对象
            skip_function: 可选的跳过函数，用于判断是否跳过某个节点的内容生成
        """
        curr_level = framework.find_max_level()
        logger.info(f"文章大纲的最大层级为: {curr_level}")
        
        while curr_level >= 1:
            curr_nodes = framework.find_level_n_nodes(level_n=curr_level)
            
            # 如果提供了skip_function，过滤掉需要跳过的节点
            if skip_function:
                original_count = len(curr_nodes)
                curr_nodes = [node for node in curr_nodes if not skip_function(node)]
                skipped_count = original_count - len(curr_nodes)
                logger.info(f"层级 {curr_level}: 跳过了 {skipped_count} 个节点（引言/总结），剩余 {len(curr_nodes)} 个节点需要生成内容")
            else:
                logger.info(f"处理层级 {curr_level}，共有 {len(curr_nodes)} 个节点。")
            
            num_nodes = len(curr_nodes)
            
            # 如果当前层级没有需要处理的节点，跳过
            if num_nodes == 0:
                curr_level -= 1
                continue
            
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