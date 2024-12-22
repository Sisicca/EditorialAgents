from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from agents.prompts import PROMPTS
from tavily import TavilyClient
from typing import List
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

class WebSearchAgent:
    def __init__(self, config):
        self.llm = ChatOpenAI(api_key=config['api_key'],
                              base_url=config['base_url'],
                              model=config['model'])
        self.web_num = config['web_num']
        
        if config['search_engine'] == 'tavily':
            self.search_client = TavilyClient(api_key=config['search_api_key'])
        else:
            raise ImportError("'search_engine' must be 'tavily'.")
    
    def _search(self, queries: List[str]):
        search_results = []
        for query in queries:
            search_results.append(
                self.search_client.get_search_context(
                    query=query,
                    max_results=self.web_num,
                )
            )
        return search_results
    
    def _process_query(self, query: str, web_search_chain):
        raw_result = self.search_client.search(
            query=query,
            max_results=self.web_num,
            include_answer=False,
            include_raw_content=True
        )
        
        content = ''
        count = 0
        for result in raw_result['results']:
            if result['raw_content']:
                count += 1
                content += f'WebDocument{count}\n'
                content += ''.join(result['raw_content'])
                content += '-' * 100 + '\n'

        answer = web_search_chain.invoke(
            {
                'query': query,
                'content': content
            }
        )
        
        return {
            'query': query,
            'answer': answer,
            'content': content
        }

    def response(self, queries: List[str]):
        response_results = []
        
        web_search_template = PromptTemplate(
            input_variables=['query', 'content'],
            template=PROMPTS['web_search_agent']
        )
        
        web_search_chain = web_search_template | self.llm | StrOutputParser()
        
        max_query_num = len(queries)
        
        with ThreadPoolExecutor() as executor:
            future_to_query = {executor.submit(self._process_query, query, web_search_chain): query for query in queries}
            with tqdm(total=max_query_num, desc="根据网络搜索结果回答问题") as pbar:
                for future in as_completed(future_to_query):
                    result = future.result()
                    response_results.append(result)
                    
                    pbar.update(1)

        return response_results
