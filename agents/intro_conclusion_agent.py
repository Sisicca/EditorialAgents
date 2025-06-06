from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from agents.prompts import PROMPTS
from agents.initial_analysis_agent import ArticleOutline
import os
from loguru import logger

class IntroductionConclusionAgent:
    """
    引言和总结生成代理
    
    该代理负责在其他章节内容生成完成后，基于已生成的内容来撰写引言和总结部分。
    引言部分将介绍文章的背景、目的和结构；
    总结部分将概括主要发现、结论和未来展望。
    """
    
    def __init__(self, config):
        self.llm = ChatOpenAI(
            api_key=config['api_key'] or os.environ["OPENAI_API_KEY"],
            base_url=config['base_url'] or os.environ["OPENAI_BASE_URL"],
            model=config['model'],
        )
        
        # 构建引言生成链
        try:
            introduction_template = PromptTemplate(
                input_variables=['outline', 'main_content', 'topic', 'description'],
                template=PROMPTS['generate_introduction']
            )
            self.introduction_chain = introduction_template | self.llm | StrOutputParser()
            
            # 构建总结生成链
            conclusion_template = PromptTemplate(
                input_variables=['outline', 'main_content', 'topic', 'description'],
                template=PROMPTS['generate_conclusion']
            )
            self.conclusion_chain = conclusion_template | self.llm | StrOutputParser()
            
            logger.info("引言和总结生成链构建成功")
        except Exception as e:
            logger.error(f"构建引言和总结生成链失败: {e}")
            self.introduction_chain = None
            self.conclusion_chain = None
    
    def generate_introduction_and_conclusion(self, framework: ArticleOutline, topic: str, description: str):
        """
        为文章生成引言和总结
        
        Args:
            framework: 文章框架对象
            topic: 文章主题
            description: 文章描述
        """
        try:
            # 获取文章大纲结构
            outline = framework.generate_paper_structure()
            
            # 收集所有已生成的主体内容（排除引言和总结）
            main_content = self._extract_main_content(framework)
            
            # 查找引言和总结节点
            introduction_node = self._find_node_by_keywords(framework.outline, ['引言', 'introduction', '前言', '导言'])
            conclusion_node = self._find_node_by_keywords(framework.outline, ['总结', 'conclusion', '结论', '小结', '结语'])
            
            # 生成引言
            if introduction_node and self.introduction_chain:
                logger.info("正在生成引言...")
                introduction_content = self.introduction_chain.invoke({
                    'outline': outline,
                    'main_content': main_content,
                    'topic': topic,
                    'description': description
                })
                introduction_node['content'] = introduction_content
                logger.info("引言生成完成")
            
            # 生成总结
            if conclusion_node and self.conclusion_chain:
                logger.info("正在生成总结...")
                conclusion_content = self.conclusion_chain.invoke({
                    'outline': outline,
                    'main_content': main_content,
                    'topic': topic,
                    'description': description
                })
                conclusion_node['content'] = conclusion_content
                logger.info("总结生成完成")
                
        except Exception as e:
            logger.error(f"生成引言和总结时出错: {e}")
    
    def _extract_main_content(self, framework: ArticleOutline) -> str:
        """
        提取文章的主体内容（排除引言和总结）
        
        Args:
            framework: 文章框架对象
            
        Returns:
            str: 主体内容文本
        """
        main_content_parts = []
        
        def extract_content(node):
            # 检查是否为引言或总结节点
            title_lower = node.get('title', '').lower()
            if any(keyword in title_lower for keyword in ['引言', 'introduction', '前言', '导言', '总结', 'conclusion', '结论', '小结', '结语']):
                return
            
            # 如果有内容且不是引言/总结，则添加
            if 'content' in node and node['content'].strip():
                main_content_parts.append(f"## {node['title']}\n{node['content']}")
            
            # 递归处理子节点
            for child in node.get('children', []):
                extract_content(child)
        
        extract_content(framework.outline)
        return "\n\n".join(main_content_parts)
    
    def _find_node_by_keywords(self, node, keywords):
        """
        根据关键词查找节点
        
        Args:
            node: 当前节点
            keywords: 关键词列表
            
        Returns:
            dict: 找到的节点，如果没找到返回None
        """
        title_lower = node.get('title', '').lower()
        
        # 检查当前节点标题是否包含关键词
        for keyword in keywords:
            if keyword.lower() in title_lower:
                return node
        
        # 递归搜索子节点
        for child in node.get('children', []):
            result = self._find_node_by_keywords(child, keywords)
            if result:
                return result
        
        return None
    
    def should_skip_retrieval(self, node):
        """
        判断节点是否应该跳过检索（用于引言和总结节点）
        
        Args:
            node: 节点对象
            
        Returns:
            bool: 如果应该跳过检索返回True
        """
        title_lower = node.get('title', '').lower()
        skip_keywords = ['引言', 'introduction', '前言', '导言', '总结', 'conclusion', '结论', '小结', '结语']
        
        return any(keyword.lower() in title_lower for keyword in skip_keywords)