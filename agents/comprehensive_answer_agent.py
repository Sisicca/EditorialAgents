from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from agents.prompts import PROMPTS
from pprint import pprint
import os
from tavily import TavilyClient
from typing import Dict, List

class ComprehensiveAnswerAgent:
    def __init__(self, config):
        self.llm = ChatOpenAI(api_key=config['api_key'],
                              base_url=config['base_url'],
                              model=config['model'])
        
    def _process_response_results(self, response_results:List[Dict[str,str]]):
        summaries = ''
        
        for idx, result in enumerate(response_results):
            query = result['query']
            answer = result['answer']
            
            summaries += '-'*100 + '\n'
            summaries += f'问题{idx+1}：\n{query}\n'
            summaries += f'回答{idx+1}：\n{answer}\n'
            summaries += '-'*100 + '\n\n'
        
        return summaries
    
    def generate(self, framework, web_response_results, local_response_results):
        web_summaries = self._process_response_results(web_response_results)
        local_summaries = self._process_response_results(local_response_results)
        
        comprehensive_answer_template = PromptTemplate(
            input_variables=['framework', 'web_summaries', 'local_summaries'],
            template=PROMPTS['comprehensive_answer_agent']
        )
        
        comprehensive_answer_chain = comprehensive_answer_template | self.llm | StrOutputParser()
        
        article = comprehensive_answer_chain.invoke(
            {
                'framework': framework,
                'web_summaries': web_summaries,
                'local_summaries': local_summaries
            }
        )
        
        return article
