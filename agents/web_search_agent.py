from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from agents.prompts import PROMPTS
from pprint import pprint
import os
from tavily import TavilyClient
from typing import List

class WebSearchAgent:
    def __init__(self, config):
        self.llm = ChatOpenAI(api_key=config['api_key'],
                              base_url=config['base_url'],
                              model=config['model'])
        self.web_num = config['web_num']
        
        if config['search_engine'] == 'tavily':
            self.search_client = TavilyClient(api_key=config['search_api_key'])
        else:
            raise ImportError("'search_engine' must be 'tayily'.")
    
    def _search(self, queries:List[str]):
        search_results = []
        for query in queries:
            search_results.append(
                self.search_client.get_search_context(
                    query=query,
                    max_results=self.web_num,
                    # max_tokens=2000
                )
            )
        return search_results
    
    def response(self, queries:List[str]):
        response_results = []
        
        web_search_template = PromptTemplate(
            input_variables=['query', 'content'],
            template=PROMPTS['web_search_agent']
        )
        
        web_search_chain = web_search_template | self.llm | StrOutputParser()
        
        for query in queries:
            
            raw_result = self.search_client.search(
                query=query,
                max_results=self.web_num,
                include_answer=False,
                include_raw_content=True
            )
            # answer = raw_result['answer']
            content = ''
            count = 0
            for result in raw_result['results']:
                if result['raw_content']:
                    count += 1
                    content += f'WebDocument{count}\n'
                    content += ''.join(result['raw_content'])
                    content += '-'*100 + '\n'

            answer = web_search_chain.invoke(
                {
                    'query': query,
                    'content': content
                }
            )
            
            response_results.append(
                {
                    'query': query,
                    'answer': answer,
                    'content': content
                }
            )

        return response_results

if __name__ == '__main__':
    config = {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'base_url': os.getenv('OPENAI_BASE_URL'),
        'model': 'gpt-4o',
        'search_engine': 'tavily',
        'search_api_key': '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',
        'web_num': 3
    }
    
    test_websearch_agent = WebSearchAgent(
        config=config
    )
    
    # search_results = test_websearch_agent._search(
    #     queries=['跑步表现与睡眠质量', '心血管健康对跑步的重要性']
    # )
    
    # print(search_results)
    
    response_results = test_websearch_agent.response(
        queries=['气温如何影响跑步表现？']
    )
    
    pprint(response_results)