from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader, CSVLoader, UnstructuredEPubLoader  # 读取论文文件
from langchain_text_splitters import RecursiveCharacterTextSplitter  # 将读取的文件拆分为chunk
from langchain_community.embeddings import HuggingFaceEmbeddings  # 读取huggingface的embedding模型
from langchain_community.vectorstores import FAISS  # 把embedding模型的编码结果储存为向量数据库
from langchain_community.cross_encoders import HuggingFaceCrossEncoder  # 读取huggingface的cross_embedding模型
from langchain.retrievers.document_compressors import CrossEncoderReranker  # 设置reranker模型的重排方法
from langchain.retrievers import ContextualCompressionRetriever  # 整合embedding和reranker
# 构造 chatgpt + rag
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import logging
from tqdm import tqdm
from typing import Dict, List
from agents.prompts import PROMPTS
from agents.initial_analysis_agent import ArticleOutline
from concurrent.futures import ThreadPoolExecutor, as_completed

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _list_files_in_directory(directory_path):
    try:
        files_and_dirs = os.listdir(directory_path)
        files = [f for f in files_and_dirs if os.path.isfile(os.path.join(directory_path, f))]
        return files
    except Exception as e:
        logger.error(f"列出目录文件失败: {e}")
        return []

def _file2docs(file_path, chunk_size, chunk_overlap):
    if file_path.endswith(".docx"):
        Loader = Docx2txtLoader
    elif file_path.endswith(".pdf"):
        Loader = PyPDFLoader
    elif file_path.endswith(".txt"):
        Loader = TextLoader
    elif file_path.endswith(".csv"):
        Loader = CSVLoader
    elif file_path.endswith(".epub"):
        Loader = UnstructuredEPubLoader
    else:
        logger.warning(f"不支持的文件格式: {file_path}")
        return []
    
    try:
        loader = Loader(file_path)
        docs = loader.load()
    except Exception as e:
        logger.error(f"加载文件失败 ({file_path}): {e}")
        return []
    
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        texts = text_splitter.split_documents(docs)
        return texts
    except Exception as e:
        logger.error(f"拆分文档失败 ({file_path}): {e}")
        return []

