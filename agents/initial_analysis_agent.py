from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from agents.prompts import PROMPTS
from pprint import pprint
import os
from loguru import logger

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
    
    def print_outline(self, node, indent=0):
        print('    ' * indent + f"{'#' * node['level']} {node['title']}")
        print('    ' * indent + f"概述: {node['summary']}\n")
        for child in node.get('children', []):
            self.print_outline(child, indent + 1)
            
    def check_outline_structure(self, outline):
        """
        检查文章大纲结构是否符合要求：
        1. 只有一个 level1 的标题（文章主标题）。
        2. 标题的 level 不超过4。
        3. 子标题的 level 必须比父标题的 level 大1。
        
        参数：
            outline (dict): 文章大纲的字典表示。
            
        返回：
            bool: 如果结构正确，返回True；否则，返回False并打印错误信息。
        """
        errors = []
        level1_count = 0
        
        def traverse(node, expected_level, path):
            nonlocal level1_count
            # 检查当前节点是否为字典
            if not isinstance(node, dict):
                errors.append(f"节点路径 '{' > '.join(path)}' 不是字典类型。")
                return
            
            # 检查必要的键是否存在
            required_keys = {'title', 'level', 'summary', 'children'}
            if not required_keys.issubset(node.keys()):
                missing = required_keys - node.keys()
                errors.append(f"节点路径 '{' > '.join(path)}' 缺少键：{', '.join(missing)}。")
                return
            
            # 检查level是否为整数
            level = node.get('level')
            if not isinstance(level, int):
                errors.append(f"节点路径 '{' > '.join(path)}' 的level必须是整数，当前值为{level}。")
                return
            
            # 统计level1的标题数量
            if level == 1:
                level1_count += 1
            
            # 检查level是否超过4
            if level > 4:
                errors.append(f"节点路径 '{' > '.join(path)}' 的level {level} 超过最大允许级别4。")
            
            # 检查level是否符合预期
            if level != expected_level:
                errors.append(f"节点路径 '{' > '.join(path)}' 的level {level} 不符合预期的level {expected_level}。")
            
            # 检查children是否为列表
            children = node.get('children', [])
            if not isinstance(children, list):
                errors.append(f"节点路径 '{' > '.join(path)}' 的children必须是列表。")
                return
            
            # 递归检查子节点
            for idx, child in enumerate(children, start=1):
                child_path = path + [f"{child.get('title', '未命名')}"]
                traverse(child, expected_level + 1, child_path)
        
        # 开始遍历，从根节点开始，预期level为1
        traverse(outline, 1, [outline.get('title', '未命名')])
        
        # 检查是否只有一个level1的标题
        if level1_count != 1:
            errors.append(f"共有 {level1_count} 个 level1 的标题，但需要且只有1个。")
        
        # 输出错误信息
        if errors:
            logger.info("大纲结构不正确，发现以下问题：")
            for error in errors:
                logger.info(f"- {error}")
            return False
        else:
            logger.info("大纲结构正确。")
            return True
