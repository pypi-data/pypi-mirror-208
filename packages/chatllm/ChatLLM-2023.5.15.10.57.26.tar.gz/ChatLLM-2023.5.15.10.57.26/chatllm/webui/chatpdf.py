#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : chatpdf
# @Time         : 2023/4/25 17:01
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

import streamlit as st
from meutils.pipe import *
from meutils.serving.st_utils import display_pdf, st_chat, set_config

from chatllm.applications.chatpdf import ChatPDF

st.set_page_config(page_title='🔥ChatPDF', layout='wide', initial_sidebar_state='collapsed')


################################################################################################################
class Conf(BaseConfig):
    encode_model = 'nghuyong/ernie-3.0-nano-zh'
    llm = "THUDM/chatglm-6b"  # /Users/betterme/PycharmProjects/AI/CHAT_MODEL/chatglm
    cachedir = 'pdf_cache'

    topk: int = 3
    threshold: float = 0.66


conf = Conf()
conf = set_config(conf)


# st.json(conf.dict())


################################################################################################################


@st.cache_resource()
def qa4pdf(encode_model, model_name_or_path):
    qa = ChatPDF(encode_model=encode_model)
    qa.load_llm4chat(model_name_or_path=model_name_or_path)
    return qa


################################################################################################################

tabs = st.tabs(['ChatPDF', 'PDF文件预览'])

file = st.sidebar.file_uploader("上传PDF", type=['pdf'])
bytes_array = ''
if file:
    bytes_array = file.read()
    base64_pdf = base64.b64encode(bytes_array).decode('utf-8')

    with tabs[1]:
        if bytes_array:
            display_pdf(base64_pdf)
        else:
            st.warning('### 请先上传PDF')
################################################################################################################
try:
    qa = qa4pdf(conf.encode_model, conf.llm)
    with st.spinner("构建知识库：文本向量化"):
        disk_cache(location=conf.cachedir)(qa.create_index)(bytes_array)
except Exception as e:
    st.warning('启动前选择正确的参数进行初始化')
    st.error(e)


################################################################################################################
def reply_func(query):
    for response, _ in qa(query=query, topk=conf.topk, threshold=conf.threshold):
        yield response


with tabs[0]:
    if file:
        container = st.container()  # 占位符
        text = st.text_area(label="用户输入", height=100, placeholder="请在这儿输入您的问题")

        if st.button("发送", key="predict"):
            with st.spinner("🤔 AI 正在思考，请稍等..."):
                history = st.session_state.get('state')
                st.session_state["state"] = st_chat(
                    text, history, container=container,
                    previous_messages=['请上传需要分析的PDF，我将为你解答'],
                    reply_func=reply_func,
                )

        with st.expander('点击可查看被召回的知识'):
            st.dataframe(qa.recall)
