from typing import Dict, Optional, List, Tuple, Any
from threading import Lock
import datetime

from ..models_api import ProcessState, LeafNodeStatus, RetrievalOverallStatus, LeafNodeStatusUpdate

class ProcessStatusManager:
    _instance = None
    _lock = Lock() # For thread-safe singleton instantiation and dictionary access

    # Making it a singleton so it can be easily accessed across the FastAPI app
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ProcessStatusManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Ensure __init__ is only called once for the singleton
        if not hasattr(self, '_initialized'): 
            self._processes: Dict[str, ProcessState] = {}
            self._initialized = True

    def create_process(self, topic: str, description: Optional[str], problem: Optional[str]) -> ProcessState:
        with self._lock:
            new_process = ProcessState(topic=topic, description=description, problem=problem)
            self._processes[new_process.process_id] = new_process
            return new_process

    def get_process_state(self, process_id: str) -> Optional[ProcessState]:
        with self._lock:
            return self._processes.get(process_id)

    def update_outline(self, process_id: str, outline_dict: Dict[str, Any]) -> Optional[ProcessState]:
        with self._lock:
            process = self._processes.get(process_id)
            if process:
                process.outline_dict = outline_dict
                process.last_updated = datetime.datetime.utcnow()
                # Potentially reset retrieval status if outline changes significantly after retrieval started
                # For now, simple update.
                return process
            return None

    def init_retrieval_status(self, process_id: str, leaf_nodes_info: List[Tuple[str, str]], retrieval_options: Dict[str, bool]) -> Optional[RetrievalOverallStatus]:
        """
        Initializes or resets the retrieval status for a process and its leaf nodes.
        leaf_nodes_info: A list of tuples, where each tuple is (node_id, node_title).
        """
        with self._lock:
            process = self._processes.get(process_id)
            if not process:
                return None

            process.retrieval_options = retrieval_options
            process.retrieval_status = RetrievalOverallStatus(
                overall_status_message="Retrieval Initialized",
                total_leaf_nodes=len(leaf_nodes_info),
                completed_leaf_nodes=0,
                start_time=datetime.datetime.utcnow(),
                leaf_nodes_status={}
            )
            for node_id, node_title in leaf_nodes_info:
                process.retrieval_status.leaf_nodes_status[node_id] = LeafNodeStatus(node_id=node_id, title=node_title)
            
            process.last_updated = datetime.datetime.utcnow()
            return process.retrieval_status

    def update_leaf_node_status(self, process_id: str, node_id: str, update_data: LeafNodeStatusUpdate) -> Optional[LeafNodeStatus]:
        with self._lock:
            process = self._processes.get(process_id)
            if not process or node_id not in process.retrieval_status.leaf_nodes_status:
                return None

            node_status = process.retrieval_status.leaf_nodes_status[node_id]
            
            if update_data.status_message is not None:
                node_status.status_message = update_data.status_message
            if update_data.current_query is not None:
                node_status.current_query = update_data.current_query
            if update_data.iteration_progress is not None:
                node_status.iteration_progress = update_data.iteration_progress
            if update_data.is_completed is not None:
                node_status.is_completed = update_data.is_completed
                if update_data.is_completed and not node_status.error_message:
                    process.retrieval_status.completed_leaf_nodes = sum(
                        1 for nid, ns in process.retrieval_status.leaf_nodes_status.items() if ns.is_completed and not ns.error_message
                    )
                    node_status.status_message = "Completed"
            
            # 新增：处理retrieved_docs_preview 和 content_preview
            if update_data.retrieved_docs_preview is not None:
                node_status.retrieved_docs_preview = update_data.retrieved_docs_preview
            if update_data.content_preview is not None:
                node_status.content_preview = update_data.content_preview

            if update_data.error_message is not None:
                node_status.error_message = update_data.error_message
                node_status.is_completed = True # Mark as completed to stop further processing if error occurs
                # Optionally, update overall status to reflect node error
                # process.retrieval_status.overall_status_message = "Error in node processing"

            node_status.last_updated = datetime.datetime.utcnow()
            process.last_updated = datetime.datetime.utcnow()

            # Check if all nodes are completed to update overall status
            if process.retrieval_status.completed_leaf_nodes == process.retrieval_status.total_leaf_nodes and process.retrieval_status.total_leaf_nodes > 0:
                if not any(ns.error_message for ns in process.retrieval_status.leaf_nodes_status.values()):
                    process.retrieval_status.overall_status_message = "Retrieval Completed"
                else:
                    process.retrieval_status.overall_status_message = "Retrieval Completed with Errors"
                process.retrieval_status.end_time = datetime.datetime.utcnow()
            elif process.retrieval_status.total_leaf_nodes > 0 : # If not all completed but some are active
                 process.retrieval_status.overall_status_message = "Retrieval In Progress"

            return node_status

    def update_overall_retrieval_message(self, process_id: str, message: str, error: Optional[str] = None) -> Optional[RetrievalOverallStatus]:
        with self._lock:
            process = self._processes.get(process_id)
            if not process:
                return None
            process.retrieval_status.overall_status_message = message
            if error:
                process.retrieval_status.error_message = error
                process.retrieval_status.end_time = datetime.datetime.utcnow()
            process.last_updated = datetime.datetime.utcnow()
            return process.retrieval_status

    def update_composition_status(self, process_id: str, status: str, article_content: Optional[str] = None) -> Optional[ProcessState]:
        with self._lock:
            process = self._processes.get(process_id)
            if process:
                process.composition_status = status
                if article_content is not None:
                    process.article_content = article_content
                if status == "Completed" or status == "Error":
                    # Optionally set an end time for composition
                    pass
                process.last_updated = datetime.datetime.utcnow()
                return process
            return None

# Global instance of the manager
status_manager_instance = ProcessStatusManager()
