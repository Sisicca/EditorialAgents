import asyncio
import json
import os
import time
import uuid
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

from loguru import logger
from openai import OpenAI

from agents.web_search_agent import WebSearchAgent
from agents.local_kb_agent import LocalKBAgent
from agents.prompts import PROMPTS
from web_api.models_api import LeafNodeStatusUpdate, DocumentPreview

# Attempt to import the status manager instance
# This will be part of the FastAPI app, so direct import might be tricky
# For now, we'll assume it's passed in or globally available in the FastAPI context.
# from web_api.services.status_manager import status_manager_instance, LeafNodeStatusUpdate
# Placeholder for actual import or injection strategy
# Global placeholder, to be properly managed by FastAPI app structure
# This is NOT a good practice for standalone modules but helps illustrate the integration point.
# In a real FastAPI app, this would be injected or accessed via a shared context.
# For the purpose of this focused edit, we will assume it's passed as an argument.

class Document:
    """统一的文档表示类，用于网络和本地知识库检索"""
    def __init__(self, content: str, source: str, query: str, metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.source = source  # 'web' 或 'kb'
        self.query = query
        self.metadata = metadata or {}
        
        # 生成唯一标识符
        if source == 'web':
            self.id = self.metadata.get('url', str(uuid.uuid4())[:8])
            self.citation_key = f"web_{hashlib.md5(self.id.encode()).hexdigest()[:6]}"
        else:  # source == 'kb'
            file_path = self.metadata.get('source', '')
            page = self.metadata.get('page', 0)
            self.id = f"{file_path}:{page}"
            file_name = os.path.basename(file_path) if file_path else "unknown"
            self.citation_key = f"kb_{hashlib.md5(self.id.encode()).hexdigest()[:6]}"

    def to_dict(self):
        """将文档转换为字典表示"""
        return {
            "content": self.content,
            "source": self.source,
            "query": self.query,
            "metadata": self.metadata,
            "id": self.id,
            "citation_key": self.citation_key
        }
        

class UnifiedRetrievalAgent:
    """统一检索智能体，整合网络和本地知识库检索"""
    
    def __init__(self, web_config: Dict[str, Any], kb_config: Dict[str, Any]):
        """初始化统一检索智能体
        
        Args:
            web_config: 网络检索配置
            kb_config: 本地知识库配置
        """
        # 初始化网络和本地知识库检索工具
        self.web_search_agent = WebSearchAgent(web_config)
        self.local_kb_agent = LocalKBAgent(kb_config)
        
        # 配置参数
        self.max_iterations = web_config.get('max_iterations', 3)
        self.max_workers = web_config.get('max_workers', 4)
        self.web_concurrency = web_config.get('max_concurrency', 5)
        self.kb_concurrency = kb_config.get('max_concurrency', 2)
        self.similarity_threshold = web_config.get('similarity_threshold', 0.7)
        
        # 错误处理和重试配置
        self.max_retries = web_config.get('max_retries', 3)
        self.retry_delay = web_config.get('retry_delay', 1)
        
        # 初始化OpenAI客户端
        self.llm = OpenAI(
            api_key=web_config['api_key'],
            base_url=web_config['base_url']
        )
        self.model = web_config['model']
        
        # 初始化提示模板
        self.prompts = PROMPTS
    
    def iterative_retrieval_for_leaf_nodes(self, framework, process_id: str, status_manager: Any, use_web: bool = True, use_kb: bool = True):
        """对大纲的所有叶节点进行迭代检索
        
        Args:
            framework: 文章框架对象
            process_id: 当前处理流程的ID
            status_manager: 状态管理器实例
            use_web: 是否使用网络检索
            use_kb: 是否使用本地知识库检索
        """
        logger.info(f"PID-{process_id}: 开始对叶节点进行迭代检索. 使用网络: {use_web}, 使用知识库: {use_kb}")
        status_manager.update_overall_retrieval_message(process_id, f"Retrieval In Progress: Processing {framework.find_leaf_nodes().__len__()} leaf nodes.")
        
        # 获取所有叶节点
        leaf_nodes = framework.find_leaf_nodes()
        logger.info(f"PID-{process_id}: 找到 {len(leaf_nodes)} 个叶节点")
        
        # 使用线程池并发处理每个叶节点
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self._process_node, node, process_id, status_manager, use_web, use_kb) 
                      for node in leaf_nodes]
            
            for future in as_completed(futures):
                try:
                    future.result() # To catch exceptions from _process_node if any
                except Exception as e:
                    # Errors within _process_node should be handled and reported by _process_node itself.
                    # This catch is a fallback.
                    logger.error(f"PID-{process_id}: 处理叶节点时发生未捕获的严重错误: {str(e)}")
                    # status_manager.update_overall_retrieval_message(process_id, "Error during leaf node processing", error=str(e))
        
        logger.info(f"PID-{process_id}: 叶节点迭代检索完成或已处理所有节点。检查最终状态...")
        # Overall status (Completed / Completed with Errors) should be set by the last node update in status_manager
    
    def _get_node_display_id(self, node: Dict[str, Any]) -> str:
        # Helper to create a consistent ID for status reporting, can be enhanced
        return f"level{node.get('level', 'N')}-{node.get('title', 'Untitled').replace(' ', '_')[:30]}"

    def _process_node(self, node: Dict[str, Any], process_id: str, status_manager: Any, use_web: bool, use_kb: bool):
        """处理单个叶节点的迭代检索流程
        
        Args:
            node: 叶节点字典
            process_id: 当前处理流程的ID
            status_manager: 状态管理器实例
            use_web: 是否使用网络检索
            use_kb: 是否使用本地知识库检索
        """
        # from web_api.models_api import LeafNodeStatusUpdate # Moved here to avoid circular deps if file structure is flat
        # This import should ideally be at the top or managed by dependency injection.
        # For now, to make it runnable in isolation, assuming models_api is accessible.
        # A better way is to define LeafNodeStatusUpdate in a common models file if not already.
        # For this edit, assume status_manager methods accept dicts or specific update models.
        
        node_display_id = self._get_node_display_id(node)
        logger.info(f"PID-{process_id} Node-{node_display_id}: 开始处理")
        status_manager.update_leaf_node_status(process_id, node_display_id, LeafNodeStatusUpdate(status_message="Initializing node processing..."))

        # 初始化节点的检索历史和内容
        node['retrieval_history'] = []
        node['content'] = ""
        node['references'] = []
        
        # 生成初始检索语句
        logger.info(f"PID-{process_id} Node-{node_display_id}: 生成初始检索语句")
        status_manager.update_leaf_node_status(process_id, node_display_id, LeafNodeStatusUpdate(status_message="Generating initial search queries..."))
        initial_prompt = self.prompts['generate_initial_queries'].format(
            title=node['title'],
            summary=node['summary']
        )
        
        response = self._complete(initial_prompt, process_id, node_display_id)
        try:
            # 处理可能的markdown格式，去除```json和```
            response = self._clean_json_response(response)
            queries = json.loads(response)
            if not isinstance(queries, list):
                logger.warning(f"PID-{process_id} Node-{node_display_id}: 查询不是列表格式: {response}")
                queries = [node['title']]
        except json.JSONDecodeError as e:
            logger.warning(f"PID-{process_id} Node-{node_display_id}: 无法解析初始查询JSON: {response}，错误: {str(e)}")
            status_manager.update_leaf_node_status(process_id, node_display_id, LeafNodeStatusUpdate(error_message=f"Failed to parse initial queries: {str(e)}", is_completed=True))
            return # Stop processing this node
        
        all_used_queries = queries.copy()
        iteration = 0
        
        while iteration < self.max_iterations:
            current_iter_progress = f"{iteration + 1}/{self.max_iterations}"
            logger.info(f"PID-{process_id} Node-{node_display_id}: 第 {iteration+1} 次迭代检索")
            status_manager.update_leaf_node_status(process_id, node_display_id, 
                LeafNodeStatusUpdate(status_message=f"Iteration {current_iter_progress}: Starting searches...", 
                                 current_query=", ".join(queries), 
                                 iteration_progress=current_iter_progress)
            )
            
            # 执行检索
            try:
                results = self._execute_searches(queries, node, use_web, use_kb, process_id, node_display_id)
            except Exception as e:
                logger.error(f"PID-{process_id} Node-{node_display_id}: _execute_searches 失败: {str(e)}")
                status_manager.update_leaf_node_status(process_id, node_display_id, 
                    LeafNodeStatusUpdate(error_message=f"Search execution failed: {str(e)}", is_completed=True, iteration_progress=current_iter_progress)
                )
                return

            status_manager.update_leaf_node_status(process_id, node_display_id, 
                LeafNodeStatusUpdate(status_message=f"Iteration {current_iter_progress}: Processing {len(results)} search results...")
            )
            
            # 去重处理
            new_results = self._deduplicate(results, node['retrieval_history'])
            if not new_results:
                logger.info(f"PID-{process_id} Node-{node_display_id}: 无新结果，停止迭代")
                status_manager.update_leaf_node_status(process_id, node_display_id, 
                    LeafNodeStatusUpdate(status_message=f"Iteration {current_iter_progress}: No new unique documents found. Stopping iteration.", is_completed=True)
                )
                break  # 没有新结果，停止迭代
                
            # 更新检索历史
            node['retrieval_history'].extend(new_results)
            logger.info(f"PID-{process_id} Node-{node_display_id}: 获取到 {len(new_results)} 个新结果")
            
            # 生成 DocumentPreview 列表用于状态更新
            current_doc_previews = []
            if new_results: # 只在有新结果时更新文档预览
                for doc in new_results:
                    current_doc_previews.append(DocumentPreview(
                        id=doc.id,
                        citation_key=doc.citation_key,
                        title=doc.metadata.get('title', '未知标题'),
                        source=doc.source
                    ))
                status_manager.update_leaf_node_status(process_id, node_display_id,
                    LeafNodeStatusUpdate(retrieved_docs_preview=current_doc_previews)
                )
            
            # 格式化检索结果用于提示
            formatted_results = self._format_retrieval_results_for_prompt(new_results)
            
            # 更新节点内容
            logger.info(f"PID-{process_id} Node-{node_display_id}: 更新内容")
            status_manager.update_leaf_node_status(process_id, node_display_id, 
                LeafNodeStatusUpdate(status_message=f"Iteration {current_iter_progress}: Refining content with {len(new_results)} new documents...")
            )
            refine_prompt = self.prompts['refine_content_with_new_results'].format(
                title=node['title'],
                summary=node['summary'],
                current_content=node['content'],
                new_results=formatted_results
            )
            node['content'] = self._complete(refine_prompt, process_id, node_display_id)
            # 更新内容预览
            content_preview_text = (node['content'][:200] + '...') if node['content'] else "内容尚未生成"
            status_manager.update_leaf_node_status(process_id, node_display_id,
                LeafNodeStatusUpdate(content_preview=content_preview_text)
            )
            
            # 更新引用列表
            self._update_references(node, new_results)
            
            # 如果已达到最大迭代次数，停止
            if iteration >= self.max_iterations - 1:
                logger.info(f"PID-{process_id} Node-{node_display_id}: 达到最大迭代次数 {self.max_iterations}")
                status_manager.update_leaf_node_status(process_id, node_display_id, 
                    LeafNodeStatusUpdate(status_message=f"Max iterations ({self.max_iterations}) reached.", is_completed=True, iteration_progress=current_iter_progress)
                )
                break
                
            # 判断是否需要继续检索
            logger.info(f"PID-{process_id} Node-{node_display_id}: 判断是否需要继续检索")
            status_manager.update_leaf_node_status(process_id, node_display_id, 
                LeafNodeStatusUpdate(status_message=f"Iteration {current_iter_progress}: Evaluating content and generating next queries...")
            )
            evaluate_prompt = self.prompts['evaluate_and_generate_new_queries'].format(
                title=node['title'],
                summary=node['summary'],
                current_content=node['content'],
                previous_queries=self._format_previous_queries(all_used_queries)
            )
            
            response = self._complete(evaluate_prompt, process_id, node_display_id)
            
            # 检查是否完成检索
            if "[RETRIEVAL_COMPLETE]" in response:
                logger.info(f"PID-{process_id} Node-{node_display_id}: 检索完成")
                status_manager.update_leaf_node_status(process_id, node_display_id, 
                    LeafNodeStatusUpdate(status_message="Retrieval marked complete by LLM.", is_completed=True, iteration_progress=current_iter_progress)
                )
                break
                
            # 否则获取新查询
            try:
                # 处理可能的markdown格式
                response = self._clean_json_response(response)
                # 尝试从可能包含额外文本的响应中提取JSON
                start_idx = response.find('[')
                end_idx = response.rfind(']') + 1
                if start_idx >= 0 and end_idx > 0:
                    json_str = response[start_idx:end_idx]
                    queries = json.loads(json_str)
                    if isinstance(queries, list):
                        all_used_queries.extend(queries)
                    else:
                        logger.warning(f"PID-{process_id} Node-{node_display_id}: 解析的新查询JSON不是列表: {json_str}")
                        status_manager.update_leaf_node_status(process_id, node_display_id, 
                            LeafNodeStatusUpdate(status_message="Failed to parse new queries (not a list). Stopping.", is_completed=True, iteration_progress=current_iter_progress)
                        )
                        break
                else:
                    logger.warning(f"PID-{process_id} Node-{node_display_id}: 无法在响应中找到新查询JSON: {response}")
                    status_manager.update_leaf_node_status(process_id, node_display_id, 
                        LeafNodeStatusUpdate(status_message="No new queries found in LLM response. Stopping.", is_completed=True, iteration_progress=current_iter_progress)
                    )
                    break
            except Exception as e:
                logger.warning(f"PID-{process_id} Node-{node_display_id}: 处理模型响应生成新查询时出错: {str(e)}")
                status_manager.update_leaf_node_status(process_id, node_display_id, 
                    LeafNodeStatusUpdate(error_message=f"Error generating new queries: {str(e)}", is_completed=True, iteration_progress=current_iter_progress)
                )
                break
            
            iteration += 1
        
        # Final status update if loop exited without specific completion status set
        final_node_status = status_manager.get_process_state(process_id).retrieval_status.leaf_nodes_status.get(node_display_id)
        if final_node_status and not final_node_status.is_completed:
            logger.info(f"PID-{process_id} Node-{node_display_id}: 迭代循环结束，标记为完成。")
            status_manager.update_leaf_node_status(process_id, node_display_id, 
                LeafNodeStatusUpdate(status_message="Node processing loop finished.", 
                                 is_completed=True, 
                                 iteration_progress=f"{iteration}/{self.max_iterations}",
                                 content_preview=(node['content'][:200] + '...') if node['content'] else "最终内容未生成", # 确保完成时也有最新的内容预览
                                 retrieved_docs_preview=current_doc_previews if new_results else []) # 如果最后一次迭代没有新文档，则清空或用最后一次的
            )
        else:
             logger.info(f"PID-{process_id} Node-{node_display_id}: 迭代检索完成，状态已更新。")
             # 确保即使LLM标记完成，也有最新的内容预览
             final_node_status_obj = status_manager.get_process_state(process_id).retrieval_status.leaf_nodes_status.get(node_display_id)
             if final_node_status_obj and final_node_status_obj.is_completed:
                status_manager.update_leaf_node_status(process_id, node_display_id,
                    LeafNodeStatusUpdate(content_preview=(node['content'][:200] + '...') if node['content'] else "最终内容未生成")
                )
    
    def _execute_searches(self, queries: List[str], node: Dict[str, Any], use_web: bool, use_kb: bool, process_id: str, node_display_id: str) -> List[Document]:
        """执行检索，包括网络和本地知识库
        
        Args:
            queries: 查询列表
            node: 当前处理的节点
            use_web: 是否使用网络检索
            use_kb: 是否使用本地知识库检索
            process_id: 当前处理流程的ID
            node_display_id: 当前节点的显示ID
            
        Returns:
            List[Document]: 检索结果列表
        """
        logger.info(f"PID-{process_id} Node-{node_display_id}: 执行 {len(queries)} 个查询. 使用网络: {use_web}, 使用知识库: {use_kb}")
        all_results: List[Document] = []
        
        web_search_futures = []
        kb_search_futures = []

        # 使用线程池执行，确保并发性
        with ThreadPoolExecutor(max_workers=self.web_concurrency + self.kb_concurrency) as executor:
            if use_web:
                for query in queries:
                    web_search_futures.append(executor.submit(self._execute_web_search_with_retry, query, node, process_id, node_display_id)) # 传递node用于日志记录
            
            if use_kb:
                for query in queries:
                    kb_search_futures.append(executor.submit(self._execute_kb_search_with_retry, query, node, process_id, node_display_id)) # 传递node用于日志记录

            # 收集网络搜索结果
            for future in as_completed(web_search_futures):
                try:
                    result = future.result()
                    if result:
                        all_results.extend(result)
                except Exception as e:
                    logger.error(f"PID-{process_id} Node-{node_display_id}: 网络搜索查询失败: {str(e)}")
            
            # 收集知识库搜索结果
            for future in as_completed(kb_search_futures):
                try:
                    result = future.result()
                    if result:
                        all_results.extend(result)
                except Exception as e:
                    logger.error(f"PID-{process_id} Node-{node_display_id}: 知识库搜索查询失败: {str(e)}")
        
        logger.info(f"PID-{process_id} Node-{node_display_id}: 查询执行完毕，共获得 {len(all_results)} 个初步结果。")
        return all_results
    
    def _execute_web_search_with_retry(self, query: str, node: Optional[Dict[str, Any]], process_id: str, node_display_id: str) -> List[Document]:
        """为单个查询执行网络搜索，包含重试逻辑
        
        Args:
            query: 搜索查询语句
            node: 当前处理的节点 (可选, 用于日志)
            process_id: 当前处理流程的ID
            node_display_id: 当前节点的显示ID
        Returns:
            List[Document]: 适配后的文档列表
        """
        # node_title = node.get('title', 'Unknown') if node else 'Unknown' # node_display_id is more specific
        logger.info(f"PID-{process_id} Node-{node_display_id}: 开始网络搜索，查询: \"{query}\"")
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                # 使用现有的web_search_agent执行搜索，需要传递title和summary
                # 由于这里我们只有query，我们将query作为title和summary
                raw_results = self.web_search_agent._search_docs(title=query, summary=query)
                
                # 转换为Document格式
                results = []
                for result in raw_results:
                    doc = self._adapt_web_result(result, query)
                    # 同样需要传递title和summary
                    refined_content = self.web_search_agent._refine_doc(doc.content, title=query, summary=query)
                    doc.content = refined_content
                    results.append(doc)
                
                logger.info(f"PID-{process_id} Node-{node_display_id}: 网络搜索查询 \"{query}\" 成功，获得 {len(results)} 个结果。")
                return results
            
            except Exception as e:
                retry_count += 1
                logger.warning(f"PID-{process_id} Node-{node_display_id}: 网络检索失败 ({retry_count}/{self.max_retries}): {str(e)}")
                if retry_count >= self.max_retries:
                    logger.error(f"PID-{process_id} Node-{node_display_id}: 网络检索最终失败: {str(e)}")
                    return []
                time.sleep(self.retry_delay * retry_count)  # 指数退避
    
    def _execute_kb_search_with_retry(self, query: str, node: Optional[Dict[str, Any]], process_id: str, node_display_id: str) -> List[Document]:
        """为单个查询执行知识库搜索，包含重试逻辑
        
        Args:
            query: 搜索查询语句 (通常是原始查询，HyDE在内部处理)
            node: 当前处理的节点 (可选, 用于日志)
            process_id: 当前处理流程的ID
            node_display_id: 当前节点的显示ID
        Returns:
            List[Document]: 适配后的文档列表
        """
        # node_title = node.get('title', 'Unknown') if node else 'Unknown' # node_display_id is more specific
        logger.info(f"PID-{process_id} Node-{node_display_id}: 开始知识库搜索，原始查询: \"{query}\"")
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                kb_search_results = self.local_kb_agent._search_docs(query) # Assuming this returns a list of dictionaries
                
                results = []
                for doc_dict in kb_search_results: # doc_dict is a dictionary
                    # Step 1: Adapt dictionary to Document instance
                    document_instance = self._adapt_kb_result(doc_dict, query)
                    
                    # Step 2: Refine the content of the Document instance
                    if document_instance: # Ensure adaptation was successful
                        refined_content = self.local_kb_agent._refine_doc(document_instance.content, title=query, summary=query)
                        document_instance.content = refined_content
                        results.append(document_instance)
                
                logger.info(f"PID-{process_id} Node-{node_display_id}: 知识库搜索查询 \"{query}\" 成功，获得 {len(results)} 个结果。")
                return results
                
            except Exception as e:
                retry_count += 1
                logger.warning(f"PID-{process_id} Node-{node_display_id}: 本地检索失败 ({retry_count}/{self.max_retries}): {str(e)}")
                if retry_count >= self.max_retries:
                    logger.error(f"PID-{process_id} Node-{node_display_id}: 本地检索最终失败: {str(e)}")
                    return []
                time.sleep(self.retry_delay * retry_count)  # 指数退避
    
    def _adapt_web_result(self, result, query):
        """将网络检索结果转换为统一的Document格式
        
        Args:
            result: 网络检索结果 (结构化字典)
            query: 检索查询
            
        Returns:
            Document: 统一格式的文档
        """
        metadata = {
            'url': result.get('url', ''),
            'title': result.get('title', ''),
            'score': result.get('score', 0),
        }
        
        return Document(
            content=result.get('content', ''),
            source='web',
            query=query,
            metadata=metadata
        )
    
    def _adapt_kb_result(self, doc, query):
        """将本地知识库检索结果转换为统一的Document格式
        
        Args:
            doc: 本地知识库检索结果 (结构化字典)
            query: 检索查询
            
        Returns:
            Document: 统一格式的文档
        """
        # 直接使用doc中的metadata
        metadata = doc.get('metadata', {})
        
        # 添加其他重要字段到metadata
        for key in ['source', 'title', 'page', 'author']:
            if key in doc and key not in metadata:
                metadata[key] = doc[key]
        
        return Document(
            content=doc.get('content', ''),
            source='kb',
            query=query, 
            metadata=metadata
        )
    
    def _deduplicate(self, new_docs, history_docs):
        """去重，避免重复的检索结果
        
        Args:
            new_docs: 新检索到的文档
            history_docs: 历史检索文档
            
        Returns:
            List[Document]: 去重后的文档列表
        """
        deduplicated = []
        
        # 创建历史文档索引
        history_ids = {doc.id for doc in history_docs}
        history_titles = {}
        for doc in history_docs:
            title = doc.metadata.get('title', '')
            if title:
                if title not in history_titles:
                    history_titles[title] = []
                history_titles[title].append(doc)
        
        for new_doc in new_docs:
            # 1. 检查ID是否重复（URL或文件路径+页码）
            if new_doc.id in history_ids:
                continue
                
            # 2. 检查标题是否重复
            title = new_doc.metadata.get('title', '')
            if title and title in history_titles:
                # 如果标题相同，检查内容相似度
                similar = False
                for old_doc in history_titles[title]:
                    if self._content_similarity(new_doc.content, old_doc.content) > self.similarity_threshold:
                        similar = True
                        break
                if similar:
                    continue
                    
            # 3. 对于没有明确标识的文档，检查内容相似度
            if not title and not new_doc.id:
                similar = False
                for old_doc in history_docs:
                    if self._content_similarity(new_doc.content, old_doc.content) > self.similarity_threshold:
                        similar = True
                        break
                if similar:
                    continue
                    
            deduplicated.append(new_doc)
        return deduplicated
    
    def _content_similarity(self, text1, text2):
        """计算两段文本的相似度
        
        Args:
            text1: 第一段文本
            text2: 第二段文本
            
        Returns:
            float: 相似度分数(0-1)
        """
        # 使用较简单的方法，避免引入额外依赖
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union
    
    def _update_references(self, node, new_results):
        """更新节点的引用列表
        
        Args:
            node: 当前处理的节点
            new_results: 新检索结果
        """
        for doc in new_results:
            # 检查引用是否已存在
            if not any(ref.get('key') == doc.citation_key for ref in node['references']):
                reference = {
                    'key': doc.citation_key,
                    'title': doc.metadata.get('title', '未知标题'),
                    'source': doc.source,
                }
                
                # 根据来源添加不同的额外信息
                if doc.source == 'web':
                    reference['url'] = doc.metadata.get('url', '')
                else:
                    reference['file'] = doc.metadata.get('source', '')
                    reference['page'] = doc.metadata.get('page', '')
                    reference['author'] = doc.metadata.get('author', '')
                    reference['year'] = doc.metadata.get('year', '')
                
                node['references'].append(reference)
    
    def _format_retrieval_results_for_prompt(self, results):
        """将检索结果格式化为提示模板可用的格式
        
        Args:
            results: 检索结果列表
            
        Returns:
            str: 格式化后的检索结果文本
        """
        formatted_results = []
        
        for doc in results:
            source_type = "网络来源" if doc.source == 'web' else "本地知识库"
            
            # 准备元数据信息
            metadata_info = []
            if doc.source == 'web':
                if 'title' in doc.metadata and doc.metadata['title']:
                    metadata_info.append(f"标题: {doc.metadata['title']}")
                if 'url' in doc.metadata and doc.metadata['url']:
                    metadata_info.append(f"链接: {doc.metadata['url']}")
            else:  # 本地知识库
                if 'source' in doc.metadata and doc.metadata['source']:
                    file_name = os.path.basename(doc.metadata['source'])
                    metadata_info.append(f"文件: {file_name}")
                if 'page' in doc.metadata:
                    metadata_info.append(f"页码: {doc.metadata['page']}")
                if 'title' in doc.metadata and doc.metadata['title']:
                    metadata_info.append(f"标题: {doc.metadata['title']}")
                if 'author' in doc.metadata and doc.metadata['author']:
                    metadata_info.append(f"作者: {doc.metadata['author']}")
            
            # 格式化单个文档
            formatted_doc = f"""[{doc.citation_key}] {source_type}
{', '.join(metadata_info)}
---
{doc.content}
---
"""
            formatted_results.append(formatted_doc)
        
        return "\n\n".join(formatted_results)
    
    def _format_previous_queries(self, queries):
        """格式化之前的查询列表
        
        Args:
            queries: 查询列表
            
        Returns:
            str: 格式化后的查询文本
        """
        formatted_queries = []
        for idx, query in enumerate(queries):
            formatted_queries.append(f"{idx+1}. \"{query}\"")
        return "\n".join(formatted_queries)
    
    def _complete(self, prompt: str, process_id: str, node_display_id: str):
        """调用LLM完成提示
        
        Args:
            prompt: 提示文本
            process_id: 当前处理流程的ID
            node_display_id: 当前节点的显示ID
            
        Returns:
            str: 模型响应
        """
        try:
            response = self.llm.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"PID-{process_id} Node-{node_display_id}: 调用LLM出错: {str(e)}")
            raise 

    def _clean_json_response(self, response):
        """清理可能含有markdown格式的JSON响应
        
        Args:
            response: 原始响应字符串
            
        Returns:
            str: 清理后的JSON字符串
        """
        # 移除可能的```json前缀和```后缀
        response = response.strip()
        if "```json" in response:
            response = response.split("```json")[1]
        elif "```" in response:
            response = response.split("```")[1]
        
        # 移除末尾的```
        if response.endswith("```"):
            response = response[:-3]
            
        return response.strip() 