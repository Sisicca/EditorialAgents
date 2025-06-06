from agents.initial_analysis_agent import InitialAnalysisAgent
from agents.unified_retrieval_agent import UnifiedRetrievalAgent
from agents.comprehensive_answer_agent import ComprehensiveAnswerAgent
from agents.intro_conclusion_agent import IntroductionConclusionAgent
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
        
        logger.info("正在创建 IntroductionConclusionAgent")
        self.intro_conclusion_agent = IntroductionConclusionAgent(config['intro_conclusion'])
    
    def run(self, topic, description, problem):
        # 生成框架
        framework = self.initial_agent.get_framework(
            topic=topic, description=description, problem=problem
        )
        
        # 使用统一的迭代检索流程，但跳过引言和总结节点
        self.unified_retrieval_agent.iterative_retrieval_for_leaf_nodes(
            framework=framework, 
            skip_function=self.intro_conclusion_agent.should_skip_retrieval
        )
        
        # 综合文章内容（排除引言和总结）
        self.comprehensive_agent.compose(
            framework=framework,
            skip_function=self.intro_conclusion_agent.should_skip_retrieval
        )
        
        # 生成引言和总结
        logger.info("正在生成引言和总结...")
        self.intro_conclusion_agent.generate_introduction_and_conclusion(
            framework=framework,
            topic=topic,
            description=description
        )
        
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
            if 'references' in node and isinstance(node['references'], list):
                for ref in node['references']:
                    if isinstance(ref, dict) and 'key' in ref:
                        all_refs[ref['key']] = ref
        
        # 如果没有收集到任何引用，返回空列表
        if not all_refs:
            logger.warning("未收集到任何引用")
            return []
            
        # 格式化参考文献列表
        formatted_refs = []
        for key, ref in sorted(all_refs.items()):
            try:
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
            except Exception as e:
                logger.error(f"格式化引用 {key} 时出错: {str(e)}")
                formatted_refs.append(f"[{key}] 引用格式化错误")
        
        return formatted_refs
