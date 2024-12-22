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
        # 初步分析
        logger.info("正在分析问题...")
        analysis_output = self.initial_agent.analyze(topic, description, problem)
        framework = analysis_output['framework']
        queries = analysis_output['queries']
        hypothetical_doc = analysis_output['hypothetical_doc']
        
        pprint(framework)
        pprint(queries)
        pprint(hypothetical_doc)
        
        # 网络检索并回答
        logger.info("正在通过网络回答问题...")
        web_response_results = self.web_search_agent.response(queries)
        
        pprint(web_response_results)
        
        # 本地知识库检索并回答
        logger.info("正在通过本地知识库回答问题...")
        local_response_results = self.local_kb_agent.response(hypothetical_doc)
        
        pprint(local_response_results)
        
        # 补全框架 撰写全文
        logger.info("正在撰写全文...")
        article = self.comprehensive_agent.generate(framework, web_response_results, local_response_results)
        
        return article
