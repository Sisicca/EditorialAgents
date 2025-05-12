from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import datetime
import uuid

class DocumentPreview(BaseModel):
    id: str
    citation_key: str
    title: Optional[str] = None
    source: str # 'web' or 'kb'
    # content_snippet: Optional[str] = None # Can be added later if needed

class LeafNodeStatusUpdate(BaseModel): # For incoming updates
    status_message: Optional[str] = None
    current_query: Optional[str] = None
    iteration_progress: Optional[str] = None # e.g., "1/3"
    is_completed: Optional[bool] = None
    error_message: Optional[str] = None
    retrieved_docs_preview: Optional[List[DocumentPreview]] = None # 新增: 当前轮次检索到的文档预览
    content_preview: Optional[str] = None # 新增: 当前轮次生成的内容预览

class LeafNodeStatus(BaseModel): # For storing and outgoing status
    node_id: str 
    title: str
    status_message: str = "Pending"
    current_query: Optional[str] = None
    iteration_progress: Optional[str] = None 
    retrieved_docs_preview: List[DocumentPreview] = Field(default_factory=list) # 新增
    content_preview: Optional[str] = None # 新增: 当前内容预览 (可以是最新一次迭代的，或最终的)
    is_completed: bool = False
    error_message: Optional[str] = None
    last_updated: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class RetrievalOverallStatus(BaseModel):
    overall_status_message: str = "Not Started" # e.g., "Initializing", "Retrieval In Progress", "Retrieval Completed", "Error"
    total_leaf_nodes: int = 0
    completed_leaf_nodes: int = 0
    leaf_nodes_status: Dict[str, LeafNodeStatus] = Field(default_factory=dict) # node_id as key
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    error_message: Optional[str] = None # For overall process errors

class ProcessState(BaseModel):
    process_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: Optional[str] = None
    description: Optional[str] = None
    problem: Optional[str] = None
    # Storing the full ArticleOutline object might be heavy if it contains all retrieved docs.
    # Consider storing only the structure or essential parts for status tracking.
    # For now, let's assume we store the dictionary form.
    outline_dict: Optional[Dict[str, Any]] = None 
    # This will store the ArticleOutline object itself after parsing from outline_dict
    # framework: Optional[Any] = None # Type hint with actual ArticleOutline if possible, or Any
    
    retrieval_options: Optional[Dict[str, bool]] = None # e.g., {"use_web": True, "use_kb": False}
    retrieval_status: RetrievalOverallStatus = Field(default_factory=RetrievalOverallStatus)
    
    composition_status: str = "Not Started" # e.g., "In Progress", "Completed", "Error"
    article_content: Optional[str] = None
    
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    last_updated: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True # To allow 'framework' of non-pydantic type if needed

# --- API Request/Response Specific Models ---

class ProcessCreationInput(BaseModel):
    topic: str
    description: Optional[str] = ""
    problem: Optional[str] = ""

class ProcessCreationResponse(BaseModel):
    process_id: str
    topic: str
    initial_outline: Optional[Dict[str, Any]] = None # The outline_dict from ArticleOutline
    message: str

class OutlineUpdateRequest(BaseModel):
    outline_dict: Dict[str, Any]

class OutlineUpdateResponse(BaseModel):
    process_id: str
    message: str

class RetrievalStartRequest(BaseModel):
    use_web: bool = True
    use_kb: bool = True

class RetrievalStartResponse(BaseModel):
    process_id: str
    message: str
    initial_status: RetrievalOverallStatus

class RetrievalStatusResponse(BaseModel):
    process_id: str
    retrieval_status: RetrievalOverallStatus
    
class CompositionStartResponse(BaseModel):
    process_id: str
    message: str

class ArticleResponse(BaseModel):
    process_id: str
    composition_status: str
    article_content: Optional[str] = None
    references_raw: Optional[List[Dict[str, Any]]] = None # For raw references if needed
