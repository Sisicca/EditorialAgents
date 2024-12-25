import yaml
from chains.main_chain import ScienceArticleChain
from rich.pretty import pprint
from agents.initial_analysis_agent import InitialAnalysisAgent

def load_config(config_path='config/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def main():
    config = load_config()
    chain = ScienceArticleChain(config)

    topic = "论如何科学跑步"
    description = "本科普文章旨在介绍科学跑步的方法和技巧，涵盖跑步的基本原理、正确的跑步姿势、训练计划的制定、预防和处理跑步相关的常见伤病，以及营养与恢复策略。通过结合最新的科学研究和实际案例，帮助读者了解如何通过科学的方法提升跑步效果，减少受伤风险，并享受跑步带来的健康益处。"
    problem = "1. 科学跑步的基本原理是什么？如何理解跑步中的生物力学和能量系统？\n2. 正确的跑步姿势有哪些关键要素？不良跑姿可能带来哪些健康问题？\n3. 如何制定一个有效的跑步训练计划，以提高耐力和速度，同时避免过度训练？\n4. 跑步过程中常见的伤病有哪些？如何预防和处理这些伤病？\n5. 科学跑步中，营养摄入和恢复策略应如何安排，以支持训练效果和身体健康？"
    
    article = chain.run(topic=topic, description=description, problem=problem)
    pprint(article)

def test_initial_agent():
    config = load_config()
    
    test_analysis_agent = InitialAnalysisAgent(config=config["initial_analysis"])
    
    response = test_analysis_agent.analyze(
        topic='睡眠、健康、环境与跑步表现',
        description=('我希望能写作一篇总结影响跑步表现的各种因素的文章，包括但不限于睡眠因素、健康因素、环境因素等等。'
                     '需要全面且详细的总结出各种可能的因素，分门别类且轻重有序。'
                     '对于每一个因素需要给出它的作用机制，即它是如何一步一步影响到人的跑步表现的。'),
        problem='影响跑步表现的因素有哪些？它们是如何影响跑步的？'
    )
    
    pprint(response)
    test_analysis_agent.print_outline(response)
    test_analysis_agent.check_outline_structure(response)
    
if __name__ == "__main__":
    test_initial_agent()
