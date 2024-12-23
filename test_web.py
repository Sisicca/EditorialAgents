import streamlit as st

# 初始化会话状态中的大纲字典
if 'outline_dict' not in st.session_state:
    st.session_state.outline_dict = {
        '1': '章节1标题',
        '1.1': '章节1.1标题',
        '1.2': '章节1.2标题',
        '2': '章节2标题',
        # 可以添加更多章节
    }

def display_outline(outline_dict):
    # 首先按章节序号排序
    sorted_keys = sorted(outline_dict.keys(), key=lambda x: [int(part) for part in x.split('.')])
    section_keys = [k for k in sorted_keys if '.' not in k]
    
    for key in section_keys:
        title = outline_dict[key]
        with st.expander(f"章节 {key}: {title}", expanded=True):
            new_title = st.text_input(f"编辑章节 {key}", value=title, key=f"main_{key}")
            outline_dict[key] = new_title
            # 子章节
            sub_keys = [k for k in sorted_keys if k.startswith(f"{key}.")]
            for sub_key in sub_keys:
                sub_title = outline_dict[sub_key]
                cols = st.columns([0.1, 0.8, 0.1])
                with cols[0]:
                    st.write("")  # 占位
                with cols[1]:
                    new_sub_title = st.text_input(f"章节 {sub_key}", value=sub_title, key=sub_key)
                    outline_dict[sub_key] = new_sub_title
                with cols[2]:
                    if st.button(f"删除 {sub_key}", key=f"del_{sub_key}"):
                        del outline_dict[sub_key]
                        st.rerun()
            # 添加子章节按钮
            if st.button(f"添加子章节到 {key}", key=f"add_{key}"):
                # 生成新的子章节编号
                existing_sub = [k for k in outline_dict.keys() if k.startswith(f"{key}.")]
                if existing_sub:
                    last_sub = sorted(existing_sub, key=lambda x: [int(part) for part in x.split('.')])[-1]
                    next_num = int(last_sub.split('.')[-1]) + 1
                else:
                    next_num = 1
                new_sub_key = f"{key}.{next_num}"
                outline_dict[new_sub_key] = f"章节{new_sub_key}标题"
                st.rerun()

# 页面标题
st.title('可编辑的文章大纲展示')

# 展示和编辑大纲
display_outline(st.session_state.outline_dict)

# 添加主章节按钮
if st.button("添加主章节"):
    existing_main = [k for k in st.session_state.outline_dict.keys() if '.' not in k]
    if existing_main:
        last_main = sorted(existing_main, key=lambda x: int(x))[ -1]
        next_num = int(last_main) + 1
    else:
        next_num = 1
    new_main_key = f"{next_num}"
    st.session_state.outline_dict[new_main_key] = f"章节{new_main_key}标题"
    st.rerun()

# 显示修改后的大纲字典（可选）
st.write('修改后的大纲字典：', st.session_state.outline_dict)