class LocalKBAgent:
    def __init__(self, config):
        self.kb_path = config['kb_path']
        self.embedding_model = config['embedding_model']
        self.reranker_model = config['reranker_model']
        self.k = config['k']
        self.top_n = config['top_n']
        self.chunk_size = config['chunk_size']
        self.chunk_overlap = config['chunk_overlap']
        self.device = config['device']
        # 设置最大线程数，可以根据实际情况调整
        self.max_workers = config['max_workers']
        
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
    
    def _create_retriever(self, kb_path, embedding_model, reranker_model, k, top_n, chunk_size, chunk_overlap):
        paper_list = _list_files_in_directory(kb_path)
        texts_list = []
        logger.info(f"开始加载和拆分文档，共计 {len(paper_list)} 个文件。")
        
        for pdf_name in tqdm(paper_list, desc="加载和拆分文档"):
            file_path = os.path.join(kb_path, pdf_name)
            texts = _file2docs(file_path, chunk_size, chunk_overlap)
            texts_list.extend(texts)
        
        if not texts_list:
            logger.warning("没有加载到任何文本片段。")
        
        logger.info('正在构建混合检索器...')
        try:
            embeddingsModel = HuggingFaceEmbeddings(model_name=embedding_model,
                                                    model_kwargs={"device": self.device},
                                                    encode_kwargs={"normalize_embeddings": True})
            retriever = FAISS.from_documents(texts_list, embeddingsModel).as_retriever(search_type='similarity', search_kwargs={"k": k})
            
            crossEncoderModel = HuggingFaceCrossEncoder(model_name=reranker_model, model_kwargs={"device": self.device})
            compressor = CrossEncoderReranker(model=crossEncoderModel, top_n=top_n)
            
            self.retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)
            logger.info('混合检索器构建完毕')
        except Exception as e:
            logger.error(f"构建混合检索器失败: {e}")
            self.retriever = None
    
    def _generate_hypothetical_doc(self, title: str, summary: str) -> str:
        try:
            hypothetical_template = PromptTemplate(
                input_variables=['title', 'summary'],
                template=PROMPTS['hypothetical_doc']
            )
            
            hypothetical_chain = hypothetical_template | self.llm | StrOutputParser()
            
            hypothetical_doc = hypothetical_chain.invoke(
                {
                    'title': title,
                    'summary': summary
                }
            )
            
            return hypothetical_doc
        except Exception as e:
            logger.error(f"生成假设性文档失败 (标题: {title}): {e}")
            return ""
    
    def _search_docs(self, hypothetical_doc: str) -> List[str]:        
        try:
            kb_docs = self.retriever.invoke(hypothetical_doc)
            return [doc.page_content for doc in kb_docs]
        except Exception as e:
            logger.error(f"检索文档失败: {e}")
            return []
        
    def _refine_doc(self, doc: str, title: str, summary: str) -> str:
        try:
            refine_template = PromptTemplate(
                input_variables=['title', 'summary', 'document'],
                template=PROMPTS['refine_doc']
            )
            
            refine_chain = refine_template | self.llm | StrOutputParser()
            
            refine_result = refine_chain.invoke(
                {
                    'title': title,
                    'summary': summary,
                    'document': doc
                }
            )
            return refine_result
        except Exception as e:
            logger.error(f"精炼文档失败 (标题: {title}): {e}")
            return ""
    
    def search_for_leaf_nodes(self, framework: ArticleOutline) -> ArticleOutline:
        leaf_nodes = framework.find_leaf_nodes()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 1. 并发生成假设性文档
            logger.info("开始生成假设性文档...")
            hypothetical_futures = {
                executor.submit(self._generate_hypothetical_doc, node['title'], node['summary']): node
                for node in leaf_nodes
            }
            
            with tqdm(total=len(hypothetical_futures), desc="为叶子节点生成假设性文档") as pbar:
                for future in as_completed(hypothetical_futures):
                    node = hypothetical_futures[future]
                    try:
                        node['hypothetical_doc'] = future.result()
                        if not node['hypothetical_doc']:
                            logger.warning(f"假设性文档为空 (标题: {node['title']})")
                    except Exception as e:
                        logger.error(f"生成假设性文档失败 (标题: {node['title']}): {e}")
                        node['hypothetical_doc'] = ""
                    
                    pbar.update(1)
            
            # 2. 顺序检索本地知识库
            logger.info("开始顺序检索本地知识库...")
            for node in tqdm(leaf_nodes, desc="检索本地知识库"):
                try:
                    node['kb_docs'] = self._search_docs(hypothetical_doc=node.get('hypothetical_doc', ""))
                    if not node['kb_docs']:
                        logger.warning(f"未检索到相关文档 (标题: {node['title']})")
                except Exception as e:
                    logger.error(f"检索本地知识库失败 (标题: {node['title']}): {e}")
                    node['kb_docs'] = []
            
            # 3. 并发精炼文档
            logger.info("开始精炼文档...")
            refine_futures = {
                executor.submit(self._refine_doc, doc, node['title'], node['summary']): (node, doc)
                for node in leaf_nodes
                for doc in node.get('kb_docs', [])
            }
            
            # 初始化 web_docs_refined
            for node in leaf_nodes:
                node['kb_docs_refined'] = []
            
            with tqdm(total=len(refine_futures), desc="对知识库文档进行精炼") as pbar:
                for future in as_completed(refine_futures):
                    node, doc = refine_futures[future]
                    try:
                        refined_doc = future.result()
                        if refined_doc:
                            node['kb_docs_refined'].append(refined_doc)
                    except Exception as e:
                        logger.error(f"精炼节点 '{node['title']}' 的文档失败: {e}")
                    
                    pbar.update(1)
        
        return framework
