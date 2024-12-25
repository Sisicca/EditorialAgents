import streamlit as st
import yaml
from agents.initial_analysis_agent import InitialAnalysisAgent

# 初始化会话状态中的大纲字典
if 'outline_dict' not in st.session_state:
    st.session_state.outline_dict = {
    'title': '睡眠、健康、环境与跑步表现',
    'level': 1,
    'summary': '全面探讨影响跑步表现的多种因素，包括睡眠、健康和环境等，并分析其作用机制及对跑步表现的影响。',
    'children': [
        {
            'title': '引言',
            'level': 2,
            'summary': '概述跑步表现的重要性及其受到多种因素影响的复杂性，阐明研究这些因素的意义。',
            'children': []
        },
        {
            'title': '睡眠对跑步表现的影响',
            'level': 2,
            'summary': '分析睡眠质量和睡眠时长如何影响跑步表现及其背后的生理机制。',
            'children': [
                {
                    'title': '睡眠质量与恢复',
                    'level': 3,
                    'summary': '探讨高质量的睡眠如何通过促进肌肉恢复和降低疲劳来提高跑步表现。',
                    'children': []
                },
                {
                    'title': '睡眠不足对身体机能的影响',
                    'level': 3,
                    'summary': '分析睡眠不足如何导致反应时间延迟、耐力下降以及精神专注力降低。',
                    'children': []
                },
                {
                    'title': '昼夜节律与运动表现',
                    'level': 3,
                    'summary': '讨论昼夜节律如何通过调节体温和荷尔蒙分泌影响跑步表现。',
                    'children': []
                }
            ]
        },
        {
            'title': '健康因素对跑步表现的影响',
            'level': 2,
            'summary': '阐述健康状况，包括饮食、免疫力和心理健康等对跑步表现的作用机制。',
            'children': [
                {
                    'title': '营养摄入与能量供给',
                    'level': 3,
                    'summary': '介绍饮食结构如何通过提供能量和维持代谢功能影响跑步表现。',
                    'children': [
                        {
                            'title': '碳水化合物摄入与跑步耐力',
                            'level': 4,
                            'summary': '分析碳水化合物储备如何支持长时间跑步中的能量需求。',
                            'children': []
                        },
                        {
                            'title': '微量营养素在运动中的作用',
                            'level': 4,
                            'summary': '探讨维生素和矿物质如何通过支持代谢和免疫功能影响跑步表现。',
                            'children': []
                        }
                    ]
                },
                {
                    'title': '免疫系统与跑步恢复',
                    'level': 3,
                    'summary': '分析免疫系统强弱如何影响运动后恢复速度和整体表现。',
                    'children': []
                },
                {
                    'title': '心理健康与动机',
                    'level': 3,
                    'summary': '探讨心理健康和跑步动机如何通过情绪调节和压力管理影响表现。',
                    'children': []
                }
            ]
        },
        {
            'title': '环境因素对跑步表现的影响',
            'level': 2,
            'summary': '分析外部环境条件如气温、湿度和海拔对跑步表现的具体影响。',
            'children': [
                {
                    'title': '气温与跑步效率',
                    'level': 3,
                    'summary': '讨论高温或低温环境如何影响体温调节和能量消耗。',
                    'children': []
                },
                {
                    'title': '湿度与脱水风险',
                    'level': 3,
                    'summary': '分析湿度对体液平衡和耐力的影响及导致脱水的风险。',
                    'children': []
                },
                {
                    'title': '海拔高度与氧气供应',
                    'level': 3,
                    'summary': '探讨高海拔环境中氧气稀薄如何影响跑步中的有氧代谢能力。',
                    'children': []
                }
            ]
        },
        {
            'title': '综合因素的相互作用',
            'level': 2,
            'summary': '分析睡眠、健康和环境因素如何相互作用，共同影响跑步表现。',
            'children': [
                {
                    'title': '睡眠与健康的交互影响',
                    'level': 3,
                    'summary': '探讨睡眠不足如何削弱免疫力，并进一步影响跑步恢复。',
                    'children': []
                },
                {
                    'title': '环境与健康的联动效应',
                    'level': 3,
                    'summary': '分析极端环境条件如何加剧身体负担，对健康和表现产生复合影响。',
                    'children': []
                }
            ]
        },
        {
            'title': '改善跑步表现的建议',
            'level': 2,
            'summary': '基于上述分析，提出提高跑步表现的实际策略。',
            'children': [
                {
                    'title': '优化睡眠质量',
                    'level': 3,
                    'summary': '提供改善睡眠的具体建议，如制定规律的作息时间和优化睡眠环境。',
                    'children': []
                },
                {
                    'title': '健康管理与饮食策略',
                    'level': 3,
                    'summary': '建议通过科学饮食和健康管理来提升跑步能力。',
                    'children': []
                },
                {
                    'title': '环境适应训练',
                    'level': 3,
                    'summary': '提出通过适应性训练提高在不同环境条件下的跑步表现。',
                    'children': []
                }
            ]
        },
        {
            'title': '结论',
            'level': 2,
            'summary': '总结睡眠、健康和环境因素对跑步表现的综合影响，并展望未来研究方向。',
            'children': []
        }
    ]
}
    
