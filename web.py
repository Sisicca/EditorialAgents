import streamlit as st
import pandas as pd
import os
import yaml
from agents.initial_analysis_agent import InitialAnalysisAgent
from typing import List
from copy import deepcopy
from agents.initial_analysis_agent import ArticleOutline, InitialAnalysisAgent
from agents.web_search_agent import WebSearchAgent
from agents.local_kb_agent import LocalKBAgent
from agents.comprehensive_answer_agent import ComprehensiveAnswerAgent

def display_outline_editable(outline_dict):
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

def display_outline_static(outline_dict):
    # 提取论文主标题 1级
    class_1_title, class_1_summary, class_2_list = outline_dict['title'], outline_dict['summary'], outline_dict['children']
    
    with st.container():
        st.markdown(f"## {class_1_title}")
        st.write(class_1_summary)
    
    # 遍历 2级
    for i, class_2 in enumerate(class_2_list):
        i_class_2_title, i_class_2_summary, i_class_3_list = class_2['title'], class_2['summary'], class_2['children']
        
        docs_list = []
        
        docs_list.append(class_2.get('web_docs_refined', []))
        docs_list.append(class_2.get('kb_docs_refined', []))
        
        with st.expander(f"**{i+1}. {i_class_2_title}**", expanded=False):
            st.markdown(f"**概述:** {i_class_2_summary}")
            
            # 遍历当前 2级 下的所有 3级
            for si, i_class_3 in enumerate(i_class_3_list):
                i_si_class_3_title, i_si_class_3_summary, i_si_class_4_list = i_class_3['title'], i_class_3['summary'], i_class_3['children']
                
                docs_list.append(i_class_3.get('web_docs_refined', []))
                docs_list.append(i_class_3.get('kb_docs_refined', []))
                
                st.markdown(f"### {i+1}.{si+1} {i_si_class_3_title}")
                st.markdown(f"**概述:** {i_si_class_3_summary}")
                
                # 遍历当前 3级 下的所有 4级
                for ssi, i_si_class_4 in enumerate(i_si_class_4_list):
                    i_si_ssi_class_4_title, i_si_ssi_class_4_summary = i_si_class_4['title'], i_si_class_4['summary']
                    
                    docs_list.append(i_si_class_4.get('web_docs_refined', []))
                    docs_list.append(i_si_class_4.get('kb_docs_refined', []))
                        
                    st.markdown(f"#### {i+1}.{si+1}.{ssi+1} {i_si_ssi_class_4_title}")
                    st.markdown(f"**概述:** {i_si_ssi_class_4_summary}")
    
            delete_docs_ij = display_documents(docs_list=docs_list, label=f"{i+1}.相关文档")
            delete_documents(docs_list=docs_list, delete_docs_ij=delete_docs_ij)
        
    return

def display_documents(docs_list:List[List[str]], label:str):
    with st.popover(label):
        delete_doc_ij = []
        save_doc = True
        for i, docs in enumerate(docs_list):
            for j, doc in enumerate(docs):
                cols = st.columns([8, 2])
                with cols[0]:
                    st.text(doc[:200])
                with cols[1]:
                    save_doc = st.checkbox("使用文档", key=f"{i}{j}{doc}", value=True)
                if not save_doc:
                    delete_doc_ij.append((i, j))
        return delete_doc_ij

def delete_documents(docs_list, delete_docs_ij):
    for i, j in delete_docs_ij:
        docs_list[i][j] = "No Document Here"

def load_config(config_path='config/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def folder_selector(folder_path='knowledge_base'):
    folder_paths = []
    for dirpath, _, _ in os.walk(folder_path):
        folder_paths.append(dirpath)
    selected_foldername = st.selectbox('选择知识库', folder_paths)
    pdf_list = os.listdir(selected_foldername)
    pdf_list = [f for f in pdf_list if f.endswith(".pdf")]
    df = pd.DataFrame(pdf_list, columns=["文章列表"])
    st.dataframe(df, width=1000)
    return selected_foldername

def main():
    # 初始化会话状态
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'outline_dict' not in st.session_state:
        st.session_state.outline_dict = ""
    if 'article' not in st.session_state:
        st.session_state.article = ""

    st.title("_Editorial_ :blue[Agents] :memo:")

    config = load_config()

    if st.session_state.step == 1:
        st.header("第一步：输入文章信息")

        # 创建三列用于并排输入
        col1, col2, col3 = st.columns(3)

        with col1:
            topic = st.text_input("文章主题", "")
        with col2:
            description = st.text_area("具体描述", "")
        with col3:
            problem = st.text_area("想要解决的问题", "")

        if st.button("生成文章大纲"):
            if not topic:
                st.error("请填写文章主题。")
            else:
                with st.spinner("生成文章大纲中..."):
                    st.session_state.initial_agent = InitialAnalysisAgent(config=config['initial_analysis'])
                    st.session_state.outline_dict = st.session_state.initial_agent.get_framework(topic=topic, description=description, problem=problem)
                    st.session_state.step = 2
                    st.rerun()

    elif st.session_state.step == 2:
        st.header("第二步：修改文章大纲")

        st.subheader("文章大纲")
        # 使用文本区域显示并允许用户修改大纲
        display_outline_editable(st.session_state.outline_dict.outline)
        
        st.subheader("本地知识库")
        use_kb = st.toggle("启用本地知识库搜索相关文章辅助写作")
        if use_kb:
            foldername = folder_selector()
        
        st.subheader("联网搜索")
        use_web = st.toggle("启用联网搜索相关文章辅助写作")

        if not use_kb and not use_web:
            if st.button("确认大纲并直接生成文章"):
                with st.spinner("生成文章中..."):
                    st.session_state.compose_agent = ComprehensiveAnswerAgent(config=config['comprehensive_answer'])
                    st.session_state.compse_agent.compose(st.session_state.outline_dict)
                    st.session_state.step = 4
                    st.rerun()
        else:
            if st.button("确认大纲并开始检索相关文档"):
                with st.spinner("检索文档中..."):
                    if use_web:
                        st.session_state.web_agent = WebSearchAgent(config=config['web_search'])
                        st.session_state.web_agent.search_for_leaf_nodes(st.session_state.outline_dict)
                    if use_kb:
                        config['local_kb']['kb_path'] = foldername
                        st.session_state.kb_agent = LocalKBAgent(config=config['local_kb'])
                        st.session_state.kb_agent.search_for_leaf_nodes(st.session_state.outline_dict)
                    st.session_state.step = 3
                    st.rerun()

    elif st.session_state.step == 3:
        st.header("第三步：完成检索")
        temp_outline = deepcopy(st.session_state.outline_dict.outline)
        display_outline_static(temp_outline)
        
        if st.button("确认文档并开始生成文章"):
            with st.spinner("生成文章中..."):
                st.session_state.compose_agent = ComprehensiveAnswerAgent(config=config['comprehensive_answer'])
                st.session_state.outline_dict = ArticleOutline(temp_outline)
                st.session_state.compose_agent.compose(st.session_state.outline_dict)
                st.session_state.step = 4
                st.rerun()

    elif st.session_state.step == 4:
        st.header("第四步：生成完成")

        st.subheader("生成的文章")
        article = st.session_state.outline_dict.outline.get('content')
        article_name = st.session_state.outline_dict.outline.get('title')
        st.markdown(article)
        st.download_button("下载文章", article, file_name=f"{article_name}.txt")

        # 提供重新开始的选项
        if st.button("重新开始"):
            st.session_state.step = 1
            st.session_state.outline = ""
            st.session_state.article = ""
            st.rerun()

if __name__ == "__main__":
    main()