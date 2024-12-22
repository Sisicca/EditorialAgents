from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader, CSVLoader, UnstructuredEPubLoader # 读取论文文件
from langchain_text_splitters import RecursiveCharacterTextSplitter # 将读取的文件拆分为chunk
from langchain_community.embeddings import HuggingFaceEmbeddings # 读取huggingface的embedding模型
from langchain_community.vectorstores import FAISS # 把embedding模型的编码结果储存为向量数据库
from langchain_community.cross_encoders import HuggingFaceCrossEncoder # 读取huggingface的cross_embedding模型
from langchain.retrievers.document_compressors import CrossEncoderReranker # 设置reranker模型的重排方法
from langchain.retrievers import ContextualCompressionRetriever # 整合embedding和reranker

# 构造 chatgpt + rag
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

import os
from loguru import logger
from tqdm import tqdm
from pprint import pprint
from typing import Dict

from agents.prompts import PROMPTS

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def _list_files_in_directory(directory_path):
    try:
        # 获取目录中的所有文件和子目录
        files_and_dirs = os.listdir(directory_path)
        # 过滤出文件
        files = [f for f in files_and_dirs if os.path.isfile(os.path.join(directory_path, f))]
        
        return files
    except Exception as e:
        print(f"Error: {e}")
        return []

def _file2docs(file_name, chunk_size, chunk_overlap):
    if file_name.endswith(".docx"):
        Loader = Docx2txtLoader
    elif file_name.endswith(".pdf"):
        Loader = PyPDFLoader
    elif file_name.endswith(".txt"):
        Loader = TextLoader
    elif file_name.endswith(".csv"):
        Loader = CSVLoader
    elif file_name.endswith(".epub"):
        Loader = UnstructuredEPubLoader
    else:
        logger.info("只支持docx,pdf,txt,csv和epub文件。")
        return []
    loader = Loader(file_name)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    texts = text_splitter.split_documents(docs)
    return texts

class LocalKBAgent:
    def __init__(self, config):
        self.kb_path = config['kb_path']
        self.embedding_model = config['embedding_model']
        self.reranker_model = config['reranker_model']
        self.k = config['k']
        self.top_n = config['top_n']
        self.chunk_size = config['chunk_size']
        self.chunk_overlap = config['chunk_overlap']
        
        self.llm = ChatOpenAI(api_key=config['api_key'],
                              base_url=config['base_url'],
                              model=config['model'])
        
        self._create_retriever(
            kb_path=self.kb_path,
            embedding_model=self.embedding_model,
            reranker_model=self.reranker_model,
            k=self.k,
            top_n=self.top_n,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
    
    def _create_retriever(self, kb_path , embedding_model, reranker_model, k, top_n, chunk_size, chunk_overlap):
        paper_list = _list_files_in_directory(kb_path)
        texts_list = []
        for pdf_name in tqdm(paper_list):
            directory_path = f"{kb_path}/{pdf_name}"
            texts = _file2docs(directory_path, chunk_size, chunk_overlap)
            texts_list += texts
        
        embeddingsModel = HuggingFaceEmbeddings(model_name=embedding_model,
                                                model_kwargs = {"device": "mps"},
                                                encode_kwargs={"normalize_embeddings": True})
        retriever = FAISS.from_documents(texts, embeddingsModel).as_retriever(search_type='similarity', search_kwargs={"k": k})
        
        crossEncoderModel = HuggingFaceCrossEncoder(model_name=reranker_model, model_kwargs={"device": "mps"})
        compressor = CrossEncoderReranker(model=crossEncoderModel, top_n=top_n)
        
        self.retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)
    
    def _search(self, hypothetical_doc:Dict[str,str]):
        search_results = []
        
        for query, hy_doc in hypothetical_doc.items():
            real_docs = self.retriever.invoke(hy_doc)
            content = ''
            
            for idx, doc in enumerate(real_docs):
                page_content = doc.page_content
                content += f'LocalKBDocument{idx+1}\n'
                content += page_content
                content += '-'*100 + '\n'
            
            search_results.append(
                {
                    'query': query,
                    'hy_doc': hy_doc,
                    'content': content
                }
            )
        
        return search_results
    
    def response(self, hypothetical_doc:Dict[str,str]):
        search_results = self._search(hypothetical_doc)
        
        local_kb_template = PromptTemplate(
            input_variables=['query', 'content'],
            template=PROMPTS['local_kb_agent']
        )
        
        local_kb_chain = local_kb_template | self.llm | StrOutputParser()
        
        for item in search_results:
            answer = local_kb_chain.invoke(
                {
                    'query': item['query'],
                    'content': item['content']
                }
            )
            item['answer'] = answer
        
        return search_results
        
    

