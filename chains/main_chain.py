from agents.initial_analysis_agent import InitialAnalysisAgent
from agents.web_search_agent import WebSearchAgent
from agents.local_kb_agent import LocalKBAgent
from agents.comprehensive_answer_agent import ComprehensiveAnswerAgent
from loguru import logger
from rich.pretty import pprint

class ScienceArticleChain:
    def __init__(self, config):
        logger.info("正在创建 InitialAnalysisAgent")
        self.initial_agent = InitialAnalysisAgent(config['initial_analysis'])
        
        logger.info("正在创建 WebSearchAgent")
        self.web_search_agent = WebSearchAgent(config['web_search'])
        
        logger.info("正在创建 LocalKBAgent")
        self.local_kb_agent = LocalKBAgent(config['local_kb'])
        
        logger.info("正在创建 ComprehensiveAnswerAgent")
        self.comprehensive_agent = ComprehensiveAnswerAgent(config['comprehensive_answer'])
    
    def run(self, topic, description, problem):
        framework = self.initial_agent.get_framework(
            topic=topic, description=description, problem=problem
        )
        
        self.web_search_agent.search_for_leaf_nodes(framework=framework)
        
        self.local_kb_agent.search_for_leaf_nodes(framework=framework)
        
        self.comprehensive_agent.compose(framework=framework)
        
        return framework.outline.get('content')
