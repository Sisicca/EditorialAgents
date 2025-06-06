#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试引言和总结生成功能

这个脚本用于测试新的IntroductionConclusionAgent是否能正确生成引言和总结。
"""

import os
import sys
import yaml
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.initial_analysis_agent import InitialAnalysisAgent
from agents.intro_conclusion_agent import IntroductionConclusionAgent
from loguru import logger

def load_config():
    """加载配置文件"""
    config_path = project_root / "config" / "config_example.yaml"
    
    if not config_path.exists():
        logger.error(f"配置文件不存在: {config_path}")
        return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config

def create_test_framework():
    """创建一个测试用的文章框架"""
    test_outline = {
        "title": "人工智能在医疗诊断中的应用",
        "level": 1,
        "summary": "探讨人工智能技术在医疗诊断中的各种应用及其影响。",
        "children": [
            {
                "title": "引言",
                "level": 2,
                "summary": "介绍人工智能在医疗领域的发展背景和研究意义。",
                "children": []
            },
            {
                "title": "人工智能技术概述",
                "level": 2,
                "summary": "概述人工智能的基本概念、主要技术及其在医疗中的基本应用。",
                "children": [],
                "content": "人工智能（AI）是计算机科学的一个分支，旨在创建能够模拟人类认知功能的智能系统。在医疗领域，AI的应用主要基于机器学习和深度学习等技术。这些技术通过分析大量医疗数据，学习复杂的模式和关联，从而辅助医疗决策和诊断过程。机器学习算法在疾病预测、早期检测和预后预测方面展现出巨大潜力，而深度学习特别是在医学影像分析中表现出色。"
            },
            {
                "title": "应用案例",
                "level": 2,
                "summary": "通过具体案例展示人工智能在医疗诊断中的实际应用效果。",
                "children": [],
                "content": "人工智能在医疗诊断中已有多个成功的应用案例。在肺癌诊断方面，AI系统通过分析CT扫描图像，能够检测早期肺结节并评估其恶性程度，准确率达到94.4%。在糖尿病视网膜病变检测中，深度学习算法能够自动分析眼底照片，识别微血管瘤等早期病变特征，敏感性达到87.2%，特异性达到90.7%。这些案例展示了AI技术在提高诊断准确率和效率方面的巨大潜力。"
            },
            {
                "title": "挑战与未来发展",
                "level": 2,
                "summary": "分析人工智能在医疗诊断中面临的主要挑战及未来发展趋势。",
                "children": [],
                "content": "尽管人工智能在医疗诊断领域取得了显著进展，但仍面临多方面的挑战。数据隐私与安全问题是首要关注点，AI系统的训练需要大量患者数据，如何在保证数据质量的同时保护患者隐私是关键问题。此外，AI辅助诊断还涉及复杂的伦理和法律问题，如医疗责任归属、算法偏见和公平性等。未来，AI医疗诊断将向多模态、精准化方向发展，结合基因组学、蛋白质组学等多源数据的AI系统将提供更全面的健康评估。"
            },
            {
                "title": "总结",
                "level": 2,
                "summary": "总结人工智能在医疗诊断中的应用成果及其未来潜力。",
                "children": []
            }
        ]
    }
    
    # 导入ArticleOutline类
    from agents.initial_analysis_agent import ArticleOutline
    return ArticleOutline(test_outline)

def test_intro_conclusion_generation():
    """测试引言和总结生成功能"""
    logger.info("开始测试引言和总结生成功能...")
    
    # 加载配置
    config = load_config()
    if not config:
        logger.error("无法加载配置文件")
        return False
    
    try:
        # 创建引言和总结生成代理
        intro_conclusion_agent = IntroductionConclusionAgent(config['intro_conclusion'])
        
        # 创建测试框架
        framework = create_test_framework()
        
        # 测试主题和描述
        topic = "人工智能在医疗诊断中的应用"
        description = "详细介绍各种可以用于医疗诊断的人工智能技术，介绍他们的原理和应用，需要涵盖多种模态"
        
        # 生成引言和总结
        logger.info("正在生成引言和总结...")
        intro_conclusion_agent.generate_introduction_and_conclusion(
            framework=framework,
            topic=topic,
            description=description
        )
        
        # 检查结果
        introduction_node = intro_conclusion_agent._find_node_by_keywords(
            framework.outline, ['引言', 'introduction', '前言', '导言']
        )
        conclusion_node = intro_conclusion_agent._find_node_by_keywords(
            framework.outline, ['总结', 'conclusion', '结论', '小结', '结语']
        )
        
        if introduction_node and 'content' in introduction_node:
            logger.success("引言生成成功！")
            logger.info(f"引言内容长度: {len(introduction_node['content'])} 字符")
            print("\n=== 生成的引言 ===")
            print(introduction_node['content'])
        else:
            logger.error("引言生成失败")
            return False
        
        if conclusion_node and 'content' in conclusion_node:
            logger.success("总结生成成功！")
            logger.info(f"总结内容长度: {len(conclusion_node['content'])} 字符")
            print("\n=== 生成的总结 ===")
            print(conclusion_node['content'])
        else:
            logger.error("总结生成失败")
            return False
        
        # 测试跳过函数
        logger.info("\n测试跳过函数...")
        test_nodes = [
            {"title": "引言", "level": 2},
            {"title": "技术概述", "level": 2},
            {"title": "总结", "level": 2},
            {"title": "Introduction", "level": 2},
            {"title": "Conclusion", "level": 2},
        ]
        
        for node in test_nodes:
            should_skip = intro_conclusion_agent.should_skip_retrieval(node)
            logger.info(f"节点 '{node['title']}' 是否跳过检索: {should_skip}")
        
        logger.success("引言和总结生成功能测试完成！")
        return True
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 设置日志级别
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    success = test_intro_conclusion_generation()
    
    if success:
        logger.success("所有测试通过！")
        sys.exit(0)
    else:
        logger.error("测试失败！")
        sys.exit(1)