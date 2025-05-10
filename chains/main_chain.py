from agents.initial_analysis_agent import InitialAnalysisAgent
from agents.unified_retrieval_agent import UnifiedRetrievalAgent
from agents.comprehensive_answer_agent import ComprehensiveAnswerAgent
from loguru import logger
from rich.pretty import pprint

class ScienceArticleChain:
    def __init__(self, config):
        logger.info("正在创建 InitialAnalysisAgent")
        self.initial_agent = InitialAnalysisAgent(config['initial_analysis'])
        
        logger.info("正在创建 UnifiedRetrievalAgent")
        self.unified_retrieval_agent = UnifiedRetrievalAgent(config['web_search'], config['local_kb'])
        
        logger.info("正在创建 ComprehensiveAnswerAgent")
        self.comprehensive_agent = ComprehensiveAnswerAgent(config['comprehensive_answer'])
    
    def run(self, topic, description, problem):
        # 生成框架
        framework = self.initial_agent.get_framework(
            topic=topic, description=description, problem=problem
        )
        
        # 使用统一的迭代检索流程替代原来分开的网络和本地知识库检索
        self.unified_retrieval_agent.iterative_retrieval_for_leaf_nodes(framework=framework)
        
        # 综合文章内容
        self.comprehensive_agent.compose(framework=framework)
        
        # 生成参考文献列表
        content = framework.outline.get('content', '')
        references = self._compile_references(framework)
        if references:
            content += "\n\n## 参考文献\n\n" + "\n".join(references)
            framework.outline['content'] = content
        
        return content
    
    def _compile_references(self, framework):
        """收集所有节点的引用并生成参考文献列表"""
        all_refs = {}
        
        # 收集所有引用
        for node in framework.find_all_nodes():
            if 'references' in node:
                for ref in node['references']:
                    all_refs[ref['key']] = ref
        
        # 格式化参考文献列表
        formatted_refs = []
        for key, ref in sorted(all_refs.items()):
            if ref['source'] == 'web':
                formatted_refs.append(f"[{key}] {ref.get('title', '未知标题')}. {ref.get('url', '')}")
            else:  # ref['source'] == 'kb'
                file_name = ref.get('file', '')
                if file_name:
                    file_name = file_name.split('/')[-1] if '/' in file_name else file_name
                
                author = ref.get('author', '')
                year = ref.get('year', '')
                title = ref.get('title', '未知标题')
                
                if author and year:
                    formatted_refs.append(f"[{key}] {author}. ({year}). {title}. {file_name}")
                else:
                    formatted_refs.append(f"[{key}] {title}. {file_name}")
        
        return formatted_refs
