from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from agents.prompts import PROMPTS
from pprint import pprint
import os
from tavily import TavilyClient

class InitialAnalysisAgent:
    def __init__(self, config):
        self.llm = ChatOpenAI(api_key=config['api_key'],
                              base_url=config['base_url'],
                              model=config['model'])
        
        
    
    def analyze(self, topic, description, problem):
        analysis_template = PromptTemplate(
            input_variables=['topic', 'description', 'problem'],
            template=PROMPTS['initial_analysis_agent']
        )
        
        analysis_chain = analysis_template | self.llm | JsonOutputParser()
        
        response = analysis_chain.invoke(
            {
                'topic': topic,
                'description': description,
                'problem': problem
            }
        )
        
        return response
    

if __name__ == '__main__':
    config = {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'base_url': os.getenv('OPENAI_BASE_URL'),
        'model': 'gpt-4o'
    }
    
    test_analysis_agent = InitialAnalysisAgent(config=config)
    
    response = test_analysis_agent.analyze(
        topic='睡眠、健康、环境与跑步表现',
        description=('我希望能写作一篇总结影响跑步表现的各种因素的文章，包括但不限于睡眠因素、健康因素、环境因素等等。'
                     '需要全面且详细的总结出各种可能的因素，分门别类且轻重有序。'
                     '对于每一个因素需要给出它的作用机制，即它是如何一步一步影响到人的跑步表现的。'),
        problem='影响跑步表现的因素有哪些？它们是如何影响跑步的？'
    )
    
    pprint(response)