def display_outline(outline_dict):
    # 提取论文主标题 1级
    # 1级 放入container
    class_1_title, class_1_summary, class_2_list = outline_dict['title'], outline_dict['summary'], outline_dict['children']
    with st.container(border=True):
        outline_dict['title'] = st.text_input('**文章标题**', value=class_1_title, key='0_title')
        outline_dict['summary'] = st.text_input('**文章概述**', value=class_1_summary, key='0_summary')
    
    # 遍历 2级
    # 2级 放入与 1级 并列的expander
    for i, class_2 in enumerate(class_2_list):
        i_class_2_title, i_class_2_summary, i_class_3_list = class_2['title'], class_2['summary'], class_2['children']
        
        with st.expander(f"**{i+1}.**", expanded=False):
            
            cols = st.columns([9, 1])
            
            with cols[0]:
                class_2['title'] = st.text_input('**段落标题**', value=i_class_2_title, key=f'{i+1}_title')
                class_2['summary'] = st.text_input('**段落概述**', value=i_class_2_summary, key=f'{i+1}_summary')
            
            with cols[1]:
                st.write('---')
                
                if st.button(label='🗑️', key=f'删除{i+1}'):
                    delete_class(outline_dict=outline_dict, path=[i])
                    st.rerun()
                    
                if st.button(label='➕', key=f'新增{i+1}子标题'):
                    add_class(outline_dict=outline_dict, path=[i])
                    st.rerun()
        
            # 遍历当前 2级 下的所有 3级
            # 3级 放入当前 2级 的expander
            # 3级 以colunm布局
            for si, i_class_3 in enumerate(i_class_3_list):
                i_si_class_3_title, i_si_class_3_summary, i_si_class_4_list = i_class_3['title'], i_class_3['summary'], i_class_3['children']
                
                st.divider()
                
                subcols = st.columns([0.6, 8.5, 0.9])
                
                with subcols[0]:
                    st.write(f'**{i+1}.{si+1}.**')
                
                with subcols[1]:
                    i_class_3['title'] = st.text_input('**段落标题**', value=i_si_class_3_title, key=f'{i+1}.{si+1}_title')
                    i_class_3['summary'] = st.text_input('**段落概述**', value=i_si_class_3_summary, key=f'{i+1}.{si+1}_summary')
                    
                    # 遍历当前 3级 下的所有 4级
                    # 4级 放入与 3级 并列的container
                    for ssi, i_si_class_4 in enumerate(i_si_class_4_list):
                        i_si_ssi_class_4_title, i_si_ssi_class_4_summary = i_si_class_4['title'], i_si_class_4['summary']
                        
                        with st.container(border=True):
                            subsubcols = st.columns([1, 8, 1])
                            
                            with subsubcols[0]:
                                st.write(f'**{i+1}.{si+1}.{ssi+1}.**')
                            
                            with subsubcols[1]:
                                i_si_class_4['title'] = st.text_input('**段落标题**', value=i_si_ssi_class_4_title, key=f'{i+1}.{si+1}.{ssi+1}_title')
                                i_si_class_4['summary'] = st.text_input('**段落概述**', value=i_si_ssi_class_4_summary, key=f'{i+1}.{si+1}.{ssi+1}_summary')
                                
                            with subsubcols[2]:
                                st.write('---')
                                
                                if st.button(label='🗑️', key=f'删除{i+1}.{si+1}.{ssi+1}'):
                                    delete_class(outline_dict=outline_dict, path=[i, si, ssi])
                                    st.rerun()
                    
                with subcols[2]:
                    st.write('---')
                    
                    if st.button(label='🗑️', key=f'删除{i+1}.{si+1}'):
                        delete_class(outline_dict=outline_dict, path=[i, si])
                        st.rerun()
                    
                    if st.button(label='➕', key=f'新增{i+1}.{si+1}子标题'):
                        add_class(outline_dict=outline_dict, path=[i, si])
                        st.rerun()
                    
    
    if st.button(label='➕', key='新增子标题'):
        add_class(outline_dict=outline_dict, path=[])
        st.rerun()
    
    return

def delete_class(outline_dict, path:list):
    target_section = outline_dict
    
    target_index = path.pop()
    
    for i in path:
        target_section = target_section['children'][i]
    
    target_section['children'].pop(target_index)

def add_class(outline_dict, path:list):
    target_section = outline_dict
    
    for i in path:
        target_section = target_section['children'][i]
    
    target_section['children'].append(
        {
            'title': '段落标题',
            'level': len(path)+2,
            'summary': '段落概述',
            'children': []
        }
    )
    

def load_config(config_path='config/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

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
    st.session_state.outline_dict = response

test_initial_agent()
display_outline(st.session_state.outline_dict)