from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from agents.prompts import PROMPTS
from agents.initial_analysis_agent import ArticleOutline
from tavily import TavilyClient
from typing import List
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSearchAgent:
    def __init__(self, config):
        self.llm = ChatOpenAI(api_key=config['api_key'],
                              base_url=config['base_url'],
                              model=config['model'])
        self.web_num = config['web_num']
        # 设置最大线程数，可以根据实际情况调整
        self.max_workers = config['max_workers']
        self.max_length = config['max_length']
        
        if config['search_engine'] == 'tavily':
            self.search_client = TavilyClient(api_key=config['search_api_key'])
        else:
            raise ImportError("'search_engine' must be 'tavily'.")
        
    def _search_docs(self, title: str, summary: str) -> List[str]:
        try:
            raw_results = self.search_client.search(
                query=f"{title} {summary}",
                max_results=self.web_num,
                include_answer=False,
                include_raw_content=True
            )
            # 每篇最多不超过 max_length 字
            return [result['raw_content'][:self.max_length] for result in raw_results['results'] if result.get('raw_content')]
        except Exception as e:
            logger.error(f"搜索文档失败: {e}")
            return []
    
    def _refine_doc(self, doc: str, title: str, summary: str) -> str:
        try:
            refine_template = PromptTemplate(
                input_variables=['title', 'summary', 'document'],
                template=PROMPTS['refine_doc']
            )
            
            refine_chain = refine_template | self.llm | StrOutputParser()
            
            refine_result = refine_chain.invoke(
                {
                    'title': title,
                    'summary': summary,
                    'document': doc
                }
            )
            return refine_result
        except Exception as e:
            logger.error(f"精炼文档失败: {e}")
            return ""
    
    def search_for_leaf_nodes(self, framework: ArticleOutline) -> ArticleOutline:
        leaf_nodes = framework.find_leaf_nodes()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 并发执行搜索任务
            search_futures = {
                executor.submit(self._search_docs, node['title'], node['summary']): node
                for node in leaf_nodes
            }
            with tqdm(total=len(search_futures), desc="为叶子节点检索网络文档") as pbar:
                for future in as_completed(search_futures):
                    node = search_futures[future]
                    try:
                        web_docs = future.result()
                        node['web_docs'] = web_docs
                    except Exception as e:
                        logger.error(f"搜索节点 '{node['title']}' 失败: {e}")
                        node['web_docs'] = []
                    
                    pbar.update(1)
            
            # 并发执行精炼任务
            refine_futures = {
                executor.submit(self._refine_doc, doc, node['title'], node['summary']): (node, doc)
                for node in leaf_nodes
                for doc in node.get('web_docs', [])
            }
            
            # 初始化 web_docs_refined
            for node in leaf_nodes:
                node['web_docs_refined'] = []
            
            with tqdm(total=len(refine_futures), desc="对网络文档进行精炼") as pbar:
                for future in as_completed(refine_futures):
                    node, doc = refine_futures[future]
                    try:
                        refined_doc = future.result()
                        if refined_doc:
                            node['web_docs_refined'].append(refined_doc)
                    except Exception as e:
                        logger.error(f"精炼节点 '{node['title']}' 的文档失败: {e}")
                
                pbar.update(1)
        
        return framework
