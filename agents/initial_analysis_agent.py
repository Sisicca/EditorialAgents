from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from agents.prompts import PROMPTS
from pprint import pprint
import os
from loguru import logger

class ArticleOutline():
    def __init__(self, outline:dict):
        self.outline = outline
    
    def generate_paper_structure(self):
        def traverse_outline(node, numbering=[]):
            lines = []
            # 处理主标题
            if node['level'] == 1:
                lines.append(f"《{node['title']}》")
            else:
                # 生成当前节点的序号
                current_number = '.'.join(map(str, numbering))
                lines.append(f"{current_number}. {node['title']}: {node['summary']}")
            
            # 如果需要包含摘要，可以取消下面的注释
            # if node.get('summary'):
            #     lines.append(f"    摘要：{node['summary']}")
            
            # 处理子节点
            for idx, child in enumerate(node.get('children', []), 1):
                # 为子节点生成新的序号列表
                child_numbering = numbering + [idx]
                lines.extend(traverse_outline(child, child_numbering))
            
            return lines
        lines = traverse_outline(self.outline)
        return '\n'.join(lines)
    
    def check_outline_structure(self):
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
            traverse(self.outline, 1, [self.outline.get('title', '未命名')])
            
            # 检查是否只有一个level1的标题
            if level1_count != 1:
                errors.append(f"共有 {level1_count} 个 level1 的标题，但需要且只有1个。")
            
            # 输出错误信息
            if errors:
                print("大纲结构不正确，发现以下问题：")
                for error in errors:
                    print(f"- {error}")
                return False
            else:
                print("大纲结构正确。")
                return True
    
    def find_leaf_nodes(self):
        leaf_nodes = []

        def traverse(node):
            if not node.get('children'):
                leaf_nodes.append(node)
            else:
                for child in node['children']:
                    traverse(child)

        traverse(self.outline)
        return leaf_nodes
    
    def find_all_nodes(self):
        """收集大纲中的所有节点
        
        Returns:
            list: 所有节点的列表
        """
        all_nodes = []
        
        def traverse(node):
            all_nodes.append(node)
            for child in node.get('children', []):
                traverse(child)
        
        traverse(self.outline)
        return all_nodes
    
    def find_max_level(self):
        leaf_nodes = self.find_leaf_nodes()
        return max([node['level'] for node in leaf_nodes])
    
    def find_level_n_nodes(self, level_n):
        level_n_nodes = []

        def traverse(node):
            if node['level'] == level_n:
                level_n_nodes.append(node)
            else:
                for child in node['children']:
                    traverse(child)

        traverse(self.outline)
        return level_n_nodes

class InitialAnalysisAgent:
    def __init__(self, config:dict):
        self.llm = ChatOpenAI(api_key=config['api_key'] or os.environ['OPENAI_API_KEY'],
                              base_url=config['base_url'] or os.environ['OPENAI_BASE_URL'],
                              model=config['model'])
        
        
    
    def get_framework(self, topic:str, description:str, problem:str) -> ArticleOutline:
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
        
        return ArticleOutline(response)
