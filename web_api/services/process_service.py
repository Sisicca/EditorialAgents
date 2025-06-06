from fastapi import HTTPException, BackgroundTasks
from typing import Dict, Any, List, Tuple, Optional

from ..models_api import (
    ProcessCreationInput, ProcessCreationResponse, 
    OutlineUpdateRequest, OutlineUpdateResponse,
    RetrievalStartRequest, RetrievalStartResponse,
    RetrievalStatusResponse, CompositionStartResponse, ArticleResponse,
    LeafNodeStatusUpdate # For direct use in agent if type hinting is strict
)
from .status_manager import ProcessStatusManager
from ..core_integrator import AgentIntegrator
from agents.initial_analysis_agent import ArticleOutline # For type hinting

class ProcessService:
    def __init__(self, status_manager: ProcessStatusManager, agent_integrator: AgentIntegrator):
        self.status_manager = status_manager
        self.agent_integrator = agent_integrator

    async def create_new_process(self, creation_input: ProcessCreationInput) -> ProcessCreationResponse:
        process_state = self.status_manager.create_process(
            topic=creation_input.topic,
            description=creation_input.description,
            problem=creation_input.problem
        )
        try:
            # This is a synchronous call from the agent, potentially long.
            # For a production app, InitialAnalysisAgent might also need to be async or run in a thread.
            article_outline_obj: ArticleOutline = self.agent_integrator.generate_initial_outline(
                topic=process_state.topic,
                description=process_state.description,
                problem=process_state.problem
            )
            self.status_manager.update_outline(process_state.process_id, article_outline_obj.outline)
            return ProcessCreationResponse(
                process_id=process_state.process_id,
                topic=process_state.topic,
                initial_outline=article_outline_obj.outline,
                message="Process created and initial outline generated."
            )
        except Exception as e:
            self.status_manager.update_overall_retrieval_message(process_state.process_id, "Error during outline generation", error=str(e))
            raise HTTPException(status_code=500, detail=f"Error generating outline: {str(e)}")

    async def update_process_outline(self, process_id: str, update_request: OutlineUpdateRequest) -> OutlineUpdateResponse:
        process_state = self.status_manager.get_process_state(process_id)
        if not process_state:
            raise HTTPException(status_code=404, detail="Process not found")
        
        self.status_manager.update_outline(process_id, update_request.outline_dict)
        return OutlineUpdateResponse(process_id=process_id, message="Outline updated successfully.")

    def _extract_leaf_nodes_info(self, outline_dict: Dict[str, Any]) -> List[Tuple[str, str]]:
        """ Helper to get (node_id, title) for all leaf nodes from an outline dictionary, excluding intro/conclusion """
        leaf_nodes_info = []
        # Create a temporary ArticleOutline object to use its methods
        # This assumes ArticleOutline can be instantiated with just the dict for this purpose
        temp_outline_obj = ArticleOutline(outline_dict) 
        
        leaf_nodes = temp_outline_obj.find_leaf_nodes()
        
        # Get intro_conclusion_agent to use its skip function
        intro_conclusion_agent = self.agent_integrator.get_intro_conclusion_agent()
        
        # We need a consistent way to get a unique ID for each node that matches 
        # what UnifiedRetrievalAgent._get_node_display_id will produce.
        # For now, we simulate that ID generation here.
        # It's better if ArticleOutline itself provides a unique path/ID for each node.
        # Or if _get_node_display_id is a static/utility method callable from here.
        
        # Placeholder for UnifiedRetrievalAgent's ID logic - this needs to match!
        def get_temp_node_display_id(node: Dict[str, Any]) -> str:
             return f"level{node.get('level', 'N')}-{node.get('title', 'Untitled').replace(' ', '_')[:30]}"

        for node_dict in leaf_nodes:
            # 跳过引言和结论节点
            if intro_conclusion_agent.should_skip_retrieval(node_dict):
                continue
                
            node_id = get_temp_node_display_id(node_dict) # Must match agent's internal ID
            title = node_dict.get('title', 'Unknown Leaf')
            leaf_nodes_info.append((node_id, title))
        return leaf_nodes_info

    async def start_iterative_retrieval(self, process_id: str, retrieval_request: RetrievalStartRequest, background_tasks: BackgroundTasks) -> RetrievalStartResponse:
        process_state = self.status_manager.get_process_state(process_id)
        if not process_state:
            raise HTTPException(status_code=404, detail="Process not found")
        if not process_state.outline_dict:
            raise HTTPException(status_code=400, detail="Outline not set for this process")

        leaf_nodes_info = self._extract_leaf_nodes_info(process_state.outline_dict)
        if not leaf_nodes_info:
            raise HTTPException(status_code=400, detail="No leaf nodes found in the outline to process.")

        retrieval_options = {"use_web": retrieval_request.use_web, "use_kb": retrieval_request.use_kb}
        initial_status = self.status_manager.init_retrieval_status(process_id, leaf_nodes_info, retrieval_options)
        
        # Re-create the ArticleOutline object from the stored dict for the agent
        # This ensures the agent gets a proper object, not just a dict.
        framework_obj = ArticleOutline(process_state.outline_dict)

        # Get a fresh agent instance
        retrieval_agent = self.agent_integrator.get_unified_retrieval_agent()
        intro_conclusion_agent = self.agent_integrator.get_intro_conclusion_agent()
        
        background_tasks.add_task(
            retrieval_agent.iterative_retrieval_for_leaf_nodes,
            framework_obj, 
            process_id, 
            self.status_manager, # Pass the singleton instance
            retrieval_request.use_web,
            retrieval_request.use_kb,
            intro_conclusion_agent.should_skip_retrieval  # 跳过引言和结论部分的检索
        )
        
        return RetrievalStartResponse(
            process_id=process_id, 
            message="Iterative retrieval process started in background.",
            initial_status=initial_status
        )

    async def get_retrieval_status_for_process(self, process_id: str) -> RetrievalStatusResponse:
        process_state = self.status_manager.get_process_state(process_id)
        if not process_state:
            raise HTTPException(status_code=404, detail="Process not found")
        return RetrievalStatusResponse(process_id=process_id, retrieval_status=process_state.retrieval_status)

    async def start_article_composition(self, process_id: str, background_tasks: BackgroundTasks) -> CompositionStartResponse:
        process_state = self.status_manager.get_process_state(process_id)
        if not process_state or not process_state.outline_dict:
            raise HTTPException(status_code=404, detail="Process or outline not found")
        if process_state.retrieval_status.overall_status_message not in ["Retrieval Completed", "Retrieval Completed with Errors"]:
             # Allow composition even if retrieval has errors, but not if it's not started/in progress
            if process_state.retrieval_status.overall_status_message in ["Not Started", "Retrieval Initialized", "Retrieval In Progress"]:
                raise HTTPException(status_code=400, detail="Retrieval is not yet completed for this process.")

        self.status_manager.update_composition_status(process_id, "Composition In Progress")
        
        # The framework object should have its node['content'] populated by UnifiedRetrievalAgent
        # And node['references'] as well.
        # ComprehensiveAnswerAgent works on this framework object.
        framework_obj = ArticleOutline(process_state.outline_dict) # This should be the one modified by retrieval

        comp_agent = self.agent_integrator.get_comprehensive_answer_agent()
        intro_conclusion_agent = self.agent_integrator.get_intro_conclusion_agent()
        
        # The compose method in the agent is synchronous
        def composition_task():
            try:
                # 更新状态：开始生成主体内容
                self.status_manager.update_composition_status(process_id, "正在生成主体内容...")
                
                # ScienceArticleChain has the logic for _compile_references
                # We need to replicate or call that here if not using the full chain.
                # For now, let's assume comp_agent.compose populates framework_obj.outline['content'] for the main article
                comp_agent.compose(framework_obj, skip_function=intro_conclusion_agent.should_skip_retrieval) # Modifies framework_obj in place
                
                # 更新状态：开始生成引言和结论
                self.status_manager.update_composition_status(process_id, "正在生成引言和结论...")
                
                # 生成引言和结论
                intro_conclusion_agent.generate_introduction_and_conclusion(
                    framework=framework_obj,
                    topic=process_state.topic,
                    description=process_state.description
                )
                
                # 更新状态：正在整理文章格式
                self.status_manager.update_composition_status(process_id, "正在整理文章格式...")
                
                final_article_content = framework_obj.outline.get('content', "Error: Main content not generated.")
                
                # Simulate _compile_references from ScienceArticleChain
                # This ideally should be a utility or part of ArticleOutline or a separate service
                all_refs_data = [] 
                for node in framework_obj.find_all_nodes():
                    if 'references' in node and isinstance(node['references'], list):
                        for ref in node['references']:
                             all_refs_data.append(ref) # Store raw ref dicts
                
                # Simplified reference formatting for now:
                formatted_refs_text = "\n\n## References\n\n"
                if all_refs_data:
                    unique_refs = {ref['key']: ref for ref in all_refs_data}.values()
                    for i, ref_item in enumerate(sorted(list(unique_refs), key=lambda x: x['key'])):
                        if ref_item.get('source') == 'web':
                            formatted_refs_text += f"[{ref_item.get('key')}] {ref_item.get('title', 'N/A')}. URL: {ref_item.get('url', 'N/A')}\n"
                        else:
                            formatted_refs_text += f"[{ref_item.get('key')}] {ref_item.get('title', 'N/A')}. (KB: {ref_item.get('file','N/A')}, Page: {ref_item.get('page','N/A')})\n"
                else:
                    formatted_refs_text = "\n\n (No references available)"

                final_article_content += formatted_refs_text

                self.status_manager.update_composition_status(process_id, "Completed", article_content=final_article_content)
            except Exception as e:
                self.status_manager.update_composition_status(process_id, "Error", article_content=f"Error during composition: {str(e)}")
        
        background_tasks.add_task(composition_task)
        return CompositionStartResponse(process_id=process_id, message="Article composition started in background.")

    async def get_composed_article(self, process_id: str) -> ArticleResponse:
        process_state = self.status_manager.get_process_state(process_id)
        if not process_state:
            raise HTTPException(status_code=404, detail="Process not found")
        
        # Extract raw references for potential separate display or structured use by frontend
        raw_references = []
        if process_state.outline_dict:
            temp_framework = ArticleOutline(process_state.outline_dict)
            for node in temp_framework.find_all_nodes():
                if 'references' in node and isinstance(node['references'], list):
                    raw_references.extend(node['references'])
            # Deduplicate raw references by key for the response if needed
            # raw_references = list({ref['key']: ref for ref in raw_references}.values()) 

        return ArticleResponse(
            process_id=process_id, 
            composition_status=process_state.composition_status,
            article_content=process_state.article_content,
            references_raw=list({ref['key']: ref for ref in raw_references}.values()) if raw_references else None
        )
